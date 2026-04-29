"""Application-layer data transfer objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ekko.core.enums import MessageRole

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True, slots=True)
class ConversationDTO:
    """Conversation data for API/GraphQL boundaries."""

    id: str
    started_at: datetime
    ended_at: datetime | None = None
    summary: str | None = None
    is_active: bool = True


@dataclass(frozen=True, slots=True)
class MessageDTO:
    """Message data for API/GraphQL boundaries."""

    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class TranscriptDTO:
    """Transcript data for API/GraphQL boundaries."""

    id: str
    text: str
    source: str
    confidence: float
    created_at: datetime


@dataclass(frozen=True, slots=True)
class AgentResultDTO:
    """CrewAI agent result for API/GraphQL boundaries."""

    agent_name: str
    task_name: str
    output: str
    execution_time_seconds: float


@dataclass(frozen=True, slots=True)
class StartConversationDTO:
    """Input for starting a new conversation."""

    metadata: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class SendMessageDTO:
    """Input for sending a message in a conversation."""

    conversation_id: str
    content: str
    role: str = MessageRole.USER
