import asyncio
import logging
from asyncio import Event, StreamReader, StreamWriter

from voice.config.config import Config
from voice.infrastructure.audio_streamer.audio_streamer import AudioStreamer

logger = logging.getLogger(__name__)


async def _ipc_handler(
    reader: StreamReader,
    writer: StreamWriter,
    audio_streamer: AudioStreamer,
    stop_event: Event,
):
    """Handle incoming TCP commands and stream audio back to the main app."""
    try:
        data = await reader.read(audio_streamer.cfg.MAX_READ_BYTES)
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
                        sys_r, sys_w = await asyncio.open_connection(
                            audio_streamer.cfg.HOST,
                            audio_streamer.cfg.AUDIO_STREAMER_TCP_PORT + 1,
                        )

                        async def _send_loop(stream, writer_sock):
                            try:
                                while audio_streamer.sending and audio_streamer.running:
                                    data = await asyncio.to_thread(
                                        stream.read,
                                        audio_streamer.cfg.AUDIO_FRAMES_PER_BUFFER,
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
                    except Exception as e:
                        print(f"[Streamer] Failed to connect for sys audio: {e}")
                # Microphone audio
                if audio_streamer.mic_sending_task is None or audio_streamer.mic_sending_task.done():
                    try:
                        mic_r, mic_w = await asyncio.open_connection(
                            audio_streamer.cfg.HOST,
                            audio_streamer.cfg.AUDIO_STREAMER_TCP_PORT + 2,
                        )

                        async def _send_loop_mic(stream, writer_sock):
                            try:
                                while audio_streamer.sending and audio_streamer.running:
                                    data = await asyncio.to_thread(
                                        stream.read,
                                        audio_streamer.cfg.AUDIO_FRAMES_PER_BUFFER,
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
                    except Exception as e:
                        print(f"[Streamer] Failed to connect for mic audio: {e}")

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

    except Exception as e:
        logger.exception("Unhandled exception in IPC handler: %s", e)
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
    cfg = Config()
    audio_streamer = AudioStreamer(cfg)
    await audio_streamer.start()  # Initialize audio streams (no output yet)

    server = await asyncio.start_server(
        lambda r, w: _ipc_handler(r, w, audio_streamer, stop_event),
        host=cfg.HOST,
        port=cfg.AUDIO_STREAMER_TCP_PORT,
    )
    print(f"IPC server started on {cfg.HOST}:{cfg.AUDIO_STREAMER_TCP_PORT}")

    try:
        async with server:
            await stop_event.wait()
    finally:
        await audio_streamer.stop()
        print("IPC server shutting down")


if __name__ == "__main__":
    asyncio.run(main())
