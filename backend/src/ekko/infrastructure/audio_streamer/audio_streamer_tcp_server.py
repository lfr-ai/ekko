"""TCP server that streams audio data from the subprocess to connected clients."""

import asyncio
import logging
from asyncio import Event, StreamReader, StreamWriter

from ekko.config.settings import get_settings
from ekko.infrastructure.audio_streamer.audio_streamer import AudioStreamer

logger = logging.getLogger(__name__)


async def _ipc_handler(  # noqa: C901, PLR0915
    reader: StreamReader,
    writer: StreamWriter,
    audio_streamer: AudioStreamer,
    stop_event: Event,
):
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
                # Establish connections to main app's audio servers and start sending
                # System audio
                if audio_streamer.sys_sending_task is None or audio_streamer.sys_sending_task.done():
                    try:
                        _, sys_w = await asyncio.open_connection(
                            settings.host,
                            settings.audio_streamer_tcp_port + 1,
                        )

                        async def _send_loop(stream, writer_sock):
                            try:
                                while audio_streamer.sending and audio_streamer.running:
                                    data = await asyncio.to_thread(
                                        stream.read,
                                        settings.audio_frames_per_buffer,
                                    )
                                    if not data:
                                        break
                                    writer_sock.write(data)
                                    await writer_sock.drain()
                            except Exception as e:
                                logger.debug("Error while sending sys audio: %s", e)
                            finally:
                                writer_sock.close()
                                await writer_sock.wait_closed()

                        audio_streamer.sys_sending_task = asyncio.create_task(
                            _send_loop(audio_streamer.stream_sys, sys_w)
                        )
                    except Exception:
                        logger.exception("Failed to connect for sys audio")
                # Microphone audio
                if audio_streamer.mic_sending_task is None or audio_streamer.mic_sending_task.done():
                    try:
                        _, mic_w = await asyncio.open_connection(
                            settings.host,
                            settings.audio_streamer_tcp_port + 2,
                        )

                        async def _send_loop_mic(stream, writer_sock):
                            try:
                                while audio_streamer.sending and audio_streamer.running:
                                    data = await asyncio.to_thread(
                                        stream.read,
                                        settings.audio_frames_per_buffer,
                                    )
                                    if not data:
                                        break
                                    writer_sock.write(data)
                                    await writer_sock.drain()
                            except Exception as e:
                                logger.debug("Error while sending mic audio: %s", e)
                            finally:
                                writer_sock.close()
                                await writer_sock.wait_closed()

                        audio_streamer.mic_sending_task = asyncio.create_task(
                            _send_loop_mic(audio_streamer.stream_mic, mic_w)
                        )
                    except Exception:
                        logger.exception("Failed to connect for mic audio")

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
        logger.exception("Unhandled exception in IPC handler")
        try:
            writer.write(b"error")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception as e2:
            logger.debug("Failed to close writer after error: %s", e2)


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
    logger.info("IPC server started on %s:%s", settings.host, settings.audio_streamer_tcp_port)

    try:
        async with server:
            await stop_event.wait()
    finally:
        await audio_streamer.stop()
        logger.info("IPC server shutting down")


if __name__ == "__main__":
    asyncio.run(main())
