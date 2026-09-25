"""Factory-boy factories for core domain entities.

Provides factories for generating test data with sensible defaults
and controlled variation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import factory

from ekko.core.entities import Conversation, Message, Transcript
from ekko.core.enums import MessageRole, TranscriptStatus


class ConversationFactory(factory.Factory):
    """Factory for Conversation entities."""

    class Meta:
        model = Conversation

    id = factory.LazyFunction(uuid.uuid4)
    started_at = factory.LazyFunction(lambda: datetime.now(UTC))
    ended_at = None
    summary = None

    @classmethod
    def ended(cls, **kwargs):
        """Create a completed conversation with end time and summary."""
        ended_at = kwargs.pop("ended_at", None) or datetime.now(UTC)
        summary = kwargs.pop("summary", None) or "Sample conversation summary"
        return cls.create(ended_at=ended_at, summary=summary, **kwargs)


class MessageFactory(factory.Factory):
    """Factory for Message entities."""

    class Meta:
        model = Message

    id = factory.LazyFunction(uuid.uuid4)
    conversation_id = factory.LazyFunction(uuid.uuid4)
    role = MessageRole.USER
    content = factory.Faker("sentence")
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))

    @classmethod
    def user_message(cls, **kwargs):
        """Create a user message."""
        return cls.create(role=MessageRole.USER, **kwargs)

    @classmethod
    def assistant_message(cls, **kwargs):
        """Create an assistant message."""
        return cls.create(role=MessageRole.ASSISTANT, **kwargs)

    @classmethod
    def system_message(cls, **kwargs):
        """Create a system message."""
        return cls.create(role=MessageRole.SYSTEM, **kwargs)


class TranscriptFactory(factory.Factory):
    """Factory for Transcript entities."""

    class Meta:
        model = Transcript

    id = factory.LazyFunction(uuid.uuid4)
    conversation_id = factory.LazyFunction(uuid.uuid4)
    text = factory.Faker("sentence")
    source = "microphone"
    status = TranscriptStatus.RECEIVED
    confidence = 0.95
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))

    @classmethod
    def completed(cls, **kwargs):
        """Create a completed transcript."""
        return cls.create(status=TranscriptStatus.COMPLETED, confidence=1.0, **kwargs)

    @classmethod
    def failed(cls, **kwargs):
        """Create a failed transcript."""
        return cls.create(status=TranscriptStatus.FAILED, confidence=0.0, **kwargs)

    @classmethod
    def low_confidence(cls, **kwargs):
        """Create a low-confidence transcript."""
        confidence = kwargs.pop("confidence", 0.3)
        return cls.create(confidence=confidence, **kwargs)


__all__ = [
    "ConversationFactory",
    "MessageFactory",
    "TranscriptFactory",
]
