import asyncio

from ekko.config.settings import BaseAppConfig
from ekko.infrastructure.audio_streamer.audio_streamer_controller import (
    AudioStreamerController,
)


def test_send_command_tcp():
    settings = BaseAppConfig(
        host="127.0.0.1",
        audio_streamer_tcp_port=56000,
    )

    async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(100)
        # echo back with acknowledgement
        writer.write(b"ACK:" + data)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def run_test():
        server = await asyncio.start_server(handler, settings.host, settings.audio_streamer_tcp_port)
        controller = AudioStreamerController(settings)
        try:
            result = await controller.send_command("ping")
            assert result == "ACK:ping"
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(run_test())
