"""Typed FastAPI dependencies for runtime application state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException, Request, status

if TYPE_CHECKING:
    from ekko.application.services import PIIService, ReadinessService, SummarizerService, TranscriptBroadcaster
    from ekko.core.ports import AudioStreamerControllerPort


def get_stream_controller(request: Request) -> AudioStreamerControllerPort:
    """Resolve the configured stream controller.

    Args:
        request (Request): Current FastAPI request.

    Returns:
        AudioStreamerControllerPort: Configured audio stream controller.

    Raises:
        HTTPException: If audio streaming is unavailable for this application.
    """
    controller = getattr(request.app.state, "controller", None)
    if controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stream controller unavailable",
        )
    return controller


def get_pii_service(request: Request) -> PIIService:
    """Resolve the configured PII service."""
    return request.app.state.pii_service


def get_summarizer_service(request: Request) -> SummarizerService:
    """Resolve the configured summarizer service."""
    return request.app.state.summarizer_service


def get_readiness_service(request: Request) -> ReadinessService:
    """Resolve the configured readiness service."""
    return request.app.state.readiness_service


def get_transcript_broadcaster(request: Request) -> TranscriptBroadcaster:
    """Resolve the live transcript broadcaster."""
    return request.app.state.transcript_broadcaster
