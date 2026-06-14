"""Retry and backoff policy utilities.

Uses tenacity for production-grade retry logic with exponential backoff.
Provides two retry policies:
- ``http_retry``: General HTTP operations (shorter backoff)
- ``api_retry``: LLM/AI API operations (longer backoff for rate limits)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

import httpx
from fastapi import status
from openai import APIConnectionError, APIError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

type _Retry[R] = Callable[[Callable[..., R]], Callable[..., R]]

_MAX_ATTEMPTS: Final[int] = 3

_HTTP_BACKOFF_MULTIPLIER: Final[float] = 1.5
_HTTP_BACKOFF_MIN_SECONDS: Final[int] = 2
_HTTP_BACKOFF_MAX_SECONDS: Final[int] = 15

_API_BACKOFF_MULTIPLIER: Final[int] = 2
_API_BACKOFF_MIN_SECONDS: Final[int] = 4
_API_BACKOFF_MAX_SECONDS: Final[int] = 30

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


_TRANSIENT_HTTP_ERRORS = (
    ConnectionError,
    TimeoutError,
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
)

_TRANSIENT_OPENAI_ERRORS = (APIError, RateLimitError, APIConnectionError)

# Retry policy for general HTTP operations
http_retry: Final[_Retry] = retry(
    stop=stop_after_attempt(_MAX_ATTEMPTS),
    wait=wait_exponential(
        multiplier=_HTTP_BACKOFF_MULTIPLIER,
        min=_HTTP_BACKOFF_MIN_SECONDS,
        max=_HTTP_BACKOFF_MAX_SECONDS,
    ),
    retry=(retry_if_exception_type(_TRANSIENT_HTTP_ERRORS) | retry_if_exception(_is_retryable_http_error)),
    reraise=True,
)
"""Tenacity retry decorator for transient HTTP failures."""

# Retry policy for LLM/AI API operations (longer backoff for rate limits)
api_retry: Final[_Retry] = retry(
    stop=stop_after_attempt(_MAX_ATTEMPTS),
    wait=wait_exponential(
        multiplier=_API_BACKOFF_MULTIPLIER,
        min=_API_BACKOFF_MIN_SECONDS,
        max=_API_BACKOFF_MAX_SECONDS,
    ),
    retry=retry_if_exception_type(
        _TRANSIENT_HTTP_ERRORS + _TRANSIENT_OPENAI_ERRORS,
    ),
    reraise=True,
)
"""Tenacity retry decorator for transient LLM/AI API failures."""
