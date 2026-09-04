"""Tests for live transcript broadcasting."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ekko.application.services import TranscriptBroadcaster
from ekko.core.value_objects import TranscriptSegment


@pytest.mark.unit
@pytest.mark.asyncio
async def test_publish_delivers_each_segment_to_every_subscriber() -> None:
    """Fan out one transcript without destructive subscriber competition."""
    broadcaster = TranscriptBroadcaster()
    segment = TranscriptSegment(text="hello", source="microphone", timestamp=datetime.now(UTC))

    async with broadcaster.subscribe() as first, broadcaster.subscribe() as second:
        broadcaster.publish(segment)

        assert await first.get() == segment
        assert await second.get() == segment


@pytest.mark.unit
@pytest.mark.asyncio
async def test_publish_drops_oldest_segment_for_slow_subscriber() -> None:
    """Bound memory while keeping the newest live transcript."""
    broadcaster = TranscriptBroadcaster(queue_size=1)
    old = TranscriptSegment(text="old")
    new = TranscriptSegment(text="new")

    async with broadcaster.subscribe() as queue:
        broadcaster.publish(old)
        broadcaster.publish(new)

        assert await queue.get() == new