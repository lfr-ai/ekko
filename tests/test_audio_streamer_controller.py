import asyncio

from voice.config.config import Config
from voice.models.audio_streamer.audio_streamer_controller import (
    AudioStreamerController,
)


def test_send_command_tcp():
    cfg = Config()
    cfg.HOST = '127.0.0.1'
    cfg.AUDIO_STREAMER_TCP_PORT = 56000

    async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(100)
        # echo back with acknowledgement
        writer.write(b'ACK:' + data)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def run_test():
        server = await asyncio.start_server(handler, cfg.HOST, cfg.AUDIO_STREAMER_TCP_PORT)
        controller = AudioStreamerController(cfg)
        try:
            result = await controller.send_command('ping')
            assert result == 'ACK:ping'
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(run_test())
