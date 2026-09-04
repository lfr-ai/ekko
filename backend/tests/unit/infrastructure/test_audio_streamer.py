"""Tests for audio streamer task and resource ownership."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from ekko.config.base import BaseAppConfig
from ekko.infrastructure.audio_streamer.audio_streamer import AudioStreamer


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stop_when_queue_tasks_running_cancels_and_awaits_them() -> None:
    """Stopping the streamer deterministically finishes every owned queue task."""
    settings = BaseAppConfig()
    streamer = AudioStreamer(settings)
    stream = MagicMock()
    stream.read.side_effect = lambda _frames: b"audio"
    streamer.stream_sys = stream
    streamer.p = MagicMock()
    queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=1)
    streamer.running = True
    task = asyncio.create_task(streamer._stream_audio(stream, queue))
    streamer._queue_tasks.add(task)
    await asyncio.sleep(0)

    await streamer.stop()

    assert task.done()
    assert streamer._queue_tasks == set()


@pytest.mark.unit
def test_controller_initialization_does_not_construct_audio_streamer() -> None:
    """The subprocess controller does not initialize unused audio hardware state."""
    with patch(
        "ekko.infrastructure.audio_streamer.audio_streamer.AudioStreamer",
        side_effect=AssertionError("unexpected audio hardware construction"),
    ):
        from ekko.infrastructure.audio_streamer.audio_streamer_controller import AudioStreamerController

        AudioStreamerController(BaseAppConfig())
