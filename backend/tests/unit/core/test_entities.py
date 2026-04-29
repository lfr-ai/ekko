"""Tests for core domain entities."""

import uuid
from datetime import UTC, datetime

import pytest

from ekko.core.entities import AgentResult, Conversation, Message, Transcript
from ekko.core.enums import MessageRole, TranscriptStatus


class TestConversation:
    def test_new_conversation_is_active(self):
        conv = Conversation()
        assert conv.is_active()
        assert conv.ended_at is None
        assert isinstance(conv.id, uuid.UUID)

    def test_conversation_with_ended_at_is_inactive(self):
        conv = Conversation(ended_at=datetime.now(UTC))
        assert not conv.is_active()

    def test_conversation_is_frozen(self):
        conv = Conversation()
        try:
            conv.id = uuid.uuid4()  # type: ignore[misc]
            pytest.fail("Should raise AttributeError")
        except AttributeError:
            pass


class TestMessage:
    def test_default_message(self):
        msg = Message()
        assert msg.role == MessageRole.USER
        assert msg.content == ""
        assert isinstance(msg.id, uuid.UUID)

    def test_message_with_role(self):
        msg = Message(role=MessageRole.ASSISTANT, content="Hello")
        assert msg.role == MessageRole.ASSISTANT
        assert msg.content == "Hello"


class TestTranscript:
    def test_default_transcript(self):
        t = Transcript()
        assert t.status == TranscriptStatus.RECEIVED
        assert t.source == "microphone"
        assert t.confidence == 0.0

    def test_transcript_with_text(self):
        t = Transcript(text="Hello world", confidence=0.95)
        assert t.text == "Hello world"
        assert t.confidence == 0.95


class TestAgentResult:
    def test_default_agent_result(self):
        r = AgentResult()
        assert r.agent_name == ""
        assert r.execution_time_seconds == 0.0

    def test_agent_result_with_data(self):
        r = AgentResult(agent_name="intent_detector", output="question", execution_time_seconds=1.5)
        assert r.agent_name == "intent_detector"
        assert r.execution_time_seconds == 1.5
