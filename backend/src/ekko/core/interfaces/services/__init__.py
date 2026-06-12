"""Service port protocols for external integrations.

These protocols define the contracts that infrastructure adapters must fulfill.
"""

from ekko.core.interfaces.services.audio import (
    AudioStreamerControllerProtocol,
    STTService,
)
from ekko.core.interfaces.services.chat import ChatPort
from ekko.core.interfaces.services.pii import PIIAnonymizerPort
from ekko.core.interfaces.services.prompts import PromptProvider, PromptProviderError
from ekko.core.interfaces.services.transcript import TranscriptProtocol

__all__ = [
    "AudioStreamerControllerProtocol",
    "ChatPort",
    "PIIAnonymizerPort",
    "PromptProvider",
    "PromptProviderError",
    "STTService",
    "TranscriptProtocol",
]
