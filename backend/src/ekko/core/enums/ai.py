"""AI-related enums (STT providers)."""

from __future__ import annotations

from enum import auto, unique

from ekko.core.enums.base import ParseableEnum


@unique
class STTProvider(ParseableEnum):
    """Speech-to-text provider options."""

    WHISPER = auto()
    FASTER_WHISPER = auto()
    AZURE_SPEECH = auto()
    GOOGLE_SPEECH = auto()
    OTHER = auto()


__all__ = ["STTProvider"]
