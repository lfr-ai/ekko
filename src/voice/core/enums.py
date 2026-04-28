"""Centralized, well-documented enumerations used across the codebase.

Keep a single authoritative source for shared constants to avoid
drift and accidental re-definitions introduced by merges.
"""

from __future__ import annotations

from enum import StrEnum, auto, unique


@unique
class Environment(StrEnum):
    """Deployment environment identifiers.

    Members reflect a typical pipeline: LOCAL -> DEV -> TEST -> STAGING -> PROD
    """

    LOCAL = auto()
    DEV = auto()
    TEST = auto()
    STAGING = auto()
    PROD = auto()


@unique
class LLMProvider(StrEnum):
    """Canonical LLM provider identifiers used by adapter factories."""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"


@unique
class ChatModel(StrEnum):
    """Common chat model identifiers (examples; override per-deployment).

    These are convenience names and may be mapped to actual deployment IDs in
    environment settings.
    """

    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_5 = "gpt-5"


@unique
class STTProvider(StrEnum):
    """Speech-to-text backends supported by the application."""

    WHISPER = "whisper"
    FASTER_WHISPER = "faster_whisper"
