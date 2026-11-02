"""Audio chunk value object."""

from __future__ import annotations

from dataclasses import dataclass

from ekko.core.enums import AudioChannel, SampleRate


@dataclass(frozen=True, kw_only=True, slots=True)
class AudioChunk:
    """Raw audio data with metadata."""

    data: bytes = b""
    sample_rate: int = SampleRate.SR_48000
    channels: int = AudioChannel.STEREO
    source: str = "system"
