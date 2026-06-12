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

logger = logging.getLogger(__name__)


def _request_log_extra(request: Request) -> JSONDict:
    """Build structured logging context from request metadata.

    Args:
        request (Request): Incoming HTTP request.

    Returns:
        JSONDict: Structured request metadata for logging.
    """
    request_id = getattr(request.state, "request_id", "-")
    return {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "query": request.url.query,
        "client_ip": request.client.host if request.client else "-",
        "component": "exception_handler",
    }


def _error_detail(message: str) -> JSONDict:
    """Create a standardized JSON error payload.

    Args:
        message (str): Error message for API clients.

    Returns:
        JSONDict: Standardized payload with error detail.
    """
    return {"detail": message}


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers on application.

    Args:
        app (FastAPI): FastAPI application instance.
    """

    @app.exception_handler(RequestValidationError)
    async def _request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(
            "Request validation error",
            extra=_request_log_extra(request),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=_error_detail("Request validation error"),
        )

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_exceeded(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        logger.warning(
            "Rate limit exceeded",
            extra=_request_log_extra(request),
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=_error_detail("Too many requests; please try again later"),
        )

    @app.exception_handler(PromptNotFoundError)
    async def _prompt_not_found(request: Request, exc: PromptNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=_error_detail(str(exc)),
        )

    @app.exception_handler(ConfigurationError)
    async def _configuration_error(request: Request, exc: ConfigurationError) -> JSONResponse:
        logger.error(
            "Configuration error",
            extra=_request_log_extra(request),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_detail("Configuration error"),
        )

    @app.exception_handler(AudioDeviceError)
    async def _audio_error(request: Request, exc: AudioDeviceError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_detail(str(exc)),
        )

    @app.exception_handler(STTError)
    async def _stt_error(request: Request, exc: STTError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_detail("Speech-to-text service error"),
        )

    @app.exception_handler(LLMError)
    async def _llm_error(request: Request, exc: LLMError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_detail("LLM service error"),
        )

    @app.exception_handler(EkkoError)
    async def _domain_error(request: Request, exc: EkkoError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=_error_detail(str(exc)),
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "Unhandled exception on %s %s",
            request.method,
            request.url.path,
            extra=_request_log_extra(request),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_detail("Internal server error"),
        )
