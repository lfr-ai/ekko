"""Strawberry GraphQL types for the Ekko API."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Strawberry needs runtime access
from enum import Enum

import strawberry

# ── Domain types ─────────────────────────────────────────────


@strawberry.type
class DependencyHealthType:
    """Health status of a single service dependency."""

    name: str
    healthy: bool
    detail: str = ""


@strawberry.type
class HealthType:
    """Application health check result."""

    status: str
    environment: str
    dependencies: list[DependencyHealthType]


@strawberry.type
class TranscriptType:
    """A speech-to-text transcript."""

    text: str
    source: str
    timestamp: str


@strawberry.type
class StreamStatusType:
    """Current audio stream status."""

    active: bool
    message: str


@strawberry.type
class ConversationType:
    """A voice conversation session."""

    id: str
    started_at: datetime
    ended_at: datetime | None = None
    summary: str | None = None
    is_active: bool = True


@strawberry.type
class MessageType:
    """A single message in a conversation."""

    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime


@strawberry.type
class AgentResultType:
    """Result from a CrewAI agent execution."""

    agent_name: str
    task_name: str
    output: str
    execution_time_seconds: float


@strawberry.type
class PIIResultType:
    """Result of PII anonymization."""

    anonymized_text: str
    pii_found: bool
    match_count: int


# ── Enum types ───────────────────────────────────────────────


@strawberry.enum
class ConversationStatus(Enum):
    ACTIVE = "active"
    ENDED = "ended"
    ARCHIVED = "archived"


# ── Input types ──────────────────────────────────────────────


@strawberry.input
class StreamCommandInput:
    """Input for stream control mutations."""

    action: str  # "start" or "pause"


@strawberry.input
class StartConversationInput:
    """Input for starting a new conversation."""

    metadata: str | None = None


@strawberry.input
class SendMessageInput:
    """Input for sending a message."""

    conversation_id: str
    content: str
    role: str = "user"  # Strawberry needs literal default for schema generation


@strawberry.input
class AnonymizeTextInput:
    """Input for PII anonymization."""

    text: str
    enabled_types: list[str] | None = None


# ── Pagination ───────────────────────────────────────────────


@strawberry.type
class PageInfo:
    """Relay-style pagination info."""

    has_next_page: bool
    has_previous_page: bool
    start_cursor: str | None = None
    end_cursor: str | None = None


@strawberry.type
class ConversationEdge:
    """Edge in a conversation connection."""

    cursor: str
    node: ConversationType


@strawberry.type
class ConversationConnection:
    """Paginated list of conversations."""

    edges: list[ConversationEdge]
    page_info: PageInfo
    total_count: int
