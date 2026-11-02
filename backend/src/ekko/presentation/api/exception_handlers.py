"""FastAPI exception handler registration.

Provides a centralized place for exception-to-HTTP-response mapping.
Aligns with Clean Architecture by keeping exception handling in the
presentation layer without leaking domain internals.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import status
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from ekko.core.exceptions import (
    AudioDeviceError,
    ConfigurationError,
    EkkoError,
    LLMError,
    PromptNotFoundError,
    STTError,
)

if TYPE_CHECKING:
    from fastapi import FastAPI
    from starlette.requests import Request

    from ekko.core.types import JSONDict

_logger = logging.getLogger(__name__)


def _request_log_extra(request: Request, *, status_code: int) -> JSONDict:
    """Build structured logging context from request metadata.

    Args:
        request (Request): Incoming HTTP request.
        status_code (int): HTTP status returned to the client.

    Returns:
        JSONDict: Structured request metadata. The request correlation id is
            injected globally by the logging filter, so it is omitted here.
    """
    return {
        "method": request.method,
        "scheme": request.url.scheme,
        "path": request.url.path,
        "query": request.url.query,
        "status_code": status_code,
    }


def _error_detail(message: str) -> JSONDict:
    """Create a standardized JSON error payload.

    Args:
        message (str): Error message for API clients.

    Returns:
        JSONDict: Standardized payload with error detail.
    """
    return {"detail": message}


def _log_failure(
    request: Request,
    *,
    event: str,
    level: int,
    status_code: int,
    exc: Exception | None = None,
    detail: str | None = None,
) -> None:
    """Log a handled request failure with request context.

    Args:
        request (Request): Incoming HTTP request.
        event (str): Human-readable event message.
        level (int): Logging severity.
        status_code (int): HTTP status returned to the client.
        exc (Exception | None): Original exception; when provided, its traceback
            is attached for server-side debugging.
        detail (str | None): Human-readable cause for expected failures that
            carry no traceback.
    """
    extra = _request_log_extra(request, status_code=status_code)
    if detail:
        extra["detail"] = detail
    _logger.log(level, event, exc_info=exc, extra=extra)


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers on application.

    Args:
        app (FastAPI): FastAPI application instance.
    """

    @app.exception_handler(RequestValidationError)
    async def _request_validation_error(request: Request, _exc: RequestValidationError) -> JSONResponse:
        _log_failure(
            request,
            event="Request validation failed",
            level=logging.WARNING,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=_error_detail("Request validation error"),
        )

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_exceeded(request: Request, _exc: RateLimitExceeded) -> JSONResponse:
        _log_failure(
            request,
            event="Rate limit exceeded",
            level=logging.WARNING,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=_error_detail("Too many requests; please try again later"),
        )

    @app.exception_handler(PromptNotFoundError)
    async def _prompt_not_found(request: Request, exc: PromptNotFoundError) -> JSONResponse:
        _log_failure(
            request,
            event="Prompt not found",
            level=logging.WARNING,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=_error_detail(str(exc)),
        )

    @app.exception_handler(ConfigurationError)
    async def _configuration_error(request: Request, exc: ConfigurationError) -> JSONResponse:
        _log_failure(
            request,
            event="Configuration error",
            level=logging.ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            exc=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_detail("Configuration error"),
        )

    @app.exception_handler(AudioDeviceError)
    async def _audio_error(request: Request, exc: AudioDeviceError) -> JSONResponse:
        _log_failure(
            request,
            event="Audio device error",
            level=logging.ERROR,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            exc=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_detail("Audio device unavailable"),
        )

    @app.exception_handler(STTError)
    async def _stt_error(request: Request, exc: STTError) -> JSONResponse:
        _log_failure(
            request,
            event="Speech-to-text error",
            level=logging.ERROR,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            exc=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_detail("Speech-to-text service error"),
        )

    @app.exception_handler(LLMError)
    async def _llm_error(request: Request, exc: LLMError) -> JSONResponse:
        _log_failure(
            request,
            event="LLM error",
            level=logging.ERROR,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            exc=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_detail("LLM service error"),
        )

    @app.exception_handler(EkkoError)
    async def _domain_error(request: Request, exc: EkkoError) -> JSONResponse:
        _log_failure(
            request,
            event="Domain error",
            level=logging.WARNING,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=_error_detail("Request could not be processed"),
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        _log_failure(
            request,
            event="Unhandled exception",
            level=logging.ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            exc=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_detail("Internal server error"),
        )
