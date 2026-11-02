"""STT service factory.

Creates the appropriate STT service implementation based on availability and
configuration. Prefers Azure Speech Services for production, falls back to
stub for testing without credentials.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from pydantic import SecretStr

    from ekko.core.ports import STTPort
    from ekko.core.value_objects import TranscriptSegment


class _STTConfig(Protocol):
    """Configuration fields required by the STT factory."""

    azure_speech_key: SecretStr | None
    azure_speech_region: str
    azure_speech_language: str
    azure_speech_recognition_mode: str


_logger = logging.getLogger(__name__)


class _StubSTT:
    """Lightweight STT stub used when Azure credentials aren't configured.

    Implements the minimal STTPort protocol surface used by the app so tests
    and dev environments may run without Azure credentials.

    Discards audio bytes because no transcription provider is configured.
    """

    def __init__(
        self,
        settings: _STTConfig,
        *,
        on_transcript: Callable[[TranscriptSegment], object] | None = None,
        emit_interim: bool = False,
    ):
        """Initialize stub STT service.

        Args:
            settings: Application configuration.
            on_transcript: Ignored transcript callback for API compatibility.
            emit_interim: Ignored interim-emission flag for API compatibility.
        """
        del on_transcript, emit_interim
        self.settings = settings
        _logger.warning(
            "Stub speech-to-text initialized",
            extra={"reason": "Azure credentials not configured or SDK unavailable"},
        )

    async def start(self) -> None:
        """Start stub STT service (no-op)."""
        _logger.info("Stub speech-to-text started")

    async def stop(self) -> None:
        """Stop stub STT service (no-op)."""
        _logger.info("Stub speech-to-text stopped")

    async def ensure_queue(self, queue_name: str) -> None:
        """Accept an audio source name for protocol compatibility.

        Args:
            queue_name: Audio source identifier.
        """
        _logger.debug("Stub speech-to-text source accepted", extra={"queue_name": queue_name})

    async def accept_bytes(self, queue_name: str, data: bytes) -> None:
        """Discard audio bytes because no transcriber is configured.

        Args:
            queue_name: Audio source identifier.
            data: Raw audio bytes.
        """
        del queue_name, data


def create_azure_speech_stt(
    settings: _STTConfig,
    *,
    on_transcript: Callable[[TranscriptSegment], object] | None = None,
    emit_interim: bool = False,
) -> STTPort:
    """Factory to create an STTPort.

    Prefers Azure Speech Services for production transcription. Falls back to
    stub implementation if Azure SDK is unavailable or credentials are missing.

    Args:
        settings: Application configuration with Azure credentials.
        on_transcript: Optional callback invoked for recognized transcripts.
        emit_interim: Whether to emit interim recognition results.

    Returns:
        STTPort implementation (Azure or stub).

    **Behavior:**
    - If Azure SDK available + credentials configured → AzureSpeechSTT
    - Otherwise → _StubSTT (logs warning)

    **Example:**
    ::

        stt = create_azure_speech_stt(settings, on_transcript=callback)
        await stt.start()
    """
    try:
        # Import lazily to avoid hard dependency during test collection
        from ekko.infrastructure.stt.azure_speech_stt import (  # noqa: PLC0415
            AZURE_SPEECH_AVAILABLE,
            AzureSpeechSTT,
        )

        # Check if Azure SDK is available
        if not AZURE_SPEECH_AVAILABLE:
            _logger.warning(
                "Azure Speech SDK unavailable",
                extra={"reason": "azure-cognitiveservices-speech not installed"},
            )
            return _StubSTT(
                settings=settings,
                on_transcript=on_transcript,
                emit_interim=emit_interim,
            )

        # Check if credentials are configured
        if settings.azure_speech_key is None:
            _logger.warning(
                "Azure Speech credentials missing",
                extra={"reason": "EKKO_AZURE_SPEECH_KEY not set"},
            )
            return _StubSTT(
                settings=settings,
                on_transcript=on_transcript,
                emit_interim=emit_interim,
            )

        # All good — create real Azure STT service
        _logger.info(
            "Creating Azure speech-to-text service",
            extra={
                "region": settings.azure_speech_region,
                "language": settings.azure_speech_language,
            },
        )
        return AzureSpeechSTT(
            settings=settings,
            on_transcript=on_transcript,
            emit_interim=emit_interim,
        )

    except Exception:
        _logger.exception("Failed to create Azure speech-to-text service")
        return _StubSTT(
            settings=settings,
            on_transcript=on_transcript,
            emit_interim=emit_interim,
        )
