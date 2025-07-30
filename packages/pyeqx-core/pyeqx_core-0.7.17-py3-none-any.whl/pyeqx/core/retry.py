from typing import Callable, Optional, TypeVar, Union

from tenacity import (
    RetryCallState,
    RetryError,
    Retrying,
    retry_base,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_fixed,
)

T = TypeVar("T")

TCondition = Union[retry_base, Callable[[RetryCallState], bool]]


def retry_and_wait(
    max_attempts: int,
    wait_in_seconds: int,
    fn: Callable[..., T],
    condition: Optional[Callable[[T], bool]] = None,
    on_retry: Optional[Callable[[int, RetryCallState], None]] = None,
    on_error: Optional[Callable[[Exception], None]] = None,
    on_last_error: Optional[Callable[[int, RetryError], None]] = None,
    *args,
    **kwargs,
) -> T:
    try:
        if condition is None:
            condition = __default_condition

        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts + 1),
            wait=wait_fixed(wait_in_seconds),
            retry=retry_if_result(condition) | retry_if_exception_type(),
            before_sleep=lambda retry_state: __on_retry(
                retry_state=retry_state, fn=on_retry, *args, **kwargs
            ),
        ):
            with attempt:
                return __retry_and_wait(fn=fn, on_error=on_error, *args, **kwargs)
    except RetryError as e:
        if on_last_error:
            on_last_error(e.last_attempt.attempt_number - 1, e, *args, **kwargs)
        raise


def __default_condition() -> bool:
    return False


def __on_retry(
    retry_state: RetryCallState,
    fn: Optional[Callable[[int, RetryError], None]] = None,
    *args,
    **kwargs,
) -> None:
    if fn:
        fn(retry_state.attempt_number, retry_state, *args, **kwargs)


def __retry_and_wait(
    fn: Callable[..., T],
    on_error: Optional[Callable[[Exception], None]] = None,
    *args,
    **kwargs,
):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        if on_error:
            on_error(e)
        raise
