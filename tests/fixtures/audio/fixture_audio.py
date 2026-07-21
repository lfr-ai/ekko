"""Audio fixture data for testing."""

from __future__ import annotations

import struct


def generate_pcm_audio_bytes(
    duration_seconds: float = 1.0,
    sample_rate: int = 16000,
    channels: int = 1,
) -> bytes:
    """Generate mock PCM audio bytes (silence).

    Args:
        duration_seconds: Duration of audio in seconds.
        sample_rate: Sample rate in Hz.
        channels: Number of audio channels.

    Returns:
        Raw PCM audio bytes (16-bit signed integers).
    """
    num_samples = int(duration_seconds * sample_rate * channels)
    # Generate silence (all zeros) as 16-bit signed integers
    return b"".join(struct.pack("<h", 0) for _ in range(num_samples))


# Predefined fixtures
FIXTURE_AUDIO_1_SEC = generate_pcm_audio_bytes(duration_seconds=1.0)
FIXTURE_AUDIO_SHORT = generate_pcm_audio_bytes(duration_seconds=0.1)
FIXTURE_AUDIO_INVALID = b"invalid audio data"
