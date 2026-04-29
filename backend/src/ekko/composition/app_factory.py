"""Application factory that wires the FastAPI app with routers and lifespan."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
from queue import Empty

from fastapi import FastAPI

from ekko import __version__
from ekko.composition.container import Container
from ekko.config.logging_config import configure_logging
from ekko.config.settings import get_settings
from ekko.core.enums import AudioQueueName, QueueName
from ekko.infrastructure.concurrency.queue_manager import QueueManager
from ekko.presentation.api.routes import auth_router, health_router, stream_router

logger = logging.getLogger(__name__)


# ── Lifespan helpers ─────────────────────────────────────────


async def _start_audio_servers(app: FastAPI, settings, host: str) -> None:
    """Start TCP audio receiver servers for system and microphone audio."""
    sys_port = settings.audio_streamer_tcp_port + 1
    mic_port = settings.audio_streamer_tcp_port + 2

    async def _audio_receiver(reader, writer, queue_name: str):
        try:
            while True:
                data = await reader.read(settings.audio_frames_per_buffer * 2 * settings.audio_channels)
                if not data:
                    break
                await app.state.stt.accept_bytes(queue_name, data)
        except Exception as e:
            logger.debug("Audio receiver error for %s: %s", queue_name, e)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logger.debug("Failed to close writer: %s", e)

    app.state.sys_server = await asyncio.start_server(
        lambda r, w: _audio_receiver(r, w, AudioQueueName.SYSTEM), host, sys_port,
    )
    app.state.mic_server = await asyncio.start_server(
        lambda r, w: _audio_receiver(r, w, AudioQueueName.MICROPHONE), host, mic_port,
    )
    logger.info("Audio servers listening on %s:%s (sys) and %s:%s (mic)", host, sys_port, host, mic_port)


async def _start_transcript_bridge(app: FastAPI) -> None:
    """Start background task draining transcripts from sync queue to async queue."""
    app.state.async_transcript_queue = asyncio.Queue()

    async def _drain():
        qm = app.state.queue_manager
        q = qm.get_queue(QueueName.TRANSCRIPTS)
        try:
            while True:
                try:
                    transcript = await asyncio.to_thread(q.get, True, 1)
                except Empty:
                    await asyncio.sleep(0.1)
                    continue
                try:
                    await app.state.async_transcript_queue.put(transcript)
                finally:
                    try:
                        q.task_done()
                    except Exception as e:
                        logger.debug("Failed to task_done on queue: %s", e)
        except asyncio.CancelledError:
            return

    app.state._transcript_bridge_task = asyncio.create_task(_drain())


async def _shutdown_services(app: FastAPI) -> None:
    """Gracefully stop audio controller, STT, and transcript bridge."""
    await app.state.controller.stop()
    await app.state.stt.stop()

    task = getattr(app.state, "_transcript_bridge_task", None)
    if task:
        task.cancel()
        try:
            await task
        except Exception as e:
            logger.debug("Transcript bridge task cancel/wait raised: %s", e)


# ── Lifespan ─────────────────────────────────────────────────


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Composition root lifespan. Uses Container for DI."""
    container = app.state.container
    settings = container.settings

    # Queue manager
    app.state.queue_manager = QueueManager()
    try:
        app.state.queue_manager.create_queue(QueueName.TRANSCRIPTS)
    except Exception as e:
        logger.debug("Queue %r already present or failed to create: %s", QueueName.TRANSCRIPTS, e)

    # CrewAI / HMAS service (PII anonymization wired internally)
    app.state.crewai_service = container.crewai_service

    # Audio controller
    app.state.controller = container.audio_controller

    # STT with transcript bridge callback
    def _on_transcript(transcript):
        try:
            app.state.queue_manager.put_in_queue(QueueName.TRANSCRIPTS, transcript)
        except Exception as e:
            logger.debug("Failed to put transcript into queue: %s", e)

    from ekko.infrastructure.adapters.stt_adapter import create_faster_whisper_stt

    app.state.stt = create_faster_whisper_stt(
        settings=settings, on_transcript=_on_transcript
    )

    await app.state.stt.ensure_queue(AudioQueueName.SYSTEM)
    await app.state.stt.ensure_queue(AudioQueueName.MICROPHONE)
    await app.state.stt.start()

    await _start_audio_servers(app, settings, settings.host)
    await app.state.controller.start()
    await _start_transcript_bridge(app)

    yield

    await _shutdown_services(app)


# ── Middleware wiring ────────────────────────────────────────


def _register_middleware(app: FastAPI, container: Container) -> None:
    """Register all middleware in correct order (last added = first executed)."""
    from ekko.presentation.api.middleware import (
        AuthenticationMiddleware,
        RequestIdMiddleware,
        SecurityHeadersMiddleware,
        TimingMiddleware,
        register_error_handlers,
        setup_cors,
    )

    # Error handlers (exception → HTTP response mapping)
    register_error_handlers(app)

    # CORS
    setup_cors(app, settings=container.settings)

    # Middleware stack — order: Request ID → Security → Timing → Auth
    # (added in reverse because Starlette executes last-added first)
    app.add_middleware(
        AuthenticationMiddleware,
        environment=container.settings.environment,
        jwt_adapter=container.jwt_adapter,
    )
    app.add_middleware(TimingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)


# ── Factory ──────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Create and return a FastAPI application wired with routers."""
    configure_logging()
    settings = get_settings()
    container = Container(settings=settings)

    app = FastAPI(
        title="Ekko API",
        description="AI-powered voice assistant platform",
        version=__version__,
        lifespan=_lifespan,
    )

    # Store container on app state for access in lifespan and routes
    app.state.container = container

    # Register middleware
    _register_middleware(app, container)

    # REST routers
    app.include_router(health_router)
    app.include_router(stream_router)
    app.include_router(auth_router)

    # GraphQL router
    from ekko.presentation.graphql.router import graphql_router

    app.include_router(graphql_router, prefix="/graphql")

    return app
