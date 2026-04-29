"""Core domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from ekko.core.enums import MessageRole, TranscriptStatus


@dataclass(frozen=True, slots=True)
class Conversation:
    """A voice conversation session."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None
    summary: str | None = None

    def is_active(self) -> bool:
        return self.ended_at is None


@dataclass(frozen=True, slots=True)
class Message:
    """A single message in a conversation."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    conversation_id: uuid.UUID = field(default_factory=uuid.uuid4)
    role: MessageRole = MessageRole.USER
    content: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class Transcript:
    """A speech-to-text transcript segment."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    conversation_id: uuid.UUID | None = None
    text: str = ""
    source: str = "microphone"
    status: TranscriptStatus = TranscriptStatus.RECEIVED
    confidence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class AgentResult:
    """Result from a CrewAI agent execution."""

    agent_name: str = ""
    task_name: str = ""
    output: str = ""
    raw_output: str = ""
    execution_time_seconds: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
