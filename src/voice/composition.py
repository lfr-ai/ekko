import asyncio
import logging
from contextlib import asynccontextmanager
from queue import Empty
from typing import AsyncGenerator

from fastapi import FastAPI

from voice.config.config import Config
from voice.config.logging_config import configure_logging
from voice.infrastructure.adapters.audio_streamer_adapter import (
    create_audio_streamer_controller,
)

# Import adapters lazily in create_app() to avoid hard import-time dependency on
# optional heavy libraries such as LangChain. This keeps tests and lightweight
# commands fast when the ML stack is not installed.
from voice.infrastructure.adapters.stt_adapter import create_faster_whisper_stt
from voice.managers.queue_manager import QueueManager

cfg = Config()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Minimal composition root lifespan. Uses adapter factories to satisfy core Protocols."""
    app.state.queue_manager = QueueManager()
    # prepare synchronous queues for consumers (transcripts or other messages)
    try:
        app.state.queue_manager.create_queue("transcripts")
    except Exception as e:
        logger.debug("Queue 'transcripts' already present or failed to create: %s", e)
    # create concrete implementations via infrastructure adapters
    app.state.controller = create_audio_streamer_controller(cfg)
    # wire STT with a callback that forwards transcripts into the sync QueueManager

    def _on_transcript(transcript):
        try:
            app.state.queue_manager.put_in_queue("transcripts", transcript)
        except Exception as e:
            # avoid crashing the event loop on queue errors
            logger.debug("Failed to put transcript into queue: %s", e)

    app.state.stt = create_faster_whisper_stt(
        cfg=cfg, model_name="small", batch_seconds=5, on_transcript=_on_transcript
    )

    await app.state.stt.ensure_queue("sys-queue")
    await app.state.stt.ensure_queue("mic-queue")
    await app.state.stt.start()

    # Start local servers to receive audio from subprocess
    host = cfg.HOST
    # Use command port +1/+2 for audio streams
    sys_port = cfg.AUDIO_STREAMER_TCP_PORT + 1
    mic_port = cfg.AUDIO_STREAMER_TCP_PORT + 2

    async def _audio_receiver(reader, writer, queue_name: str):
        try:
            while True:
                data = await reader.read(
                    cfg.AUDIO_FRAMES_PER_BUFFER * 2 * getattr(cfg, "AUDIO_CHANNELS", 2)
                )
                if not data:
                    break
                await app.state.stt.accept_bytes(queue_name, data)
        except Exception as e:
            # swallow errors to keep server running
            logger.debug("Audio receiver error for %s: %s", queue_name, e)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logger.debug("Failed to close writer: %s", e)

    app.state.sys_server = await asyncio.start_server(
        lambda r, w: _audio_receiver(r, w, "sys-queue"), host, sys_port
    )
    app.state.mic_server = await asyncio.start_server(
        lambda r, w: _audio_receiver(r, w, "mic-queue"), host, mic_port
    )
    print(
        f"Audio servers listening on {host}:{sys_port} (sys) and {host}:{mic_port} (mic)"
    )

    # Start audio streamer subprocess after audio servers are listening
    await app.state.controller.start()

    # Create an async queue and bridge that pulls from the sync QueueManager and
    # forwards items into an asyncio.Queue for consumers that run in the event loop.
    app.state.async_transcript_queue = asyncio.Queue()

    async def _drain_transcripts_loop():
        qm = app.state.queue_manager
        q = qm.get_queue("transcripts")
        try:
            while True:
                try:
                    # block in thread to avoid blocking event loop
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

    app.state._transcript_bridge_task = asyncio.create_task(_drain_transcripts_loop())

    yield

    # Shutdown: stop controller and stt
    await app.state.controller.stop()
    await app.state.stt.stop()

    # Cancel bridge task
    task = getattr(app.state, "_transcript_bridge_task", None)
    if task:
        task.cancel()
        try:
            await task
        except Exception as e:
            logger.debug("Transcript bridge task cancel/wait raised: %s", e)


def create_app() -> FastAPI:
    """Create and return a FastAPI application wired with composition root.

    This is the canonical composition root — presentation routers should be
    included here when migrating the API surface into `presentation/`.
    """
    app = FastAPI(lifespan=_lifespan)

    # Configure structured logging and telemetry
    configure_logging()

    # Attach a LangChain-based OpenAI adapter to app.state if available.
    # Import lazily so that environments without LangChain installed still
    # successfully import the application module.
    try:
        from voice.infrastructure.adapters.langchain_adapter import (
            LangChainOpenAIAdapter,
        )

        app.state.openai_adapter = LangChainOpenAIAdapter()
    except Exception as e:  # pragma: no cover - optional runtime dependency
        logger.debug("LangChain adapter not available: %s", e)
        app.state.openai_adapter = None

    # TODO: Add middleware and routers here when migrating presentation layer

    return app
