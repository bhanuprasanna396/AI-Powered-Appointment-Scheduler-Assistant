import time
from typing import Callable, TypeVar

T = TypeVar("T")


def with_retry(func: Callable[[], T], retries: int = 3, backoff_seconds: float = 0.8) -> T:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == retries:
                break
            time.sleep(backoff_seconds * attempt)
    raise RuntimeError(f"Operation failed after {retries} retries: {last_error}") from last_error
