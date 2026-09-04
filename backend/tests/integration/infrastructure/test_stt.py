"""Integration tests for STT adapter wiring and fallback behavior."""

import asyncio
from unittest.mock import patch

import pytest
from pydantic import SecretStr

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_create_azure_speech_stt_when_credentials_missing_then_returns_stub(integration_settings) -> None:
    """Factory should gracefully fall back to stub when key is not configured."""
    from ekko.infrastructure.adapters.stt_adapter import _StubSTT, create_azure_speech_stt

    stt = create_azure_speech_stt(settings=integration_settings)

    assert isinstance(stt, _StubSTT)

    await stt.start()
    await stt.ensure_queue("mic")
    await stt.accept_bytes("mic", b"audio")


def test_create_azure_speech_stt_when_sdk_unavailable_then_returns_stub(integration_settings) -> None:
    """Factory should return stub when Azure SDK is not available."""
    from ekko.infrastructure.adapters.stt_adapter import _StubSTT, create_azure_speech_stt

    settings_with_key = integration_settings.model_copy(update={"azure_speech_key": SecretStr("fake-key")})

    with patch("ekko.infrastructure.stt.azure_speech_stt.AZURE_SPEECH_AVAILABLE", False):
        stt = create_azure_speech_stt(settings=settings_with_key)

    assert isinstance(stt, _StubSTT)


def test_create_azure_speech_stt_when_sdk_and_credentials_present_then_returns_real_service(
    integration_settings,
) -> None:
    """Factory should build AzureSpeechSTT when requirements are present."""
    from ekko.infrastructure.adapters.stt_adapter import create_azure_speech_stt

    settings_with_key = integration_settings.model_copy(update={"azure_speech_key": SecretStr("fake-key")})

    with patch("ekko.infrastructure.stt.azure_speech_stt.AZURE_SPEECH_AVAILABLE", True):
        stt = create_azure_speech_stt(settings=settings_with_key)

    assert stt.__class__.__name__ == "AzureSpeechSTT"


@pytest.mark.asyncio
async def test_azure_speech_stt_stop_cancels_outstanding_transcript_callbacks(integration_settings) -> None:
    """Stopping Azure STT waits for callback-created emission tasks to finish."""
    from ekko.core.value_objects import TranscriptSegment
    from ekko.infrastructure.stt.azure_speech_stt import AzureSpeechSTT

    callback_started = asyncio.Event()
    callback_cancelled = asyncio.Event()

    async def blocking_callback(_transcript: TranscriptSegment) -> None:
        callback_started.set()
        try:
            await asyncio.Event().wait()
        finally:
            callback_cancelled.set()

    settings_with_key = integration_settings.model_copy(update={"azure_speech_key": SecretStr("fake-key")})
    with patch("ekko.infrastructure.stt.azure_speech_stt.AZURE_SPEECH_AVAILABLE", True):
        stt = AzureSpeechSTT(settings=settings_with_key, on_transcript=blocking_callback)

    await stt.start()
    stt._schedule_emit_transcript(
        transcript=TranscriptSegment(
            text="hello",
            source="microphone",
        ),
    )
    await callback_started.wait()

    await stt.stop()

    assert callback_cancelled.is_set()
    assert stt._emission_tasks == set()
