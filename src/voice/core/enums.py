"""Centralized enums for the voice-bot project.

This module provides a stable set of string/int enums used by the
application layers (core, application, infrastructure).
"""

from __future__ import annotations

from enum import IntEnum, StrEnum, unique
from typing import List


@unique
class LLMProvider(StrEnum):
    OPENAI = "openai"
    """Comprehensive, stable enumeration module for the voice-bot project.

    Centralizes all enumerated constants used across layers. Keep
    backwards-compatible names for values referenced elsewhere (do not rename
    existing members without a deprecation step).

    Design notes:
    - Prefer a StrEnum-like type for textual identifiers so environment
      variables and configuration may reference the string value directly.
    - Provide a small set of commonly used enums (audio, llm, stt, queues,
      transcript lifecycle, and telemetry flags).
    """

    from __future__ import annotations

    from enum import Enum, IntEnum, unique
    from typing import List

    try:  # Python 3.11+ provides StrEnum
        from enum import StrEnum  # type: ignore
    except Exception:  # pragma: no cover - fallback for older runtimes
        class StrEnum(str, Enum):
            """Fallback StrEnum for older Python versions."""


    def enum_values(enum_cls: type[StrEnum]) -> List[str]:
        """Return the string values of an enum class in declaration order.

        Example: enum_values(LLMProvider) -> ["openai", "azure_openai", ...]
        """

        return [e.value for e in enum_cls]


    @unique
    class Environment(StrEnum):
        """Deployment environment identifiers.

        Values are lowercase to make them friendly for env vars and logs.
        """

        LOCAL = "local"
        DEV = "dev"
        TEST = "test"
        STAGING = "staging"
        PROD = "prod"


    @unique
    class LLMProvider(StrEnum):
        """Canonical provider identifiers for LLM adapters."""

        OPENAI = "openai"
        AZURE_OPENAI = "azure_openai"
        ANTHROPIC = "anthropic"
        COHERE = "cohere"
        OTHER = "other"


    @unique
    class ChatModel(StrEnum):
        """Common chat model identifiers used in the app."""

        GPT_3_5_TURBO = "gpt-3.5-turbo"
        GPT_4 = "gpt-4"
        GPT_4O = "gpt-4o"
        GPT_5 = "gpt-5"


    @unique
    class STTProvider(StrEnum):
        """Speech-to-text backends supported by the application."""

        WHISPER = "whisper"
        FASTER_WHISPER = "faster_whisper"
        AZURE_SPEECH = "azure_speech"
        GOOGLE_SPEECH = "google_speech"
        OTHER = "other"


    @unique
    class AudioFormat(StrEnum):
        """Common audio container/encoding formats."""

        WAV = "wav"
        FLAC = "flac"
        MP3 = "mp3"
        OGG = "ogg"
        PCM16 = "pcm16"


    @unique
    class AudioChannel(IntEnum):
        """Audio channel counts (monophonic/stereo)."""

        MONO = 1
        STEREO = 2


    @unique
    class SampleRate(IntEnum):
        """Common audio sampling rates (Hz)."""

        SR_8000 = 8000
        SR_16000 = 16000
        SR_22050 = 22050
        SR_44100 = 44100
        SR_48000 = 48000
        SR_96000 = 96000


    @unique
    class BitDepth(IntEnum):
        """Common PCM bit depths."""

        BITS_8 = 8
        BITS_16 = 16
        BITS_24 = 24
        BITS_32 = 32


    @unique
    class QueueName(StrEnum):
        """Canonical names for in-process queues used by QueueManager."""

        TRANSCRIPTS = "transcripts"
        COMMANDS = "commands"
        EVENTS = "events"
        METRICS = "metrics"


    @unique
    class TranscriptStatus(StrEnum):
        """Lifecycle status for transcript items."""

        RECEIVED = "received"
        QUEUED = "queued"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"


    @unique
    class MessageRole(StrEnum):
        """Roles in chat/message payloads."""

        SYSTEM = "system"
        USER = "user"
        ASSISTANT = "assistant"
        TOOL = "tool"


    @unique
    class LogLevel(IntEnum):
        """Convenient mapping of standard logging levels to ints."""

        NOTSET = 0
        DEBUG = 10
        INFO = 20
        WARNING = 30
        ERROR = 40
        CRITICAL = 50


    @unique
    class DeploymentTarget(StrEnum):
        """Where the application is intended to run in a deployment pipeline."""

        LOCAL = "local"
        DOCKER = "docker"
        KUBERNETES = "kubernetes"
        AZURE_CONTAINER_APPS = "azure_container_apps"
        AZURE_FUNCTIONS = "azure_functions"


    @unique
    class FeatureFlag(StrEnum):
        """Feature flags used to gate optional runtime capabilities."""

        RAG_ENABLED = "rag_enabled"
        USE_AZURE_KEYVAULT = "use_azure_keyvault"
        ENABLE_TELEMETRY = "enable_telemetry"


    __all__ = [
        "Environment",
        "LLMProvider",
        "ChatModel",
        "STTProvider",
        "AudioFormat",
        "AudioChannel",
        "SampleRate",
        "BitDepth",
        "QueueName",
        "TranscriptStatus",
        "MessageRole",
        "LogLevel",
        "DeploymentTarget",
        "FeatureFlag",
        "enum_values",
    ]

