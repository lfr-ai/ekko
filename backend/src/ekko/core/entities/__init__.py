"""Core domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from ekko.core.enums import MessageRole, TranscriptStatus


@dataclass(frozen=True, kw_only=True, slots=True)
class Conversation:
    """A voice conversation session."""

    id: UUID = field(default_factory=uuid4)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None
    summary: str | None = None

    def is_active(self) -> bool:
        """Whether the conversation has not yet ended."""
        return self.ended_at is None


@dataclass(frozen=True, kw_only=True, slots=True)
class Message:
    """A single message in a conversation."""

    id: UUID = field(default_factory=uuid4)
    conversation_id: UUID
    role: MessageRole = MessageRole.USER
    content: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True, slots=True)
class Transcript:
    """A speech-to-text transcript segment."""

    id: UUID = field(default_factory=uuid4)
    conversation_id: UUID | None = None
    text: str = ""
    source: str = "microphone"
    status: TranscriptStatus = TranscriptStatus.RECEIVED
    confidence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
