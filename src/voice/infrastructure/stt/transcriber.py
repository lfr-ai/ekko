from __future__ import annotations

import asyncio
import os
import tempfile
import wave
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Optional

from voice.config.config import Config
from voice.utils.logger import Logger

if TYPE_CHECKING:
    from numpy import ndarray

_np: Any = None
try:
    import numpy as _np
except Exception:  # pragma: no cover - optional runtime dependency
    _np = None

np: Any = _np

FasterWhisperModel: Any = None
try:
    from faster_whisper import WhisperModel as FasterWhisperModel
except Exception:  # pragma: no cover - optional runtime dependency
    FasterWhisperModel = None

cfg = Config()
logger = Logger.create(__name__, cfg.LOGS_DIR_PATH / "stt.logs")


@dataclass
class Transcript:
    stream_name: str
    text: str
    segments: Any
    info: Any


class FasterWhisperSTT:
    """Pseudo-live STT component based on faster-whisper."""

    def __init__(
        self,
        cfg: Config,
        model_name: str = "small",
        device: Optional[str] = None,
        compute_type: Optional[str] = None,
        batch_seconds: float = 5.0,
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None,
        language: str = "da",
        on_transcript: Optional[Callable[[Transcript], Any]] = None,
        output_queue: Optional[asyncio.Queue[Any]] = None,
    ) -> None:
        self.cfg = cfg
        self.model_name = model_name
        self.device = device or getattr(cfg, "STT_DEVICE", "cpu")
        # ctranslate2/Whisper does not accept None for compute_type; ensure a valid default
        self.compute_type = compute_type if compute_type is not None else getattr(cfg, "STT_COMPUTE_TYPE", "default")
        self.batch_seconds = float(batch_seconds)
        self.sample_rate = (
            sample_rate or getattr(cfg, "AUDIO_SAMPLE_RATE", None) or getattr(cfg, "SAMPLE_RATE", None) or 48000
        )
        self.channels = channels or getattr(cfg, "AUDIO_CHANNELS", None) or 2
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
                    self._model = FasterWhisperModel(
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
        if np is None:
            raise RuntimeError("numpy is required for STT processing")

        arr: ndarray[Any, Any] = np.frombuffer(raw_bytes, dtype=np.int16)
        if channels > 1:
            n_frames = arr.shape[0] // channels
            arr = arr[: n_frames * channels]
            arr = arr.reshape(-1, channels)
            mono = arr.astype(np.int32).mean(axis=1).astype(np.int16)
        else:
            mono = arr

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_name = temp.name
        temp.close()

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
            try:
                os.remove(temp_path)
            except OSError:
                pass
