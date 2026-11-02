"""Core domain ports (protocols / abstract interfaces).

Organized into:
- ``external/`` — external service port protocols (LLM, audio, PII, prompts)
- ``repositories/`` — persistence port protocols (conversations, messages, transcripts)
"""

from ekko.core.ports.external import (
    AudioStreamerControllerPort,
    ChatPort,
    DependencyStatus,
    PIIAnonymizerPort,
    PromptRegistryError,
    PromptRegistryPort,
    ReadinessProbe,
    STTPort,
    TranscriptPort,
)
from ekko.core.ports.repositories import (
    ConversationRepositoryPort,
    MessageRepositoryPort,
    TranscriptRepositoryPort,
)

__all__ = [
    "AudioStreamerControllerPort",
    "ChatPort",
    "ConversationRepositoryPort",
    "DependencyStatus",
    "MessageRepositoryPort",
    "PIIAnonymizerPort",
    "PromptRegistryError",
    "PromptRegistryPort",
    "ReadinessProbe",
    "STTPort",
    "TranscriptPort",
    "TranscriptRepositoryPort",
]
