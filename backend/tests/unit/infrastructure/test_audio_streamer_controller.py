import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ekko.config.base import BaseAppConfig
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


@pytest.mark.asyncio
async def test_send_command_when_drain_fails_closes_writer() -> None:
    """TCP writer is closed and awaited when command transmission fails."""
    settings = BaseAppConfig(host="127.0.0.1", audio_streamer_tcp_port=56000)
    reader = AsyncMock()
    writer = MagicMock()
    writer.drain = AsyncMock(side_effect=ConnectionError("connection lost"))
    writer.wait_closed = AsyncMock()

    with patch(
        "ekko.infrastructure.audio_streamer.audio_streamer_controller.asyncio.open_connection",
        new=AsyncMock(return_value=(reader, writer)),
    ):
        controller = AudioStreamerController(settings)

        with pytest.raises(ConnectionError, match="connection lost"):
            await controller.send_command("ping")

    writer.close.assert_called_once_with()
    writer.wait_closed.assert_awaited_once_with()
