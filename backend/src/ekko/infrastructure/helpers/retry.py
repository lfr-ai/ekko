"""Retry and backoff policy utilities.

Uses tenacity for production-grade retry logic with exponential backoff.
Provides two retry policies:
- ``http_retry``: General HTTP operations (shorter backoff)
- ``api_retry``: LLM/AI API operations (longer backoff for rate limits)

Transient exceptions from HTTP clients and LLM providers (LiteLLM) are retried.
Exhausted retries will be caught and translated to provider-neutral Core LLMError
at the adapter boundary (see chat.py).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

import httpx
import litellm
from fastapi import status
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

type _Retry[R] = Callable[[Callable[..., R]], Callable[..., R]]

_MAX_ATTEMPTS = 3

_HTTP_BACKOFF_MULTIPLIER = 1.5
_HTTP_BACKOFF_MIN_SECONDS = 2
_HTTP_BACKOFF_MAX_SECONDS = 15

_API_BACKOFF_MULTIPLIER = 2
_API_BACKOFF_MIN_SECONDS = 4
_API_BACKOFF_MAX_SECONDS = 30

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

# LiteLLM normalizes provider exceptions; these are the transient ones worth retrying.
_TRANSIENT_LITELLM_ERRORS = (
    litellm.APIError,
    litellm.APIConnectionError,
    litellm.InternalServerError,
    litellm.RateLimitError,
    litellm.ServiceUnavailableError,
    litellm.Timeout,
)

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

# Retry policy for LLM/AI API operations (longer backoff for rate limits)
# Uses LiteLLM-normalized exceptions; exhausted failures will be caught and
# translated to Core LLMError at the adapter boundary (see chat.py).
# NOTE: reraise=True will re-raise the exhausted exception; the adapter
# (chat.py) must catch it and translate to provider-neutral LLMError.
api_retry: Final[_Retry] = retry(
    stop=stop_after_attempt(_MAX_ATTEMPTS),
    wait=wait_exponential(
        multiplier=_API_BACKOFF_MULTIPLIER,
        min=_API_BACKOFF_MIN_SECONDS,
        max=_API_BACKOFF_MAX_SECONDS,
    ),
    retry=retry_if_exception_type(
        _TRANSIENT_HTTP_ERRORS + _TRANSIENT_LITELLM_ERRORS,
    ),
    reraise=True,
)
