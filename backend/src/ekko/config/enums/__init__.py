"""Configuration enums."""

from __future__ import annotations

from enum import auto, unique

from ekko.utils.enums import ParseableEnum


@unique
class Environment(ParseableEnum):
    """Application environment."""

    LOCAL = auto()
    TEST = auto()
    DEV = auto()
    PROD = auto()


@unique
class DatabaseBackend(ParseableEnum):
    """Supported runtime database backends."""

    SQLITE = auto()
    POSTGRESQL = auto()


@unique
class LLMProvider(ParseableEnum):
    """LLM provider options."""

    OPENAI = auto()
    AZURE_OPENAI = auto()
    ANTHROPIC = auto()
    COHERE = auto()
    GOOGLE = auto()
    OTHER = auto()


@unique
class ChatModel(ParseableEnum):
    """Chat model options."""

    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_5 = "gpt-5"


__all__ = ["ChatModel", "DatabaseBackend", "Environment", "LLMProvider"]
