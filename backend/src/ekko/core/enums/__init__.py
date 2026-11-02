"""Authoritative domain enums for the Ekko project.

Re-exports every enum from the sub-modules (``from ekko.core.enums import X``).

Configuration-level enums (Environment, ChatModel, LLMProvider, DatabaseBackend)
live in ``ekko.config.enums`` and should be imported directly from there.
"""

from ekko.core.enums.ai import Prompt, STTProvider
from ekko.core.enums.audio import (
    AudioChannel,
    AudioFormat,
    AudioQueueName,
    BitDepth,
    SampleRate,
)
from ekko.core.enums.base import ParseableEnum, enum_values
from ekko.core.enums.common import LogLevel, ServiceStatus, SortOrder
from ekko.core.enums.messaging import (
    MessageRole,
    QueueName,
    RecognitionMode,
    TranscriptStatus,
)

__all__ = [
    "AudioChannel",
    "AudioFormat",
    "AudioQueueName",
    "BitDepth",
    "LogLevel",
    "MessageRole",
    "ParseableEnum",
    "Prompt",
    "QueueName",
    "RecognitionMode",
    "STTProvider",
    "SampleRate",
    "ServiceStatus",
    "SortOrder",
    "TranscriptStatus",
    "enum_values",
]
