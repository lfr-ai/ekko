"""Tests for application lifespan composition."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, final

import pytest
from fastapi import FastAPI

from ekko.application.services import TranscriptBroadcaster
from ekko.composition.lifespan import (
    _TRANSCRIPT_REDIS_CHANNEL,
    _deserialize_transcript,
    _publish_transcript_to_redis,
    _relay_remote_transcripts,
    _serialize_transcript,
    _stop_transcript_relay,
    create_lifespan,
)
from ekko.config.base import BaseAppConfig
from ekko.core.value_objects import TranscriptSegment

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, kw_only=True, slots=True)
class DisabledAudioContainer:
    """Container stub that exposes only disabled-audio settings."""

    settings: BaseAppConfig

    @property
    def audio_controller(self) -> object:
        """Reject unexpected audio-controller construction."""
        msg = "audio controller must not be constructed when audio is disabled"
        raise AssertionError(msg)


@final
@dataclass(kw_only=True, slots=True)
class _FakePublishRedisClient:
    """Fake Redis client recording (or rejecting) ``publish`` calls."""

    should_raise: bool = False
    published: list[tuple[str, str]] = field(default_factory=list)

    async def publish(self, channel: str, message: str) -> None:
        """Record the publish call, or simulate a connection failure."""
        if self.should_raise:
            msg = "connection refused"
            raise ConnectionError(msg)
        self.published.append((channel, message))


@final
class _FakePubSub:
    """Fake ``redis.asyncio.Redis.pubsub()`` result: one queued message, then blocks."""

    def __init__(self, messages: list[dict[str, object]]) -> None:
        self._messages = list(messages)
        self.subscribed_channels: list[str] = []

    async def subscribe(self, channel: str) -> None:
        """Record the subscribed channel."""
        self.subscribed_channels.append(channel)

    async def get_message(
        self,
        *,
        ignore_subscribe_messages: bool,
        timeout: float | None,  # noqa: ASYNC109  # mirrors redis-py's own PubSub.get_message signature
    ) -> dict[str, object] | None:
        """Return the next queued message, then block as a real idle subscription would."""
        if self._messages:
            return self._messages.pop(0)
        await asyncio.sleep(3600)
        return None

    async def __aenter__(self) -> _FakePubSub:
        """Enter the async pub/sub context, mirroring redis-py's own PubSub."""
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        """Exit the async pub/sub context; nothing to release in the fake."""
        return


@final
@dataclass(kw_only=True, slots=True)
class _FakeRelayRedisClient:
    """Fake Redis client exposing only the pub/sub + disposal surface the relay uses."""

    messages: list[dict[str, object]] = field(default_factory=list)
    closed: bool = False
    pubsub_obj: _FakePubSub = field(init=False)

    def __post_init__(self) -> None:
        self.pubsub_obj = _FakePubSub(self.messages)

    def pubsub(self) -> _FakePubSub:
        """Return the fake pub/sub subscription."""
        return self.pubsub_obj

    async def aclose(self) -> None:
        """Record that the connection was released."""
        self.closed = True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_lifespan_when_audio_disabled_skips_audio_and_stt_construction(tmp_path: Path) -> None:
    """Start the application without native audio or speech dependencies."""
    settings = BaseAppConfig(
        disable_audio=True,
        database_path=str(tmp_path / "ekko.db"),
    )
    app = FastAPI()
    app.state.container = DisabledAudioContainer(settings=settings)

    async with create_lifespan(app):
        assert not hasattr(app.state, "queue_manager")
        assert not hasattr(app.state, "controller")
        assert not hasattr(app.state, "stt")


# ── Cross-replica transcript relay (Redis Pub/Sub) ──────────


@pytest.mark.unit
def test_serialize_transcript_round_trips_through_deserialize() -> None:
    """Preserve every field across the Redis wire format."""
    segment = TranscriptSegment(text="hello", start_seconds=1.5, end_seconds=2.5, confidence=0.9, source="system")

    restored = _deserialize_transcript(_serialize_transcript(segment))

    assert restored == segment


@pytest.mark.unit
@pytest.mark.asyncio
async def test_publish_transcript_to_redis_publishes_serialized_payload() -> None:
    """Fan a locally-ingested segment out to the shared cross-replica channel."""
    redis_client = _FakePublishRedisClient()
    segment = TranscriptSegment(text="hello", source="microphone")

    await _publish_transcript_to_redis(redis_client, segment)

    assert redis_client.published == [(_TRANSCRIPT_REDIS_CHANNEL, _serialize_transcript(segment))]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_publish_transcript_to_redis_swallows_publish_failures() -> None:
    """Treat cross-replica fan-out as best-effort so a Redis outage never breaks ingest."""
    redis_client = _FakePublishRedisClient(should_raise=True)

    await _publish_transcript_to_redis(redis_client, TranscriptSegment(text="hello"))  # must not raise


@pytest.mark.unit
@pytest.mark.asyncio
async def test_relay_remote_transcripts_forwards_message_to_local_broadcaster() -> None:
    """Deliver a segment published by another replica to this replica's own subscribers."""
    segment = TranscriptSegment(text="from another replica", source="system")
    redis_client = _FakeRelayRedisClient(messages=[{"data": _serialize_transcript(segment)}])
    app = FastAPI()
    app.state.transcript_broadcaster = TranscriptBroadcaster()

    async with app.state.transcript_broadcaster.subscribe() as queue:
        relay_task = asyncio.create_task(_relay_remote_transcripts(app, redis_client))
        try:
            received = await asyncio.wait_for(queue.get(), timeout=1)
        finally:
            relay_task.cancel()
            with suppress(asyncio.CancelledError):
                await relay_task

    assert received == segment
    assert redis_client.pubsub_obj.subscribed_channels == [_TRANSCRIPT_REDIS_CHANNEL]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stop_transcript_relay_cancels_task_and_closes_client() -> None:
    """Release both the relay task and the Redis connection on shutdown."""
    redis_client = _FakeRelayRedisClient()
    relay_task = asyncio.create_task(asyncio.sleep(3600))

    await _stop_transcript_relay(relay_task, redis_client)

    assert relay_task.cancelled()
    assert redis_client.closed is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stop_transcript_relay_without_redis_is_a_no_op() -> None:
    """Skip disposal cleanly when no relay was ever started (Redis not configured)."""
    await _stop_transcript_relay(None, None)  # must not raise


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_lifespan_with_redis_starts_relay_and_disposes_client_on_exit(tmp_path: Path) -> None:
    """Wire the cross-replica relay task on startup and release Redis on shutdown."""
    settings = BaseAppConfig(disable_audio=True, database_path=str(tmp_path / "ekko.db"))
    redis_client = _FakeRelayRedisClient()
    app = FastAPI()
    app.state.container = DisabledAudioContainer(settings=settings)
    app.state.redis_client = redis_client

    async with create_lifespan(app):
        await asyncio.sleep(0)  # let the relay task start and subscribe
        assert redis_client.pubsub_obj.subscribed_channels == [_TRANSCRIPT_REDIS_CHANNEL]

    assert redis_client.closed is True
