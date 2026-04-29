"""Tests for application-layer mappers."""

import uuid
from datetime import UTC, datetime

from ekko.application.mappers import (
    agent_result_to_dto,
    conversation_to_dto,
    message_to_dto,
    transcript_to_dto,
)
from ekko.core.entities import AgentResult, Conversation, Message, Transcript
from ekko.core.enums import MessageRole


class TestConversationMapper:
    def test_active_conversation(self):
        conv = Conversation(id=uuid.uuid4(), started_at=datetime.now(UTC))
        dto = conversation_to_dto(conv)
        assert dto.is_active
        assert dto.ended_at is None
        assert dto.id == str(conv.id)

    def test_ended_conversation(self):
        now = datetime.now(UTC)
        conv = Conversation(id=uuid.uuid4(), started_at=now, ended_at=now)
        dto = conversation_to_dto(conv)
        assert not dto.is_active


class TestMessageMapper:
    def test_maps_role(self):
        msg = Message(role=MessageRole.ASSISTANT, content="Hi")
        dto = message_to_dto(msg)
        assert dto.role == "assistant"
        assert dto.content == "Hi"


class TestTranscriptMapper:
    def test_maps_fields(self):
        t = Transcript(text="Hello", source="system", confidence=0.9)
        dto = transcript_to_dto(t)
        assert dto.text == "Hello"
        assert dto.confidence == 0.9


class TestAgentResultMapper:
    def test_maps_fields(self):
        r = AgentResult(agent_name="summarizer", task_name="summarize", output="Done", execution_time_seconds=2.0)
        dto = agent_result_to_dto(r)
        assert dto.agent_name == "summarizer"
        assert dto.execution_time_seconds == 2.0
