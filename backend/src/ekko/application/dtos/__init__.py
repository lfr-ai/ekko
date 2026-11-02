"""Application-layer data transfer objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ekko.application.dtos.prompt_catalog import PromptCatalogDTO, PromptDTO

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class ConversationDTO:
    """Conversation data for API/GraphQL boundaries."""

    id: str
    started_at: datetime
    ended_at: datetime | None = None
    summary: str | None = None
    is_active: bool = True


@dataclass(frozen=True, kw_only=True, slots=True)
class MessageDTO:
    """Message data for API/GraphQL boundaries."""

    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class TranscriptDTO:
    """Transcript data for API/GraphQL boundaries."""

    id: str
    text: str
    source: str
    confidence: float
    created_at: datetime


__all__ = [
    "ConversationDTO",
    "MessageDTO",
    "PromptCatalogDTO",
    "PromptDTO",
    "TranscriptDTO",
]
