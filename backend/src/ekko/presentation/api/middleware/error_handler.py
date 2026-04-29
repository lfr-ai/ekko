"""Global exception handlers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from fastapi import FastAPI
    from starlette.requests import Request

from ekko.core.exceptions import (
    AudioDeviceError,
    ConfigurationError,
    EkkoError,
    LLMError,
    PromptNotFoundError,
    STTError,
)

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the app."""

    @app.exception_handler(PromptNotFoundError)
    async def _prompt_not_found(request: Request, exc: PromptNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ConfigurationError)
    async def _configuration_error(request: Request, exc: ConfigurationError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": "Configuration error"})

    @app.exception_handler(AudioDeviceError)
    async def _audio_error(request: Request, exc: AudioDeviceError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(STTError)
    async def _stt_error(request: Request, exc: STTError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": "Speech-to-text service error"})

    @app.exception_handler(LLMError)
    async def _llm_error(request: Request, exc: LLMError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": "LLM service error"})

    @app.exception_handler(EkkoError)
    async def _domain_error(request: Request, exc: EkkoError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
