"""Core domain value objects — immutable, identity-free data carriers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class AudioChunk:
    """Raw audio data with metadata."""

    data: bytes = b""
    sample_rate: int = 48000
    channels: int = 2
    source: str = "system"


@dataclass(frozen=True, slots=True)
class TranscriptSegment:
    """A segment of transcribed audio with timing info."""

    text: str = ""
    start_seconds: float = 0.0
    end_seconds: float = 0.0
    confidence: float = 0.0
    source: str = "microphone"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class PIIMatch:
    """A detected PII occurrence."""

    entity_type: str = ""
    start: int = 0
    end: int = 0
    text: str = ""
    score: float = 0.0


@dataclass(frozen=True, slots=True)
class AnonymizedText:
    """Result of PII anonymization."""

    original_text: str = ""
    anonymized_text: str = ""
    pii_matches: tuple[PIIMatch, ...] = ()

    @property
    def has_pii(self) -> bool:
        return len(self.pii_matches) > 0


@dataclass(frozen=True, slots=True)
class ConversationSummary:
    """Summary of a conversation produced by the summarizer agent."""

    text: str = ""
    key_topics: tuple[str, ...] = ()
    sentiment: str = "neutral"
    action_items: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class IntentClassification:
    """Result of intent detection from user speech."""

    intent: str = "unknown"
    confidence: float = 0.0
    entities: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TranscriptionInfo:
    """Metadata returned by the speech-to-text engine."""

    language: str = ""
    language_probability: float = 0.0
    duration: float = 0.0
