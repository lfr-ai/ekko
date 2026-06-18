"""Core domain ports (protocols / abstract interfaces).

Organized into:
- ``external/`` — external service port protocols (LLM, audio, PII, prompts)
- ``repositories/`` — persistence port protocols (conversations, messages, transcripts)
"""

from ekko.core.ports.external import (
    AudioStreamerControllerProtocol,
    ChatPort,
    PIIAnonymizerPort,
    PromptProvider,
    PromptProviderError,
    STTService,
    TranscriptProtocol,
)
from ekko.core.ports.repositories import (
    ConversationRepositoryPort,
    MessageRepositoryPort,
    TranscriptRepositoryPort,
)

__all__ = [
    "AudioStreamerControllerProtocol",
    "ChatPort",
    "ConversationRepositoryPort",
    "MessageRepositoryPort",
    "PIIAnonymizerPort",
    "PromptProvider",
    "PromptProviderError",
    "STTService",
    "TranscriptProtocol",
    "TranscriptRepositoryPort",
]
