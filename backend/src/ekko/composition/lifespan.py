"""FastAPI application lifespan management.

Extracted from app_factory to keep composition concerns separated.
Manages startup/shutdown of audio, STT, and background services.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager, suppress
from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING

from ekko.core.enums import AudioQueueName

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import FastAPI
    from redis.asyncio import Redis

    from ekko.config.base import BaseAppConfig
    from ekko.core.value_objects import TranscriptSegment

_logger = logging.getLogger(__name__)

_SYSTEM_AUDIO_PORT_OFFSET = 1
_MICROPHONE_PORT_OFFSET = 2
_PCM16_BYTES_PER_SAMPLE = 2
_TRANSCRIPT_REDIS_CHANNEL = "ekko:transcripts"


# ── Lifespan helpers ─────────────────────────────────────────


async def _start_audio_servers(
    app: FastAPI,
    *,
    settings: BaseAppConfig,
    host: str,
) -> None:
    """Start TCP audio receiver servers for system and microphone audio."""
    sys_port = settings.audio_streamer_tcp_port + _SYSTEM_AUDIO_PORT_OFFSET
    mic_port = settings.audio_streamer_tcp_port + _MICROPHONE_PORT_OFFSET

    async def _audio_receiver(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, queue_name: str) -> None:
        try:
            while True:
                data = await reader.read(
                    settings.audio_frames_per_buffer * _PCM16_BYTES_PER_SAMPLE * settings.audio_channels
                )
                if not data:
                    break
                await app.state.stt.accept_bytes(queue_name, data)
        except Exception as exc:  # noqa: BLE001  # receiver logs and exits on any stream error
            _logger.debug("Audio receiver error", extra={"queue_name": queue_name, "error": str(exc)})
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as exc:  # noqa: BLE001  # best-effort writer cleanup
                _logger.debug("Failed to close audio writer", extra={"error": str(exc)})

    app.state.sys_server = await asyncio.start_server(
        lambda r, w: _audio_receiver(r, w, AudioQueueName.SYSTEM),
        host,
        sys_port,
    )
    app.state.mic_server = await asyncio.start_server(
        lambda r, w: _audio_receiver(r, w, AudioQueueName.MICROPHONE),
        host,
        mic_port,
    )
    _logger.info(
        "Audio servers listening",
        extra={
            "host": host,
            "system_port": sys_port,
            "microphone_port": mic_port,
        },
    )


async def _close_audio_servers(app: FastAPI) -> None:
    """Close any audio TCP servers that were started."""
    for server_name in ("sys_server", "mic_server"):
        server = getattr(app.state, server_name, None)
        if server is not None:
            server.close()
            await server.wait_closed()
            setattr(app.state, server_name, None)


async def _shutdown_services(app: FastAPI) -> None:
    """Gracefully stop audio controller, STT, and TCP servers."""
    if hasattr(app.state, "controller"):
        await app.state.controller.stop()
    if hasattr(app.state, "stt"):
        await app.state.stt.stop()

    await _close_audio_servers(app)


async def _start_audio_runtime(*, app: FastAPI, settings: BaseAppConfig) -> None:
    """Start audio runtime components and degrade gracefully on startup failures."""
    try:
        await app.state.stt.start()
        await app.state.stt.ensure_queue(AudioQueueName.SYSTEM)
        await app.state.stt.ensure_queue(AudioQueueName.MICROPHONE)
        await _start_audio_servers(app, settings=settings, host=settings.host)
        await app.state.controller.start()
    except OSError as exc:
        await _close_audio_servers(app)
        _logger.warning("Audio runtime disabled", extra={"reason": "startup_os_error"}, exc_info=exc)
    except Exception as exc:  # audio runtime is optional; degrade gracefully
        await _close_audio_servers(app)
        _logger.warning("Audio runtime disabled", extra={"reason": "startup_error"}, exc_info=exc)


# ── Cross-replica transcript relay (Redis Pub/Sub) ──────────


def _serialize_transcript(segment: TranscriptSegment) -> str:
    """Encode a transcript segment for cross-replica Redis fan-out."""
    payload = asdict(segment)
    payload["timestamp"] = segment.timestamp.isoformat()
    return json.dumps(payload)


def _deserialize_transcript(raw: bytes | str) -> TranscriptSegment:
    """Decode a transcript segment received from another replica."""
    from ekko.core.value_objects import TranscriptSegment as _TranscriptSegment

    payload = json.loads(raw)
    payload["timestamp"] = datetime.fromisoformat(payload["timestamp"])
    return _TranscriptSegment(**payload)


async def _publish_transcript_to_redis(redis_client: Redis, segment: TranscriptSegment) -> None:
    """Best-effort fan-out of one transcript to every other replica."""
    try:
        await redis_client.publish(_TRANSCRIPT_REDIS_CHANNEL, _serialize_transcript(segment))
    except Exception as exc:  # noqa: BLE001  # cross-replica fan-out is best-effort
        _logger.debug("Redis transcript publish failed", extra={"error": str(exc)})


async def _relay_remote_transcripts(app: FastAPI, redis_client: Redis) -> None:
    """Forward transcripts published by other replicas to local subscribers."""
    async with redis_client.pubsub() as pubsub:
        await pubsub.subscribe(_TRANSCRIPT_REDIS_CHANNEL)
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=None)
            if message is not None:
                app.state.transcript_broadcaster.publish(_deserialize_transcript(message["data"]))


async def _stop_transcript_relay(relay_task: asyncio.Task[None] | None, redis_client: Redis | None) -> None:
    """Cancel the relay task and release the Redis connection."""
    if relay_task is not None:
        relay_task.cancel()
        with suppress(asyncio.CancelledError):
            await relay_task
    if redis_client is not None:
        await redis_client.aclose()


# ── Lifespan ─────────────────────────────────────────────────


@asynccontextmanager
async def create_lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Composition root lifespan. Uses Container for DI."""
    container = app.state.container
    settings = container.settings

    redis_client: Redis | None = getattr(app.state, "redis_client", None)
    relay_task = asyncio.create_task(_relay_remote_transcripts(app, redis_client)) if redis_client is not None else None

    try:
        if settings.disable_audio:
            yield
            return

        app.state.controller = container.audio_controller
        background_tasks: set[asyncio.Task[None]] = set()

        # STT with transcript bridge callback
        def _on_transcript(transcript: TranscriptSegment) -> None:
            app.state.transcript_broadcaster.publish(transcript)
            if redis_client is not None:
                task = asyncio.create_task(_publish_transcript_to_redis(redis_client, transcript))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)

        app.state.stt = container.build_stt_service(on_transcript=_on_transcript)
        await _start_audio_runtime(app=app, settings=settings)

        yield
    finally:
        await _shutdown_services(app)
        await _stop_transcript_relay(relay_task, redis_client)
