"""External service port protocols.

These protocols define the contracts that infrastructure adapters must fulfill.
"""

from ekko.core.ports.external.audio import (
    AudioStreamerControllerProtocol,
    STTService,
)
from ekko.core.ports.external.chat import ChatPort
from ekko.core.ports.external.pii import PIIAnonymizerPort
from ekko.core.ports.external.prompts import PromptProvider, PromptProviderError
from ekko.core.ports.external.transcript import TranscriptProtocol

__all__ = [
    "AudioStreamerControllerProtocol",
    "ChatPort",
    "PIIAnonymizerPort",
    "PromptProvider",
    "PromptProviderError",
    "STTService",
    "TranscriptProtocol",
]
