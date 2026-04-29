"""Application-layer mappers — entity ↔ DTO conversions."""

from __future__ import annotations

from ekko.application.dtos import AgentResultDTO, ConversationDTO, MessageDTO, TranscriptDTO
from ekko.core.entities import AgentResult, Conversation, Message, Transcript  # noqa: TC001


def conversation_to_dto(entity: Conversation) -> ConversationDTO:
    return ConversationDTO(
        id=str(entity.id),
        started_at=entity.started_at,
        ended_at=entity.ended_at,
        summary=entity.summary,
        is_active=entity.is_active(),
    )


def message_to_dto(entity: Message) -> MessageDTO:
    return MessageDTO(
        id=str(entity.id),
        conversation_id=str(entity.conversation_id),
        role=entity.role.value,
        content=entity.content,
        created_at=entity.created_at,
    )


def transcript_to_dto(entity: Transcript) -> TranscriptDTO:
    return TranscriptDTO(
        id=str(entity.id),
        text=entity.text,
        source=entity.source,
        confidence=entity.confidence,
        created_at=entity.created_at,
    )


def agent_result_to_dto(entity: AgentResult) -> AgentResultDTO:
    return AgentResultDTO(
        agent_name=entity.agent_name,
        task_name=entity.task_name,
        output=entity.output,
        execution_time_seconds=entity.execution_time_seconds,
    )
