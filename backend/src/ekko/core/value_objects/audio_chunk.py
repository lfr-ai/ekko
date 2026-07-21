"""Audio chunk value object."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AudioChunk:
    """Raw audio data with metadata."""

    data: bytes = b""
    sample_rate: int = 48000
    channels: int = 2
    source: str = "system"
