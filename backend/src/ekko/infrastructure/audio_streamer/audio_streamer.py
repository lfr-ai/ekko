"""Audio streamer interface for capturing system and microphone audio."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import pyaudiowpatch as pyaudio
from pyaudiowpatch import Stream

from ekko.core.enums import RecognitionMode

if TYPE_CHECKING:
    from ekko.config.base import BaseAppConfig

logger = logging.getLogger(__name__)

_EMPTY_AUDIO_CHUNK = b""


class AudioStreamer:
    """Stream system + mic audio to STT queues (in this setup, send over TCP)."""

    def __init__(self, settings: BaseAppConfig):
        self.settings = settings
        self.running = False
        self.sending = False
        self._queue_tasks: set[asyncio.Task[None]] = set()

        # PyAudio instance (lazy-created in _initialize)
        self.p: pyaudio.PyAudio | None = None
        # Track send tasks for subprocess-to-main streaming
        self.sys_sending_task: asyncio.Task[None] | None = None
        self.mic_sending_task: asyncio.Task[None] | None = None
        self.stream_sys: Stream | None = None
        self.stream_mic: Stream | None = None
        self.sys_name: str = ""
        self.mic_name: str = ""
        self.mode: RecognitionMode = RecognitionMode.CUSTOMER

    def _require_pyaudio(self) -> pyaudio.PyAudio:
        if self.p is None:
            msg = "PyAudio is not initialized"
            raise RuntimeError(msg)
        return self.p

    def _create_stream(self, device_info: dict[str, object]) -> Stream:
        py_audio = self._require_pyaudio()
        max_input_channels = device_info.get("maxInputChannels")
        default_sample_rate = device_info.get("defaultSampleRate")
        input_device_index = device_info.get("index")
        if not isinstance(max_input_channels, int):
            msg = "Audio device info missing integer maxInputChannels"
            raise TypeError(msg)
        if not isinstance(default_sample_rate, (int, float)):
            msg = "Audio device info missing numeric defaultSampleRate"
            raise TypeError(msg)
        if not isinstance(input_device_index, int):
            msg = "Audio device info missing integer index"
            raise TypeError(msg)

        return py_audio.open(
            format=self.settings.audio_format,
            channels=max_input_channels,
            rate=int(default_sample_rate),
            input=True,
            frames_per_buffer=self.settings.audio_frames_per_buffer,
            input_device_index=input_device_index,
        )

    @staticmethod
    def _require_string_field(*, device_info: dict[str, object], field_name: str) -> str:
        field_value = device_info.get(field_name)
        if not isinstance(field_value, str):
            msg = f"Audio device info missing string {field_name}"
            raise TypeError(msg)
        return field_value

    async def start(
        self,
        sys_queue: asyncio.Queue[bytes] | None = None,
        mic_queue: asyncio.Queue[bytes] | None = None,
    ) -> None:
        """Start streamer tasks (opens devices)."""
        self._initialize()
        self.running = True
        if sys_queue is not None:
            self._queue_tasks.add(asyncio.create_task(self._stream_audio(self.stream_sys, sys_queue)))
        if mic_queue is not None:
            self._queue_tasks.add(asyncio.create_task(self._stream_audio(self.stream_mic, mic_queue)))

    def _initialize(self) -> None:
        self.p = pyaudio.PyAudio()
        self._create_sys_stream()
        self._create_mic_stream()

    def _create_sys_stream(self) -> None:
        sys_info = self._get_sys_info()
        self.sys_name = self._require_string_field(device_info=sys_info, field_name="name")
        self.stream_sys = self._create_stream(sys_info)

    def _get_sys_info(self) -> dict[str, object]:
        self.mode = RecognitionMode.CUSTOMER
        return self._require_pyaudio().get_default_wasapi_loopback()

    def _create_mic_stream(self) -> None:
        mic_info = self._get_mic_info()
        self.mic_name = self._require_string_field(device_info=mic_info, field_name="name")
        self.stream_mic = self._create_stream(mic_info)

    def _get_mic_info(self) -> dict[str, object]:
        self.mode = RecognitionMode.ADVISOR
        return self._require_pyaudio().get_default_input_device_info()

    async def _stream_audio(self, stream: Stream | None, queue: asyncio.Queue[bytes]) -> None:
        """Read audio frames from stream and push to queue while running."""
        if stream is None:
            return

        while self.running:
            data = await asyncio.to_thread(stream.read, self.settings.audio_frames_per_buffer)
            if data == _EMPTY_AUDIO_CHUNK:
                break
            await queue.put(data)

    def start_stream(self) -> None:
        """Begin sending audio frames (subprocess only)."""
        self.sending = True

    def pause_stream(self) -> None:
        """Stop sending audio frames."""
        self.sending = False

    async def stop(self) -> None:
        """Stop all streaming and cleanup."""
        self.sending = False
        self.running = False
        await self._cleanup()

    async def _cleanup(self) -> None:
        owned_tasks = {
            *self._queue_tasks,
            *(task for task in (self.sys_sending_task, self.mic_sending_task) if task is not None),
        }
        for task in owned_tasks:
            task.cancel()
        if owned_tasks:
            await asyncio.gather(*owned_tasks, return_exceptions=True)
        self._queue_tasks.clear()
        self.sys_sending_task = None
        self.mic_sending_task = None

        for stream_attr in ("stream_sys", "stream_mic"):
            stream = getattr(self, stream_attr, None)
            if stream:
                stream.stop_stream()
                stream.close()
        if self.p:
            self.p.terminate()
