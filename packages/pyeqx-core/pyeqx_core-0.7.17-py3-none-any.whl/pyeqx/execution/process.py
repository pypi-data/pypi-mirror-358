from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from logging import Logger
from typing import Any, List, Optional, Union

from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import StructType

from pyeqx.common.result import FunctionExecuteResult
from pyeqx.core import Configuration, Operation
from pyeqx.core.models import AppData
from pyeqx.core.models.module.properties import FileDataModuleProperties
from pyeqx.core.models.storage.properties import AzureAdlsGen2StorageDataProperties
from pyeqx.core.schemas import (
    BRONZE_LOG_SCHEMA,
    BRONZE_METADATA_SCHEMA,
)
from pyeqx.core.spark import create_dataframe
from pyeqx.core.utils.common import build_path
from pyeqx.execution import ProcessBase
from pyeqx.execution.parameter import ExecuteParameters


@dataclass
class ProcessExecutionParameters:
    def __init__(
        self,
        name: str,
    ):
        self.name = name


@dataclass
class ProcessParameters(ExecuteParameters):
    def __init__(
        self,
        is_log_load_data=False,
    ):
        self.is_log_load_data = is_log_load_data


class Process(ProcessBase):
    _is_log_load_data: bool

    _execution_timestamp: datetime

    def __init__(self, config: Configuration, logger: Logger, operation: Operation):
        super().__init__(config, logger, operation)

    def _do_execute(self, parameters: ProcessExecutionParameters, *args, **kwargs):
        self._execution_timestamp = datetime.now()

        timestamp_str = self._execution_timestamp.isoformat()

        self.logger.info(f"start process at {timestamp_str}")

        # process datas
        self._process_datas(parameters=parameters)

    def configure(
        self,
        parameters: ProcessParameters,
    ):
        self._is_log_load_data = parameters.is_log_load_data

    @abstractmethod
    def _read_datas(self, parameters: ProcessExecutionParameters):
        """
        Read all datas from both source and destination.

        Args:
            parameters (ProcessExecuteParameters): Parameters to execute process.
        """
        pass

    @abstractmethod
    def _process_datas(self, parameters: ProcessExecutionParameters):
        """
        Process all datas from both source and destination.

        Args:
            parameters (ProcessExecuteParameters): Parameters to execute process.
        """
        pass

    def _upsert_bronze_metadata(self, name: str, data: dict[str, Any]):
        """
        Upsert metadata information to specific destination by module name.

        Args:
            name (str): name of module in configuration to find table and its database
            data (dict[str, Any]): metadata value to upsert

        Returns:
            Result[bool] | ErrorResult: result of upsert metadata
        """
        bronze_data_table = data.get("bronze_data_table")

        try:
            self.logger.debug(f"upsert metadata: {bronze_data_table}")

            data_config = self._get_data_config(name=name, cls=AppData)
            data_props = data_config.dest.get_properties(FileDataModuleProperties)
            storage_props = self.operation.get_storage(
                name=data_props.storage
            ).get_properties(AzureAdlsGen2StorageDataProperties)

            paths = []
            if storage_props.path:
                paths.append(storage_props.path)

            if data_props.path:
                paths.append(data_props.path)

            path = build_path(
                base_path=storage_props.endpoint,
                paths=paths,
            )

            record = create_dataframe(
                spark=self.operation.get_current_spark_session(),
                schema=BRONZE_METADATA_SCHEMA,
                datas=[data],
            )

            self.operation.upsert_delta_to(
                data=record.alias("updates"),
                path=path,
                matches=lambda _: {
                    "datas.bronze_data_table": "updates.bronze_data_table",
                    "datas.source_system": "updates.source_system",
                    "datas.source_type": "updates.source_type",
                    "datas.source_name": "updates.source_name",
                    "datas.updated_at": "updates.updated_at",
                },
                condition=lambda _: F.col("datas.bronze_data_table")
                == F.col("updates.bronze_data_table"),
            )

            return FunctionExecuteResult(data=True)
        except Exception as e:
            self.logger.error(
                f"error: upsert metadata: {bronze_data_table}",
            )
            return FunctionExecuteResult(error=e)

    def _write_bronze_ingestion_log(self, name: str, data: dict[str, Any]):
        try:
            log_data = create_dataframe(
                spark=self.operation.get_current_spark_session(),
                schema=BRONZE_LOG_SCHEMA,
                datas=[data],
            )

            self._write_destination(
                name=name,
                data=log_data,
                options={"mode": "append"},
            )
            return FunctionExecuteResult(data=True)
        except Exception as e:
            self.logger.error(
                "error: write ingestion log",
            )
            return FunctionExecuteResult(error=e)

    # region common operation (read/write)

    def _read_source(
        self, name: str, schema: Optional[StructType] = None, options: dict = {}
    ):
        """
        Read from source data.

        Args:
            name (str): name of module in configuration to find table and its database.
            schema (StructType, optional): schema for table. Defaults to None - for dynamic schema.
            options (dict, optional): options for reading data. Defaults to {}.

        Returns:
            DataFrame: DataFrame of source data.
        """
        data_config = self._get_data_config(name=name, cls=AppData)

        return self.operation.read_source(
            data_module=data_config.src,
            schema=schema,
            options=options,
        )

    def _read_destination(
        self, name: str, schema: Optional[StructType] = None, options: dict = {}
    ):
        """
        Read from destination data.

        Args:
            name (str): name of module in configuration to find table and its database.
            schema (StructType, optional): schema for table. Defaults to None - for dynamic schema.
            options (dict, optional): options for reading data. Defaults to {}.

        Returns:
            DataFrame: DataFrame of destination data.
        """
        data_config = self._get_data_config(name=name, cls=AppData)

        assert data_config.dest is not None, f"destination data not found for {name}"

        return self.operation.read_source(
            data_module=data_config.dest,
            schema=schema,
            options=options,
        )

    def _write_destination(
        self,
        name: str,
        data: DataFrame,
        options: dict = {},
        partition_by: Optional[Union[str, List[str]]] = None,
    ):
        """
        Write to destination data.

        Args:
            name (str): name of module in configuration to find table and its database.
        """
        data_config = self._get_data_config(name=name, cls=AppData)

        return self.operation.write_destination(
            data=data,
            data_module=data_config.dest,
            options=options,
            partition_by=partition_by,
        )

    # endregion
