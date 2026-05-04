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


class TestFactoryUsage:
    """Demonstrate and validate factory-based test data generation."""

    def test_conversation_factory_creates_active_conversation(self, conversation_factory):
        """ConversationFactory creates an active conversation by default."""
        conversation = conversation_factory.create()

        assert conversation.is_active()
        assert conversation.ended_at is None
        assert isinstance(conversation.id, uuid.UUID)

    def test_conversation_factory_ended_trait(self, conversation_factory):
        """ConversationFactory.ended() creates a completed conversation."""
        conversation = conversation_factory.ended(summary="Test summary")

        assert not conversation.is_active()
        assert conversation.ended_at is not None
        assert conversation.summary == "Test summary"

    def test_message_factory_role_helpers(self, message_factory):
        """MessageFactory provides role-specific helper methods."""
        user_msg = message_factory.user_message(content="Hello")
        assistant_msg = message_factory.assistant_message(content="Hi")
        system_msg = message_factory.system_message(content="Instructions")

        assert user_msg.role == MessageRole.USER
        assert assistant_msg.role == MessageRole.ASSISTANT
        assert system_msg.role == MessageRole.SYSTEM

    def test_transcript_factory_completed_trait(self, transcript_factory):
        """TranscriptFactory.completed() creates a completed transcript."""
        transcript = transcript_factory.completed(text="Test transcript")

        assert transcript.status == TranscriptStatus.COMPLETED
        assert transcript.confidence == 1.0
        assert transcript.text == "Test transcript"

    def test_transcript_factory_low_confidence_trait(self, transcript_factory):
        """TranscriptFactory.low_confidence() creates low-confidence transcript."""
        transcript = transcript_factory.low_confidence(confidence=0.3)

        assert transcript.confidence == 0.3
        assert transcript.status == TranscriptStatus.RECEIVED

    def test_agent_result_factory_execution_time_traits(self, agent_result_factory):
        """AgentResultFactory provides execution time helper methods."""
        fast = agent_result_factory.fast_execution()
        slow = agent_result_factory.slow_execution()

        assert fast.execution_time_seconds < 1.0
        assert slow.execution_time_seconds > 10.0

    def test_factory_batch_creation(self, message_factory):
        """Factories support batch creation for multiple entities."""
        messages = message_factory.create_batch(5, role=MessageRole.USER)

        assert len(messages) == 5
        assert all(msg.role == MessageRole.USER for msg in messages)
        assert all(isinstance(msg.id, uuid.UUID) for msg in messages)
