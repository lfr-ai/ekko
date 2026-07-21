"""Audio-related enums."""

from __future__ import annotations

from enum import IntEnum, auto, unique

from ekko.core.enums.base import ParseableEnum


@unique
class AudioFormat(ParseableEnum):
    WAV = auto()
    FLAC = auto()
    MP3 = auto()
    OGG = auto()
    PCM16 = auto()


@unique
class AudioChannel(IntEnum):
    MONO = 1
    STEREO = 2


@unique
class SampleRate(IntEnum):
    SR_8000 = 8000
    SR_16000 = 16000
    SR_22050 = 22050
    SR_44100 = 44100
    SR_48000 = 48000
    SR_96000 = 96000


@unique
class BitDepth(IntEnum):
    BITS_8 = 8
    BITS_16 = 16
    BITS_24 = 24
    BITS_32 = 32


@unique
class AudioQueueName(ParseableEnum):
    """Named audio stream queues for the STT pipeline."""

    SYSTEM = "sys-queue"
    MICROPHONE = "mic-queue"


__all__ = ["AudioChannel", "AudioFormat", "AudioQueueName", "BitDepth", "SampleRate"]
