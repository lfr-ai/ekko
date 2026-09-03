"""Tests for live transcript SSE serialization."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest

from ekko.application.services import TranscriptBroadcaster
from ekko.core.value_objects import TranscriptSegment
from ekko.presentation.api.routes.transcript import transcript_stream


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transcript_stream_yields_typed_event() -> None:
    """Serialize a broadcast transcript as one named SSE event."""
    broadcaster = TranscriptBroadcaster()
    stream = transcript_stream(broadcaster)
    pending_event = asyncio.create_task(anext(stream))
    await asyncio.sleep(0)

    broadcaster.publish(
        TranscriptSegment(
            text="hello",
            source="system",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        )
    )
    event = await pending_event
    await stream.aclose()

    assert event.event == "transcript"
    assert event.data.text == "hello"
    assert event.data.source == "system"