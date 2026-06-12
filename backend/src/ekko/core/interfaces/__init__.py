"""Core domain interfaces (protocols / abstract ports).

Organized into:
- ``services/`` — external service port protocols (LLM, audio, PII, prompts)
- ``repositories/`` — persistence port protocols (conversations, messages, transcripts)
"""

from ekko.core.interfaces.repositories import (
    ConversationRepositoryPort,
    MessageRepositoryPort,
    TranscriptRepositoryPort,
)
from ekko.core.interfaces.services import (
    AudioStreamerControllerProtocol,
    ChatPort,
    PIIAnonymizerPort,
    PromptProvider,
    PromptProviderError,
    STTService,
    TranscriptProtocol,
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
