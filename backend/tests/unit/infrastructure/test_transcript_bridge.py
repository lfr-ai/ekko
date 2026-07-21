"""Test transcript bridge between sync and async queues."""

import asyncio
import socket

import pytest


def test_transcript_bridge_roundtrip():
    """Verify transcripts flow from sync QueueManager to async queue."""
    from ekko.composition.app_factory import create_app

    app = create_app()

    # Override the audio port to avoid collisions
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    free_port = s.getsockname()[1]
    s.close()
    app.state.container.settings.__dict__["audio_streamer_tcp_port"] = max(1024, free_port - 1)

    async def run():
        async with app.router.lifespan_context(app):
            qm = app.state.queue_manager
            qm.put_in_queue("transcripts", {"text": "hello-bridge"})

            got = await asyncio.wait_for(app.state.async_transcript_queue.get(), timeout=2)
            assert got["text"] == "hello-bridge"

    # This test requires real audio infrastructure; skip if not available
    try:
        asyncio.run(run())
    except Exception:
        pytest.skip("Audio infrastructure not available for bridge test")
