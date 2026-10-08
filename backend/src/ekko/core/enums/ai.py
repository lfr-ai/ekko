"""AI-related enums (prompts, STT providers)."""

from __future__ import annotations

from enum import StrEnum, auto, unique

from ekko.core.enums.base import ParseableEnum


@unique
class Prompt(StrEnum):
    """Prompt template identifiers for AI pipeline stages.

    Members:
        SUMMARY_CHUNKS: Chunked transcript summarization prompt.
        SUMMARIZER_SYSTEM: System prompt for the summarizer.
        CONVERSATIONAL_SYSTEM: Conversational assistant system prompt.
    """

    SUMMARY_CHUNKS = auto()
    SUMMARIZER_SYSTEM = auto()
    CONVERSATIONAL_SYSTEM = auto()


@unique
class STTProvider(ParseableEnum):
    """Speech-to-text provider options."""

    WHISPER = auto()
    FASTER_WHISPER = auto()
    AZURE_SPEECH = auto()
    GOOGLE_SPEECH = auto()
    OTHER = auto()


__all__ = ["Prompt", "STTProvider"]
