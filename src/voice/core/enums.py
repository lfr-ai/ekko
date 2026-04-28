"""Authoritative enums for the voice-bot project.

This module centralizes enumerated constants used across layers. Use this
file as the single source-of-truth for shared string and int constants.
"""

from __future__ import annotations

from enum import Enum, IntEnum, unique
from typing import List

try:
    from enum import StrEnum
except Exception:
    class StrEnum(str, Enum):
        """Fallback StrEnum for older Python versions."""


def enum_values(enum_cls: type[StrEnum]) -> List[str]:
    return [e.value for e in enum_cls]


@unique
class Environment(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    TEST = "test"
    STAGING = "staging"
    PROD = "prod"


@unique
class LLMProvider(StrEnum):
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    OTHER = "other"


@unique
class ChatModel(StrEnum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_5 = "gpt-5"


@unique
class STTProvider(StrEnum):
    WHISPER = "whisper"
    FASTER_WHISPER = "faster_whisper"
    AZURE_SPEECH = "azure_speech"
    GOOGLE_SPEECH = "google_speech"
    OTHER = "other"


@unique
class AudioFormat(StrEnum):
    WAV = "wav"
    FLAC = "flac"
    MP3 = "mp3"
    OGG = "ogg"
    PCM16 = "pcm16"


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
class QueueName(StrEnum):
    TRANSCRIPTS = "transcripts"
    COMMANDS = "commands"
    EVENTS = "events"
    METRICS = "metrics"


@unique
class TranscriptStatus(StrEnum):
    RECEIVED = "received"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@unique
class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@unique
class LogLevel(IntEnum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@unique
class DeploymentTarget(StrEnum):
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AZURE_CONTAINER_APPS = "azure_container_apps"
    AZURE_FUNCTIONS = "azure_functions"


@unique
class FeatureFlag(StrEnum):
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
