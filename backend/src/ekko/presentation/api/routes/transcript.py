"""Server-sent event endpoint for live transcripts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse, ServerSentEvent

from ekko.application.services import TranscriptBroadcaster
from ekko.core.registry_constants import ROUTE_TRANSCRIPT_STREAM
from ekko.presentation.api.dependencies import get_transcript_broadcaster
from ekko.presentation.api.schemas.transcript import TranscriptResponse

if TYPE_CHECKING:
    from collections.abc import AsyncIterable

_TRANSCRIPT_TAG = "transcript"
_TRANSCRIPT_EVENT = "transcript"

router = APIRouter(tags=[_TRANSCRIPT_TAG])

type TranscriptBroadcasterDependency = Annotated[
    TranscriptBroadcaster,
    Depends(get_transcript_broadcaster),
]


@router.get(ROUTE_TRANSCRIPT_STREAM, response_class=EventSourceResponse, response_model=None)
async def transcript_stream(
    broadcaster: TranscriptBroadcasterDependency,
) -> AsyncIterable[ServerSentEvent]:
    """Stream live transcript segments."""
    async with broadcaster.subscribe() as queue:
        while True:
            segment = await queue.get()
            yield ServerSentEvent(
                event=_TRANSCRIPT_EVENT,
                data=TranscriptResponse(
                    text=segment.text,
                    source=segment.source,
                    timestamp=segment.timestamp,
                ),
            )
