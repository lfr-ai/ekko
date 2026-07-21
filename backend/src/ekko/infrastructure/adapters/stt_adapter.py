"""STT adapter factory.

Creates the appropriate STT service implementation based on availability and
configuration. Prefers Azure Speech Services for production, falls back to
stub for testing without credentials.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ekko.config.settings import BaseAppConfig
    from ekko.core.ports import STTService

import structlog

logger = structlog.get_logger(__name__)


class _StubSTT:
    """Lightweight STT stub used when Azure credentials aren't configured.

    Implements the minimal STTService protocol surface used by the app so tests
    and dev environments may run without Azure credentials.

    Only accepts and buffers audio bytes — does not perform actual transcription.
    """

    def __init__(self, settings: BaseAppConfig, **_kwargs) -> None:
        """Initialize stub STT service.

        Args:
            settings: Application configuration.
            **kwargs: Ignored (for API compatibility).
        """
        self.settings = settings

        # Map queue name -> asyncio.Queue (used for stub testing)
        self._queues: dict[str, Any] = {}
        logger.warning(
            "stub_stt_initialized",
            reason="Azure credentials not configured or SDK unavailable",
        )

    async def start(self) -> None:
        """Start stub STT service (no-op)."""
        logger.info("stub_stt_started")

    async def stop(self) -> None:
        """Stop stub STT service (no-op)."""
        logger.info("stub_stt_stopped")

    async def ensure_queue(self, queue_name: str) -> None:
        """Ensure a queue exists for the given name.

        Args:
            queue_name: Audio source identifier.
        """
        if queue_name not in self._queues:
            self._queues[queue_name] = asyncio.Queue()
            logger.debug("stub_stt_queue_created", queue_name=queue_name)

    async def accept_bytes(self, queue_name: str, data: bytes) -> None:
        """Accept audio bytes (buffered but not transcribed).

        Args:
            queue_name: Audio source identifier.
            data: Raw audio bytes.
        """
        # Place raw bytes into internal asyncio queue for possible inspection
        q = self._queues.get(queue_name)
        if q is not None:
            try:
                await q.put(data)
            except Exception:
                logger.exception("stub_stt_queue_error", queue_name=queue_name)


def create_azure_speech_stt(
    settings: BaseAppConfig,
    **kwargs,
) -> STTService:
    """Factory to create an STTService.

    Prefers Azure Speech Services for production transcription. Falls back to
    stub implementation if Azure SDK is unavailable or credentials are missing.

    Args:
        settings: Application configuration with Azure credentials.
        **kwargs: Additional arguments passed to STT service constructor.

    Returns:
        STTService implementation (Azure or stub).

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
            logger.warning(
                "azure_speech_sdk_unavailable",
                reason="azure-cognitiveservices-speech not installed",
            )
            return _StubSTT(settings=settings, **kwargs)

        # Check if credentials are configured
        if settings.azure_speech_key is None:
            logger.warning(
                "azure_speech_credentials_missing",
                reason="EKKO_AZURE_SPEECH_KEY not set",
            )
            return _StubSTT(settings=settings, **kwargs)

        # All good — create real Azure STT service
        logger.info(
            "creating_azure_speech_stt",
            region=settings.azure_speech_region,
            language=settings.azure_speech_language,
        )
        return AzureSpeechSTT(settings=settings, **kwargs)

    except Exception:
        logger.exception("failed_to_create_azure_stt")
        logger.warning("falling_back_to_stub_stt")
        return _StubSTT(settings=settings, **kwargs)
