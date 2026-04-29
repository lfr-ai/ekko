"""GraphQL subscription resolvers."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator  # noqa: TC003 — Strawberry needs runtime access

import strawberry

from ekko.presentation.graphql.types import TranscriptType


@strawberry.type
class Subscription:
    """Root subscription type for real-time events."""

    @strawberry.subscription
    async def transcript_stream(self, source: str = "all") -> AsyncGenerator[TranscriptType, None]:
        """Stream real-time transcript updates.

        Connects to the application's transcript queue and yields new
        segments as they arrive from the STT pipeline.
        """
        # Placeholder: in production, this connects to the async transcript queue
        # from app.state.async_transcript_queue
        while True:
            await asyncio.sleep(1)
            yield TranscriptType(
                text="[waiting for transcript...]",
                source=source,
                timestamp="",
            )

    @strawberry.subscription
    async def agent_status(self) -> AsyncGenerator[str, None]:
        """Stream agent execution status updates."""
        while True:
            await asyncio.sleep(5)
            yield "idle"

    @strawberry.subscription
    async def conversation_events(self, conversation_id: str) -> AsyncGenerator[str, None]:
        """Stream events for a specific conversation."""
        while True:
            await asyncio.sleep(2)
            yield f"heartbeat:{conversation_id}"
