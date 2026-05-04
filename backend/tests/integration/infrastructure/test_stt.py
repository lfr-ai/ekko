"""Integration tests for STT transcriber."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from ekko.config.settings import BaseAppConfig

pytestmark = pytest.mark.integration


@pytest.fixture
def test_audio_file() -> Path:
    """Provide path to test audio fixture."""
    return Path(__file__).parent.parent.parent / "fixtures" / "audio" / "test_audio_1s.wav"


@pytest.fixture
def mock_whisper_model():
    """Mock FasterWhisper model for testing."""
    mock_model = MagicMock()

    # Mock transcribe method
    mock_segment = MagicMock()
    mock_segment.text = "Test transcription"

    mock_info = MagicMock()
    mock_info.language = "da"

    mock_model.transcribe.return_value = ([mock_segment], mock_info)

    return mock_model


@pytest.mark.asyncio
async def test_faster_whisper_start_stop(integration_settings: BaseAppConfig) -> None:
    """Test starting and stopping the STT transcriber."""
    from ekko.infrastructure.stt.transcriber import FasterWhisperSTT

    with patch("ekko.infrastructure.stt.transcriber.FasterWhisperModel") as mock_model_cls:
        mock_model_cls.return_value = MagicMock()

        transcriber = FasterWhisperSTT(
            settings=integration_settings,
            model_name="tiny",
            device="cpu",
            compute_type="int8",
        )

        await transcriber.start()
        assert transcriber._running is True
        assert transcriber._model is not None

        await transcriber.stop()
        assert transcriber._running is False


@pytest.mark.asyncio
async def test_faster_whisper_ensure_queue(integration_settings: BaseAppConfig) -> None:
    """Test ensuring a processing queue exists."""
    from ekko.infrastructure.stt.transcriber import FasterWhisperSTT

    with patch("ekko.infrastructure.stt.transcriber.FasterWhisperModel") as mock_model_cls:
        mock_model_cls.return_value = MagicMock()

        transcriber = FasterWhisperSTT(
            settings=integration_settings,
            model_name="tiny",
            device="cpu",
            compute_type="int8",
        )

        await transcriber.start()

        queue_name = "test_queue"
        await transcriber.ensure_queue(queue_name)

        assert queue_name in transcriber._queues
        assert queue_name in transcriber._tasks

        await transcriber.stop()


@pytest.mark.asyncio
async def test_faster_whisper_accept_bytes(integration_settings: BaseAppConfig) -> None:
    """Test accepting audio bytes for processing."""
    from ekko.infrastructure.stt.transcriber import FasterWhisperSTT

    with patch("ekko.infrastructure.stt.transcriber.FasterWhisperModel") as mock_model_cls:
        mock_model_cls.return_value = MagicMock()

        transcriber = FasterWhisperSTT(
            settings=integration_settings,
            model_name="tiny",
            device="cpu",
            compute_type="int8",
        )

        await transcriber.start()

        queue_name = "audio_queue"
        test_data = b"fake_audio_data"

        await transcriber.accept_bytes(queue_name, test_data)

        # Verify queue was created and data added
        assert queue_name in transcriber._queues
        assert not transcriber._queues[queue_name].empty()

        await transcriber.stop()


@pytest.mark.asyncio
async def test_faster_whisper_transcribe_with_callback(
    integration_settings: BaseAppConfig,
    mock_whisper_model: MagicMock,
) -> None:
    """Test transcription with callback function."""
    from ekko.infrastructure.stt.transcriber import FasterWhisperSTT

    transcripts_received = []

    def on_transcript_callback(transcript):
        transcripts_received.append(transcript)

    with patch("ekko.infrastructure.stt.transcriber.FasterWhisperModel") as mock_model_cls:
        mock_model_cls.return_value = mock_whisper_model

        transcriber = FasterWhisperSTT(
            settings=integration_settings,
            model_name="tiny",
            device="cpu",
            compute_type="int8",
            batch_seconds=0.1,  # Short batch for faster test
            on_transcript=on_transcript_callback,
        )

        await transcriber.start()

        # Send enough data to trigger processing
        queue_name = "callback_queue"
        test_data = b"\x00\x01" * 1024  # 2KB of fake audio data

        await transcriber.accept_bytes(queue_name, test_data)

        # Wait for processing
        await asyncio.sleep(0.3)

        await transcriber.stop()

        # Verify callback was invoked
        assert len(transcripts_received) > 0
        assert transcripts_received[0].stream_name == queue_name


@pytest.mark.asyncio
async def test_faster_whisper_transcribe_with_queue(
    integration_settings: BaseAppConfig,
    mock_whisper_model: MagicMock,
) -> None:
    """Test transcription with output queue."""
    from ekko.infrastructure.stt.transcriber import FasterWhisperSTT

    output_queue: asyncio.Queue = asyncio.Queue()

    with patch("ekko.infrastructure.stt.transcriber.FasterWhisperModel") as mock_model_cls:
        mock_model_cls.return_value = mock_whisper_model

        transcriber = FasterWhisperSTT(
            settings=integration_settings,
            model_name="tiny",
            device="cpu",
            compute_type="int8",
            batch_seconds=0.1,
            output_queue=output_queue,
        )

        await transcriber.start()

        # Send enough data to trigger processing
        queue_name = "output_queue_test"
        test_data = b"\x00\x01" * 1024

        await transcriber.accept_bytes(queue_name, test_data)

        # Wait for processing
        await asyncio.sleep(0.3)

        await transcriber.stop()

        # Verify output queue received transcript
        assert not output_queue.empty()
        transcript = await output_queue.get()
        assert transcript.stream_name == queue_name


@pytest.mark.asyncio
async def test_faster_whisper_missing_module_error(integration_settings: BaseAppConfig) -> None:
    """Test error handling when faster-whisper is not available."""
    from ekko.infrastructure.stt.transcriber import FasterWhisperSTT

    with patch("ekko.infrastructure.stt.transcriber.FasterWhisperModel", None):
        transcriber = FasterWhisperSTT(
            settings=integration_settings,
            model_name="tiny",
        )

        with pytest.raises(RuntimeError, match="faster-whisper is not installed"):
            await transcriber.start()


@pytest.mark.asyncio
async def test_faster_whisper_raw_pcm_to_wav(integration_settings: BaseAppConfig) -> None:
    """Test conversion of raw PCM bytes to WAV file."""
    from ekko.infrastructure.stt.transcriber import FasterWhisperSTT

    transcriber = FasterWhisperSTT(
        settings=integration_settings,
        model_name="tiny",
        sample_rate=16000,
        channels=1,
    )

    # Create fake PCM data (16-bit integers)
    import numpy as np

    sample_count = 16000  # 1 second at 16kHz
    fake_pcm = np.zeros(sample_count, dtype=np.int16)
    raw_bytes = fake_pcm.tobytes()

    wav_path = transcriber._raw_pcm_bytes_to_wav_file(raw_bytes, 16000, 1)

    # Verify WAV file was created
    assert Path(wav_path).exists()

    # Cleanup
    Path(wav_path).unlink()
