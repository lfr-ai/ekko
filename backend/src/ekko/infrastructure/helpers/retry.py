"""Retry and backoff policy utilities.

Uses tenacity for production-grade retry logic with exponential backoff.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final, TypeVar

import httpx
from fastapi import status
from openai import APIConnectionError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

F = TypeVar("F", bound=Callable[..., object])

_MAX_RETRY_ATTEMPTS: Final[int] = 3
_WAIT_MULTIPLIER: Final[int] = 1
_WAIT_MIN: Final[int] = 1
_WAIT_MAX: Final[int] = 10

_RETRYABLE_HTTP_STATUS_CODES = frozenset(
    {
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        status.HTTP_502_BAD_GATEWAY,
        status.HTTP_503_SERVICE_UNAVAILABLE,
        status.HTTP_504_GATEWAY_TIMEOUT,
    }
)


def _is_retryable_http_error(exception: BaseException) -> bool:
    """Check if HTTP error is retryable based on status code.

    Args:
        exception (BaseException): Exception to check.

    Returns:
        bool: True if error should be retried.
    """
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in _RETRYABLE_HTTP_STATUS_CODES
    return False


_TRANSIENT_ERRORS = (
    ConnectionError,
    TimeoutError,
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
)

api_retry = retry(
    stop=stop_after_attempt(_MAX_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=_WAIT_MULTIPLIER, min=_WAIT_MIN, max=_WAIT_MAX),
    retry=(
        retry_if_exception_type(_TRANSIENT_ERRORS)
        | retry_if_exception_type((APIConnectionError, RateLimitError))
        | retry_if_exception(_is_retryable_http_error)
    ),
    reraise=True,
)
"""Tenacity retry decorator for transient infrastructure failures."""
