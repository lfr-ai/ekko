"""FastAPI application lifespan management.

Extracted from app_factory to keep composition concerns separated.
Manages startup/shutdown of audio, STT, and background services.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from queue import Empty
from typing import TYPE_CHECKING

from ekko.core.enums import AudioQueueName, QueueName
from ekko.infrastructure.concurrency.queue_manager import QueueManager

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import FastAPI

    from ekko.config.settings import BaseAppConfig

logger = logging.getLogger(__name__)


# ── Lifespan helpers ─────────────────────────────────────────


async def _start_audio_servers(
    app: FastAPI,
    *,
    settings: BaseAppConfig,
    host: str,
) -> None:
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
        lambda r, w: _audio_receiver(r, w, AudioQueueName.SYSTEM),
        host,
        sys_port,
    )
    app.state.mic_server = await asyncio.start_server(
        lambda r, w: _audio_receiver(r, w, AudioQueueName.MICROPHONE),
        host,
        mic_port,
    )
    logger.info(
        "Audio servers listening on %s:%s (sys) and %s:%s (mic)",
        host,
        sys_port,
        host,
        mic_port,
    )


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
    if hasattr(app.state, "controller"):
        await app.state.controller.stop()
    if hasattr(app.state, "stt"):
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
async def create_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Composition root lifespan. Uses Container for DI."""
    container = app.state.container
    settings = container.settings

    # Queue manager
    app.state.queue_manager = QueueManager()
    try:
        app.state.queue_manager.create_queue(QueueName.TRANSCRIPTS)
    except Exception as e:
        logger.debug(
            "Queue %r already present or failed to create: %s",
            QueueName.TRANSCRIPTS,
            e,
        )

    # CrewAI / HMAS service (PII anonymization wired internally)
    app.state.crewai_service = container.crewai_service

    # Audio controller (skip if disabled, e.g., in containers)
    if not settings.disable_audio:
        app.state.controller = container.audio_controller

    # STT with transcript bridge callback
    def _on_transcript(transcript):
        try:
            app.state.queue_manager.put_in_queue(QueueName.TRANSCRIPTS, transcript)
        except Exception as e:
            logger.debug("Failed to put transcript into queue: %s", e)

    from ekko.infrastructure.adapters.stt_adapter import create_azure_speech_stt

    app.state.stt = create_azure_speech_stt(settings=settings, on_transcript=_on_transcript)

    if not settings.disable_audio:
        await app.state.stt.ensure_queue(AudioQueueName.SYSTEM)
        await app.state.stt.ensure_queue(AudioQueueName.MICROPHONE)
        await app.state.stt.start()

        await _start_audio_servers(app, settings=settings, host=settings.host)
        await app.state.controller.start()
        await _start_transcript_bridge(app)

    yield

    await _shutdown_services(app)
