from abc import ABC, abstractmethod
from logging import Logger
from pyspark.sql import DataFrame
from typing import Any, Callable, Optional, Type, TypeVar
from tenacity import (
    RetryCallState,
    RetryError,
)

from pyeqx.core import Configuration, Operation
from pyeqx.core.models import AppData
from pyeqx.core.models.module import DataModule
from pyeqx.core.retry import retry_and_wait
from pyeqx.execution import ExecuteParameters

TExecuteParameters = TypeVar("TExecuteParameters", bound=ExecuteParameters)


class ProcessBase(ABC):
    LOG_PREFIX_READ = "read source"
    LOG_PREFIX_WRITE = "write destination"

    def __init__(self, config: Configuration, logger: Logger, operation: Operation):
        self.config = config
        self.logger = logger
        self.operation = operation

    def __call__(
        self,
        parameters: TExecuteParameters,
        *args,
        **kwargs,
    ) -> Any:
        return self.execute(
            parameters=parameters,
            *args,
            **kwargs,
        )

    def execute(
        self,
        parameters: TExecuteParameters,
        *args,
        **kwargs,
    ):
        try:
            self._do_execute(
                parameters=parameters,
                *args,
                **kwargs,
            )
        except Exception as e:
            self.logger.error(e, exc_info=True)
            raise e

    def _read_source_retry(
        self,
        data_module: DataModule,
        max_attempts: int = 3,
        wait_in_seconds: int = 5,
        on_retry: Optional[Callable[[int, RetryCallState], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_last_error: Optional[Callable[[int, RetryError], None]] = None,
        *args,
        **kwargs,
    ):
        return retry_and_wait(
            max_attempts=max_attempts,
            wait_in_seconds=wait_in_seconds,
            fn=self._do_read_source,
            on_retry=lambda attempt, retry_state: self._on_retry(
                prefix=self.LOG_PREFIX_READ,
                max_attempts=max_attempts,
                wait_in_seconds=wait_in_seconds,
                attempt=attempt,
                retry_state=retry_state,
                callback=on_retry,
            ),
            on_error=lambda error: self._on_retry_error(
                prefix=self.LOG_PREFIX_READ,
                error=error,
                callback=on_error,
            ),
            on_last_error=lambda attempt, error: self._on_retry_last_error(
                prefix=self.LOG_PREFIX_READ,
                attempt=attempt,
                error=error,
                callback=on_last_error,
            ),
            data_module=data_module,
            *args,
            **kwargs,
        )

    def _write_destination_retry(
        self,
        data: DataFrame,
        data_module: DataModule,
        max_attempts: int = 3,
        wait_in_seconds: int = 5,
        on_retry: Optional[Callable[[int, RetryCallState], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_last_error: Optional[Callable[[int, RetryError], None]] = None,
        *args,
        **kwargs,
    ):
        retry_and_wait(
            max_attempts=max_attempts,
            wait_in_seconds=wait_in_seconds,
            fn=self._do_write_destination,
            on_retry=lambda attempt, retry_state: self._on_retry(
                prefix=self.LOG_PREFIX_WRITE,
                max_attempts=max_attempts,
                wait_in_seconds=wait_in_seconds,
                attempt=attempt,
                retry_state=retry_state,
                callback=on_retry,
            ),
            on_error=lambda error: self._on_retry_error(
                prefix=self.LOG_PREFIX_WRITE,
                error=error,
                callback=on_error,
            ),
            on_last_error=lambda attempt, error: self._on_retry_last_error(
                prefix=self.LOG_PREFIX_WRITE,
                attempt=attempt,
                error=error,
                callback=on_last_error,
            ),
            data=data,
            data_module=data_module,
            *args,
            **kwargs,
        )

    @abstractmethod
    def _do_execute(
        self,
        parameters: TExecuteParameters,
        *args,
        **kwargs,
    ):
        pass

    def _do_read_source(self, data_module: DataModule, *args, **kwargs) -> DataFrame:
        return self.operation.read_source(data_module=data_module, *args, **kwargs)

    def _do_write_destination(
        self, data: DataFrame, data_module: DataModule, *args, **kwargs
    ):
        self.operation.write_destination(
            data=data, data_module=data_module, *args, **kwargs
        )

    def _on_retry(
        self,
        prefix: str,
        max_attempts: int,
        wait_in_seconds: int,
        attempt: int,
        retry_state: RetryCallState,
        callback: Optional[Callable[[int, RetryCallState], None]] = None,
        *args,
        **kwargs,
    ):
        (
            self.logger.info(
                f"{prefix}: failed. delay {wait_in_seconds} seconds and retry {attempt}/{max_attempts}."
            )
            if callback is None
            else callback(
                prefix,
                max_attempts,
                wait_in_seconds,
                attempt,
                retry_state,
                *args,
                **kwargs,
            )
        )

    def _on_retry_error(
        self,
        prefix: str,
        error: Exception,
        callback: Optional[Callable[[Exception], None]] = None,
        *args,
        **kwargs,
    ):
        (
            self.logger.error(error)
            if callback is None
            else callback(prefix, error, *args, **kwargs)
        )

    def _on_retry_last_error(
        self,
        prefix: str,
        attempt: int,
        error: RetryError,
        callback: Optional[Callable[[int, RetryError], None]] = None,
        *args,
        **kwargs,
    ):
        (
            self.logger.error(f"{prefix}: failed.")
            if callback is None
            else callback(prefix, attempt, error, *args, **kwargs)
        )

    def _get_data_config(self, name: str, cls: Type[AppData]):
        return self.config.app.datas.get_data(name, cls)
