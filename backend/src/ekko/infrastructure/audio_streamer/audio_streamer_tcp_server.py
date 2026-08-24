"""TCP server that streams audio data from the subprocess to connected clients."""

from __future__ import annotations

import asyncio
import logging
from asyncio import Event, StreamReader, StreamWriter
from typing import Final, Protocol

from ekko.config.settings import get_settings
from ekko.infrastructure.audio_streamer.audio_streamer import AudioStreamer

_logger = logging.getLogger(__name__)

_SYSTEM_AUDIO_PORT_OFFSET: Final[int] = 1
_MICROPHONE_AUDIO_PORT_OFFSET: Final[int] = 2


class _AudioStream(Protocol):
    """Structural protocol for a PyAudio-style audio stream."""

    def read(self, num_frames: int) -> bytes: ...


async def _audio_send_loop(
    audio_streamer: AudioStreamer,
    stream: _AudioStream,
    writer_sock: StreamWriter,
    *,
    label: str,
) -> None:
    """Stream audio frames from a PyAudio stream to a TCP socket."""
    settings = audio_streamer.settings
    try:
        while audio_streamer.sending and audio_streamer.running:
            data = await asyncio.to_thread(stream.read, settings.audio_frames_per_buffer)
            if not data:
                break
            writer_sock.write(data)
            await writer_sock.drain()
    except Exception as e:
        _logger.debug("Audio send loop error", extra={"label": label, "error": str(e)})
    finally:
        writer_sock.close()
        await writer_sock.wait_closed()


async def _start_audio_sending(audio_streamer: AudioStreamer) -> None:
    """Connect to the main app's audio servers and start sending frames."""
    settings = audio_streamer.settings
    # System audio
    if audio_streamer.sys_sending_task is None or audio_streamer.sys_sending_task.done():
        if audio_streamer.stream_sys is None:
            _logger.warning("Sys audio stream not initialized")
            return
        try:
            _, sys_w = await asyncio.open_connection(
                settings.host,
                settings.audio_streamer_tcp_port + _SYSTEM_AUDIO_PORT_OFFSET,
            )
            audio_streamer.sys_sending_task = asyncio.create_task(
                _audio_send_loop(audio_streamer, audio_streamer.stream_sys, sys_w, label="sys")
            )
        except Exception:
            _logger.exception("Failed to connect for sys audio")
    # Microphone audio
    if audio_streamer.mic_sending_task is None or audio_streamer.mic_sending_task.done():
        if audio_streamer.stream_mic is None:
            _logger.warning("Mic audio stream not initialized")
            return
        try:
            _, mic_w = await asyncio.open_connection(
                settings.host,
                settings.audio_streamer_tcp_port + _MICROPHONE_AUDIO_PORT_OFFSET,
            )
            audio_streamer.mic_sending_task = asyncio.create_task(
                _audio_send_loop(audio_streamer, audio_streamer.stream_mic, mic_w, label="mic")
            )
        except Exception:
            _logger.exception("Failed to connect for mic audio")


async def _ipc_handler(
    reader: StreamReader,
    writer: StreamWriter,
    audio_streamer: AudioStreamer,
    stop_event: Event,
) -> None:
    """Handle incoming TCP commands and stream audio back to the main app."""
    settings = audio_streamer.settings
    try:
        data = await reader.read(settings.max_read_bytes)
        if not data:
            writer.write(b"no data")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        cmd = data.decode().strip()
        match cmd:
            case "start_stream":
                audio_streamer.start_stream()
                await _start_audio_sending(audio_streamer)
                writer.write(b"started")

            case "pause_stream":
                audio_streamer.pause_stream()
                writer.write(b"paused")

            case "stop":
                audio_streamer.pause_stream()
                stop_event.set()
                writer.write(b"stopped")

            case _:
                writer.write(b"unknown command")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    except Exception:
        _logger.exception("IPC handler error")
        try:
            writer.write(b"error")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception as e2:
            _logger.debug("Failed to close IPC writer", extra={"error": str(e2)})


async def main():
    """Run the TCP IPC server and audio streamer."""
    stop_event = Event()
    settings = get_settings()
    audio_streamer = AudioStreamer(settings)
    await audio_streamer.start()  # Initialize audio streams (no output yet)

    server = await asyncio.start_server(
        lambda r, w: _ipc_handler(r, w, audio_streamer, stop_event),
        host=settings.host,
        port=settings.audio_streamer_tcp_port,
    )
    _logger.info(
        "IPC server started",
        extra={"host": settings.host, "port": settings.audio_streamer_tcp_port},
    )

    try:
        async with server:
            await stop_event.wait()
    finally:
        await audio_streamer.stop()
        _logger.info("IPC server shutting down")


if __name__ == "__main__":
    asyncio.run(main())
