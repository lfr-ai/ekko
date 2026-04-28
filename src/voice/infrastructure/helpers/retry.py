from __future__ import annotations

import asyncio
import time
from functools import wraps
from typing import Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., object])


def api_retry(_func: Optional[F] = None, *, max_attempts: int = 3, backoff_seconds: float = 0.5):
    """Decorator that retries a function or coroutine on exception.

    Supports both usage forms:
      @api_retry
      @api_retry()
      @api_retry(max_attempts=5)
    """

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    time.sleep(backoff_seconds * attempt)

        async def async_wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return await fn(*args, **kwargs)  # type: ignore
                except Exception:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    await asyncio.sleep(backoff_seconds * attempt)

        # Return async wrapper if original is coroutine function
        if asyncio.iscoroutinefunction(fn):
            return async_wrapper  # type: ignore
        return wrapper  # type: ignore

    # If used as @api_retry without args, _func will be the function
    if _func is None:
        return decorator
    return decorator(_func)
