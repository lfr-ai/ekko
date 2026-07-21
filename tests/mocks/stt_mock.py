"""Mock STT adapter for testing."""

from __future__ import annotations

import asyncio
from typing import Any


class MockTranscript:
    """Mock transcript result matching FasterWhisperSTT.Transcript structure."""

    def __init__(
        self,
        stream_name: str,
        text: str,
        segments: list[Any] | None = None,
        info: Any | None = None,
    ) -> None:
        self.stream_name = stream_name
        self.text = text
        self.segments = segments or []
        self.info = info or {}


class MockSTTAdapter:
    """Mock STT adapter that returns predefined transcripts."""

    def __init__(self, transcript_text: str = "Test transcript") -> None:
        self.transcript_text = transcript_text
        self._running = False
        self._queues: dict[str, asyncio.Queue[bytes]] = {}
        self.on_transcript = None
        self.output_queue = None

    async def start(self) -> None:
        """Start the mock STT service."""
        self._running = True

    async def stop(self) -> None:
        """Stop the mock STT service."""
        self._running = False

    async def ensure_queue(self, queue_name: str) -> None:
        """Ensure queue exists for stream."""
        if queue_name not in self._queues:
            self._queues[queue_name] = asyncio.Queue()

    async def accept_bytes(self, queue_name: str, _data: bytes) -> None:
        """Accept audio bytes and immediately process."""
        if queue_name not in self._queues:
            await self.ensure_queue(queue_name)

        # Simulate processing by creating transcript
        transcript = MockTranscript(
            stream_name=queue_name,
            text=self.transcript_text,
            segments=[],
            info={},
        )

        # Call callback if provided
        if self.on_transcript is not None:
            maybe = self.on_transcript(transcript)
            if asyncio.iscoroutine(maybe):
                await maybe

        # Put in output queue if provided
        if self.output_queue is not None:
            await self.output_queue.put(transcript)


class FailingSTTAdapter(MockSTTAdapter):
    """Mock STT adapter that simulates failures."""

    async def accept_bytes(self, _queue_name: str, _data: bytes) -> None:
        """Simulate STT failure."""
        raise RuntimeError("STT processing failed")
