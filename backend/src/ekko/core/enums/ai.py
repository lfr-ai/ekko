"""AI-related enums (LLM, STT providers and models)."""

from __future__ import annotations

from enum import auto, unique

from ekko.core.enums.base import ParseableEnum


@unique
class LLMProvider(ParseableEnum):
    OPENAI = auto()
    AZURE_OPENAI = auto()
    ANTHROPIC = auto()
    COHERE = auto()
    GOOGLE = auto()
    OTHER = auto()


@unique
class ChatModel(ParseableEnum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_5 = "gpt-5"


@unique
class STTProvider(ParseableEnum):
    WHISPER = auto()
    FASTER_WHISPER = auto()
    AZURE_SPEECH = auto()
    GOOGLE_SPEECH = auto()
    OTHER = auto()


__all__ = ["ChatModel", "LLMProvider", "STTProvider"]
