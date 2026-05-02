from __future__ import annotations

import asyncio
import contextlib
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from collections.abc import Callable

from ekko.config.settings import BaseAppConfig, get_settings
from ekko.utils.logger import Logger

# faster-whisper is an optional runtime dependency; import only when available.
FasterWhisperModel: object | None
try:
    from faster_whisper import WhisperModel as _FasterWhisperModel

    FasterWhisperModel = _FasterWhisperModel
except Exception:  # pragma: no cover - optional runtime dependency
    FasterWhisperModel = None

_settings = get_settings()
logger = Logger.create(__name__, _settings.logs_dir_path / "stt.logs")


@dataclass(slots=True)
class Transcript:
    stream_name: str
    text: str
    segments: Any
    info: Any


class FasterWhisperSTT:
    """Pseudo-live STT component based on faster-whisper."""

    def __init__(
        self,
        settings: BaseAppConfig,
        model_name: str = "small",
        device: str | None = None,
        compute_type: str | None = None,
        batch_seconds: float = 5.0,
        sample_rate: int | None = None,
        channels: int | None = None,
        language: str = "da",
        on_transcript: Callable[[Transcript], Any] | None = None,
        output_queue: asyncio.Queue[Any] | None = None,
    ) -> None:
        self.settings = settings
        self.model_name = model_name
        self.device = device or settings.stt_device
        self.compute_type = compute_type or settings.stt_compute_type
        self.batch_seconds = float(batch_seconds)
        self.sample_rate = sample_rate or settings.audio_sample_rate
        self.channels = channels or settings.audio_channels
        self.language = language
        self.on_transcript = on_transcript
        self.output_queue = output_queue

        self._queues: dict[str, asyncio.Queue[bytes]] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._model: Any = None
        self._running = False
        self._model_lock = asyncio.Lock()

    async def start(self) -> None:
        if FasterWhisperModel is None:
            raise RuntimeError("faster-whisper is not installed or failed to import")

        async with self._model_lock:
            if self._model is None:
                try:
                    model_cls = cast("type[object]", FasterWhisperModel)
                    self._model = model_cls(
                        self.model_name,
                        device=self.device,
                        compute_type=self.compute_type,
                    )
                except Exception:
                    logger.exception("Failed to load model")
                    raise

        self._running = True
        for queue_name in list(self._queues.keys()):
            await self._ensure_task(queue_name)

    async def stop(self) -> None:
        self._running = False
        tasks = list(self._tasks.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()

        async with self._model_lock:
            self._model = None

    async def ensure_queue(self, queue_name: str) -> None:
        if queue_name not in self._queues:
            self._queues[queue_name] = asyncio.Queue()
        await self._ensure_task(queue_name)

    async def _ensure_task(self, queue_name: str) -> None:
        if not self._running or queue_name in self._tasks:
            return
        self._tasks[queue_name] = asyncio.create_task(
            self._worker(queue_name),
            name=f"stt-worker-{queue_name}",
        )

    async def accept_bytes(self, queue_name: str, data: bytes) -> None:
        if queue_name not in self._queues:
            await self.ensure_queue(queue_name)
        await self._queues[queue_name].put(data)

    async def _worker(self, queue_name: str) -> None:
        queue = self._queues[queue_name]
        try:
            while self._running:
                await asyncio.sleep(self.batch_seconds)
                raw = b"".join(self._collect_chunks(queue))
                if len(raw) < 1024:
                    continue

                segs, info, text = await asyncio.to_thread(
                    self._process_raw_and_transcribe,
                    raw,
                )
                transcript = Transcript(
                    stream_name=queue_name,
                    text=text,
                    segments=segs,
                    info=info,
                )

                if self.on_transcript is not None:
                    maybe = self.on_transcript(transcript)
                    if asyncio.iscoroutine(maybe):
                        await maybe

                if self.output_queue is not None:
                    await self.output_queue.put(transcript)
        except asyncio.CancelledError:
            return
        except Exception:
            logger.exception("Unhandled exception in STT worker for %s", queue_name)
        finally:
            self._tasks.pop(queue_name, None)

    def _collect_chunks(self, queue: asyncio.Queue[bytes]) -> list[bytes]:
        chunks: list[bytes] = []
        while not queue.empty():
            try:
                chunks.append(queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return chunks

    @staticmethod
    def _raw_pcm_bytes_to_wav_file(
        raw_bytes: bytes,
        sample_rate: int,
        channels: int,
    ) -> str:
        try:
            import numpy as np  # noqa: PLC0415
        except Exception as err:  # pragma: no cover - optional runtime dependency
            raise RuntimeError("numpy is required for STT processing") from err

        arr = np.frombuffer(raw_bytes, dtype=np.int16)
        if channels > 1:
            n_frames = arr.shape[0] // channels
            arr = arr[: n_frames * channels]
            arr = arr.reshape(-1, channels)
            mono = arr.astype(np.int32).mean(axis=1).astype(np.int16)
        else:
            mono = arr

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            temp_name = temp.name

        with wave.open(temp_name, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(int(sample_rate))
            wav_file.writeframes(mono.tobytes())

        return temp_name

    def _process_raw_and_transcribe(self, raw: bytes) -> tuple[list[Any], Any, str]:
        temp_path = self._raw_pcm_bytes_to_wav_file(raw, self.sample_rate, self.channels)

        if self._model is None:
            raise RuntimeError("Model not loaded")

        try:
            segments, info = self._model.transcribe(temp_path, language=self.language)
            segs = list(segments) if hasattr(segments, "__iter__") else []
            text = "".join([getattr(seg, "text", str(seg)) for seg in segs])
            return segs, info, text
        finally:
            with contextlib.suppress(OSError):
                Path(temp_path).unlink()
