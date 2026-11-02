"""Speech-to-text service port protocol."""

from __future__ import annotations

from typing import Protocol


class STTPort(Protocol):
    """Speech-to-text service interface."""

    async def start(self) -> None:
        """Start the speech-to-text service."""
        ...

    async def stop(self) -> None:
        """Stop the service and release resources."""
        ...

    async def ensure_queue(self, queue_name: str) -> None:
        """Ensure a recognizer exists for the named audio source."""
        ...

    async def accept_bytes(self, queue_name: str, data: bytes) -> None:
        """Feed raw audio bytes for the named source."""
        ...
