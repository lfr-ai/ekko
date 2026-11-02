"""Audio streamer subprocess controller port protocol."""

from __future__ import annotations

from typing import Protocol


class AudioStreamerControllerPort(Protocol):
    """Audio streamer subprocess controller interface."""

    async def start(self) -> None:
        """Start the audio streamer subprocess."""
        ...

    async def stop(self) -> None:
        """Stop the audio streamer subprocess."""
        ...

    async def device_check(self) -> None:
        """Restart the subprocess when audio devices change."""
        ...

    async def send_command(self, cmd: str) -> str:
        """Send a control command and return the subprocess reply."""
        ...
