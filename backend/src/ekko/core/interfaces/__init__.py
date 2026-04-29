"""Core domain interfaces (protocols / abstract ports)."""

from ekko.core.interfaces.audio import AudioStreamerControllerProtocol, STTService
from ekko.core.interfaces.auth import JWTPort
from ekko.core.interfaces.chat import ChatPort
from ekko.core.interfaces.gateways import OpenAIGateway
from ekko.core.interfaces.pii import PIIAnonymizerPort
from ekko.core.interfaces.transcript import TranscriptProtocol

__all__ = [
    "AudioStreamerControllerProtocol",
    "ChatPort",
    "JWTPort",
    "OpenAIGateway",
    "PIIAnonymizerPort",
    "STTService",
    "TranscriptProtocol",
]
