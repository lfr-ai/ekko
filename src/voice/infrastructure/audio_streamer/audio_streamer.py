import asyncio
from typing import Any, Optional

import pyaudiowpatch as pyaudio
from pyaudiowpatch import Stream

from voice.config.config import Config
from voice.utils.types_ import RecognitionMode


class AudioStreamer:
    """Stream system + mic audio to STT queues (in this setup, send over TCP)."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.running = False
        self.sending = False
        self.group: Optional[asyncio.TaskGroup] = None
        from typing import Any

        # PyAudio instance (lazy-created in _initialize)
        self.p: Any = None
        # Track send tasks for subprocess-to-main streaming
        self.sys_sending_task: asyncio.Task | None = None
        self.mic_sending_task: asyncio.Task | None = None

    def _get_sys_info(self) -> dict[str, Any]:
        self.mode = RecognitionMode.CUSTOMER
        return self.p.get_default_wasapi_loopback()

    def _get_mic_info(self) -> dict[str, Any]:
        self.mode = RecognitionMode.ADVISOR
        return self.p.get_default_input_device_info()

    def _create_stream(self, device_info: dict[str, Any]) -> Stream:
        return self.p.open(
            format=self.cfg.AUDIO_FORMAT,
            channels=device_info["maxInputChannels"],
            rate=int(device_info["defaultSampleRate"]),
            input=True,
            frames_per_buffer=self.cfg.AUDIO_FRAMES_PER_BUFFER,
            input_device_index=device_info["index"],
        )

    def _create_sys_stream(self):
        sys_info = self._get_sys_info()
        self.sys_name = sys_info["name"]
        self.stream_sys = self._create_stream(sys_info)

    def _create_mic_stream(self):
        mic_info = self._get_mic_info()
        self.mic_name = mic_info["name"]
        self.stream_mic = self._create_stream(mic_info)

    async def _stream_audio(self, stream: Stream, queue: asyncio.Queue):
        """Original audio streaming to a queue (unused in this setup)."""
        try:
            while self.running:
                if self.sending:
                    data = await asyncio.to_thread(stream.read, self.cfg.AUDIO_FRAMES_PER_BUFFER)
                    await queue.put(data)
                else:
                    await asyncio.sleep(self.cfg.SLEEP_DELAY_SECONDS)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in _stream_audio: {e}")

    def _initialize(self):
        # create a TaskGroup instance; we'll enter it in async start()
        self.group = asyncio.TaskGroup()
        self.p = pyaudio.PyAudio()
        self._create_sys_stream()
        self._create_mic_stream()

    async def start(
        self,
        sys_queue: Optional[asyncio.Queue] = None,
        mic_queue: Optional[asyncio.Queue] = None,
    ):
        """Start streamer tasks (opens devices)."""
        self._initialize()
        # Enter the TaskGroup context explicitly. Use a local variable to
        # convince type checkers that it's non-None.
        group = self.group
        if group is None:
            raise RuntimeError("Failed to create TaskGroup")
        assert group is not None
        await group.__aenter__()
        self.running = True
        # We do not create queue tasks here since streaming is sent via TCP
        if sys_queue is not None:
            group.create_task(self._stream_audio(self.stream_sys, sys_queue))
        if mic_queue is not None:
            group.create_task(self._stream_audio(self.stream_mic, mic_queue))

    def start_stream(self):
        """Begin sending audio frames (subprocess only)."""
        self.sending = True

    def pause_stream(self):
        """Stop sending audio frames."""
        self.sending = False

    async def stop(self):
        """Stop all streaming and cleanup."""
        self.sending = False
        self.running = False
        await self._cleanup()

    async def _cleanup(self):
        group = getattr(self, "group", None)
        if group is not None:
            for task in list(getattr(group, "_tasks", [])):
                task.cancel()
            try:
                await group.__aexit__(None, None, None)
            except Exception as e:
                print(f"Error while stopping AudioStreamer: {e}")
        for stream_attr in ("stream_sys", "stream_mic"):
            stream = getattr(self, stream_attr, None)
            if stream:
                stream.stop_stream()
                stream.close()
        if self.p:
            self.p.terminate()
