"""Application-layer mappers — entity ↔ DTO conversions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ekko.application.dtos import ConversationDTO, MessageDTO, TranscriptDTO

if TYPE_CHECKING:
    from ekko.core.entities import Conversation, Message, Transcript


def conversation_to_dto(entity: Conversation) -> ConversationDTO:
    """Map a Conversation entity to its DTO."""
    return ConversationDTO(
        id=str(entity.id),
        started_at=entity.started_at,
        ended_at=entity.ended_at,
        summary=entity.summary,
        is_active=entity.is_active(),
    )


def message_to_dto(entity: Message) -> MessageDTO:
    """Map a Message entity to its DTO."""
    return MessageDTO(
        id=str(entity.id),
        conversation_id=str(entity.conversation_id),
        role=entity.role.value,
        content=entity.content,
        created_at=entity.created_at,
    )


def transcript_to_dto(entity: Transcript) -> TranscriptDTO:
    """Map a Transcript entity to its DTO."""
    return TranscriptDTO(
        id=str(entity.id),
        text=entity.text,
        source=entity.source,
        confidence=entity.confidence,
        created_at=entity.created_at,
    )
