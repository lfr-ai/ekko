"""Audio-related service protocols."""

from __future__ import annotations

from typing import Protocol


class STTService(Protocol):
    """Speech-to-text service interface."""

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def ensure_queue(self, queue_name: str) -> None: ...

    async def accept_bytes(self, queue_name: str, data: bytes) -> None: ...


class AudioStreamerControllerProtocol(Protocol):
    """Audio streamer subprocess controller interface."""

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def device_check(self) -> None: ...

    async def send_command(self, cmd: str) -> str: ...
