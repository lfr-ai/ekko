import asyncio
import socket

import voice.composition as composition
from voice.composition import create_app


def test_transcript_bridge_roundtrip():
    # choose a free ephemeral port for the audio streamer base port to avoid collisions
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    free_port = s.getsockname()[1]
    s.close()
    # set base port such that +1/+2 are available
    composition.cfg.AUDIO_STREAMER_TCP_PORT = max(1024, free_port - 1)

    app = create_app()

    async def run():
        async with app.router.lifespan_context(app):
            # put a transcript into the synchronous queue
            qm = app.state.queue_manager
            qm.put_in_queue("transcripts", {"text": "hello-bridge"})

            # await the async queue to receive it
            got = await asyncio.wait_for(app.state.async_transcript_queue.get(), timeout=2)
            assert got["text"] == "hello-bridge"

    asyncio.run(run())
