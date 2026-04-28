import logging

from voice.config.config import Config
from voice.core.protocols import STTService

logger = logging.getLogger(__name__)


class _StubSTT:
    """Lightweight STT stub used when faster-whisper/numpy aren't installed.

    Implements the minimal STTService protocol surface used by the app so tests
    and dev environments may run without heavy ML deps.
    """

    def __init__(self, cfg: Config, **kwargs):
        self.cfg = cfg
        from typing import Any, Dict

        # Map queue name -> asyncio.Queue (used for stub testing)
        self._queues: Dict[str, Any] = {}

    async def start(self) -> None:
        return

    async def stop(self) -> None:
        return

    async def ensure_queue(self, queue_name: str) -> None:
        if queue_name not in self._queues:
            import asyncio

            self._queues[queue_name] = asyncio.Queue()

    async def accept_bytes(self, queue_name: str, data: bytes) -> None:
        # place raw bytes into internal asyncio queue for possible inspection
        q = self._queues.get(queue_name)
        if q is not None:
            try:
                await q.put(data)
            except Exception as e:
                logger.debug("_StubSTT failed to put data into queue: %s", e)


def create_faster_whisper_stt(cfg: Config, **kwargs) -> STTService:
    """Factory to create an STTService. Prefer the real `FasterWhisperSTT` if available,
    otherwise return a stub to keep dev/test environments lightweight.
    """
    try:
        # Import lazily to avoid heavy ML deps during test collection
        from voice.infrastructure.stt.transcriber import FasterWhisperSTT

        return FasterWhisperSTT(cfg=cfg, **kwargs)
    except Exception:
        return _StubSTT(cfg=cfg, **kwargs)
