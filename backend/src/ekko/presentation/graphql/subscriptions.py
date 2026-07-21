"""GraphQL subscription resolvers."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator  # noqa: TC003 — Strawberry needs runtime access
from datetime import UTC, datetime
from typing import Final

import strawberry
from strawberry.types import Info

from ekko.config.settings import get_settings
from ekko.presentation.graphql.pii_policy import PIIPolicySettings, render_subscription_text
from ekko.presentation.graphql.types import TranscriptType

_SUBSCRIPTION_IDLE_SLEEP_SECONDS: Final[float] = 1.0
_TRANSCRIPT_QUEUE_WAIT_TIMEOUT_SECONDS: Final[float] = 1.0


def _to_iso8601_utc(*, value: datetime) -> str:
    """Convert datetime value to stable UTC ISO-8601 string."""
    normalized = value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
    return normalized.isoformat().replace("+00:00", "Z")


def _resolve_app_state(*, info: Info) -> object | None:
    """Resolve FastAPI app.state through Strawberry request context."""
    context = info.context
    if context is None:
        return None
    request = context.get("request")
    if request is None:
        return None
    app = getattr(request, "app", None)
    if app is None:
        return None
    return getattr(app, "state", None)


def _maybe_scrub_text(*, info: Info, text: str) -> str:
    """Apply PII anonymization when anonymizer exists in request context."""
    context = info.context
    if context is None:
        return text
    anonymizer = context.get("pii_anonymizer")
    settings = get_settings()
    return render_subscription_text(
        text=text,
        anonymizer=anonymizer,
        settings=PIIPolicySettings(profile=settings.pii_policy_profile),
    )


def _to_transcript_type(*, info: Info, item: object) -> TranscriptType:
    """Map queued transcript payloads into GraphQL TranscriptType."""
    if isinstance(item, dict):
        payload = {str(key): value for key, value in item.items()}
        text_value = str(payload.get("text", ""))
        source_value = str(payload.get("source", "unknown"))
        timestamp_raw = payload.get("timestamp")
        if isinstance(timestamp_raw, datetime):
            timestamp_value = _to_iso8601_utc(value=timestamp_raw)
        else:
            timestamp_value = str(timestamp_raw or "")
        return TranscriptType(
            text=_maybe_scrub_text(info=info, text=text_value),
            source=source_value,
            timestamp=timestamp_value,
        )

    text_attr = getattr(item, "text", "")
    source_attr = getattr(item, "source", "unknown")
    timestamp_attr = getattr(item, "timestamp", None)
    created_at_attr = getattr(item, "created_at", None)

    timestamp_value = ""
    if isinstance(timestamp_attr, datetime):
        timestamp_value = _to_iso8601_utc(value=timestamp_attr)
    elif isinstance(created_at_attr, datetime):
        timestamp_value = _to_iso8601_utc(value=created_at_attr)

    return TranscriptType(
        text=_maybe_scrub_text(info=info, text=str(text_attr)),
        source=str(source_attr),
        timestamp=timestamp_value,
    )


@strawberry.type
class Subscription:
    """Root subscription type for real-time events."""

    @strawberry.subscription
    async def transcript_stream(self, info: Info, source: str = "all") -> AsyncGenerator[TranscriptType, None]:
        """Stream real-time transcript updates.

        Connects to the application's transcript queue and yields new
        segments as they arrive from the STT pipeline.
        """
        app_state = _resolve_app_state(info=info)
        transcript_queue = None if app_state is None else getattr(app_state, "async_transcript_queue", None)

        if transcript_queue is None:
            while True:
                await asyncio.sleep(_SUBSCRIPTION_IDLE_SLEEP_SECONDS)
                yield TranscriptType(
                    text="[waiting for transcript queue]",
                    source=source,
                    timestamp="",
                )

        while True:
            try:
                payload = await asyncio.wait_for(
                    transcript_queue.get(),
                    timeout=_TRANSCRIPT_QUEUE_WAIT_TIMEOUT_SECONDS,
                )
            except TimeoutError:
                await asyncio.sleep(_SUBSCRIPTION_IDLE_SLEEP_SECONDS)
                continue

            transcript = _to_transcript_type(info=info, item=payload)
            if source not in ("all", transcript.source):
                continue

            task_done = getattr(transcript_queue, "task_done", None)
            if callable(task_done):
                task_done()
            yield transcript

    @strawberry.subscription
    async def agent_status(self, info: Info) -> AsyncGenerator[str, None]:
        """Stream agent execution status updates."""
        while True:
            await asyncio.sleep(_SUBSCRIPTION_IDLE_SLEEP_SECONDS)
            app_state = _resolve_app_state(info=info)
            if app_state is None:
                yield "unavailable"
                continue

            bridge_task = getattr(app_state, "_transcript_bridge_task", None)
            if bridge_task is None:
                yield "initializing"
                continue
            if bridge_task.cancelled() or bridge_task.done():
                yield "degraded"
                continue
            yield "running"

    @strawberry.subscription
    async def conversation_events(self, conversation_id: str) -> AsyncGenerator[str, None]:
        """Stream events for a specific conversation."""
        while True:
            await asyncio.sleep(_SUBSCRIPTION_IDLE_SLEEP_SECONDS)
            heartbeat_at = _to_iso8601_utc(value=datetime.now(UTC))
            yield f"heartbeat:{conversation_id}:{heartbeat_at}"
