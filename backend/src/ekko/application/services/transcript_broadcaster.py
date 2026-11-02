"""In-process broadcaster for live transcript segments."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from ekko.core.value_objects import TranscriptSegment

_SUBSCRIBER_QUEUE_SIZE = 100


@final
class TranscriptBroadcaster:
    """Broadcast each transcript segment to every active subscriber."""

    def __init__(self, *, queue_size: int = _SUBSCRIBER_QUEUE_SIZE):
        self._queue_size = queue_size
        self._subscribers: set[asyncio.Queue[TranscriptSegment]] = set()

    def publish(self, segment: TranscriptSegment) -> None:
        """Publish a transcript segment to all active subscribers."""
        for queue in tuple(self._subscribers):
            if queue.full():
                queue.get_nowait()
            queue.put_nowait(segment)

    @asynccontextmanager
    async def subscribe(self) -> AsyncGenerator[asyncio.Queue[TranscriptSegment]]:
        """Provide a bounded queue for one subscriber's lifetime."""
        queue: asyncio.Queue[TranscriptSegment] = asyncio.Queue(maxsize=self._queue_size)
        self._subscribers.add(queue)
        try:
            yield queue
        finally:
            self._subscribers.discard(queue)
