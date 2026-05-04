"""Common conversation fixtures for testing.

Provides pre-built conversation scenarios for consistent testing.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from ekko.core.entities import Conversation, Message
from ekko.core.enums import MessageRole

# Sample conversation IDs for consistent testing
SAMPLE_CONVERSATION_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")
SAMPLE_USER_ID = uuid.UUID("87654321-4321-8765-4321-876543218765")

# Active conversation fixture
ACTIVE_CONVERSATION = Conversation(
    id=SAMPLE_CONVERSATION_ID,
    started_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
    ended_at=None,
    summary=None,
)

# Completed conversation fixture
COMPLETED_CONVERSATION = Conversation(
    id=SAMPLE_CONVERSATION_ID,
    started_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
    ended_at=datetime(2024, 1, 1, 10, 30, 0, tzinfo=UTC),
    summary="User discussed project requirements and timelines.",
)

# Sample messages for a conversation
SAMPLE_MESSAGES = [
    Message(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        conversation_id=SAMPLE_CONVERSATION_ID,
        role=MessageRole.SYSTEM,
        content="You are a helpful AI assistant.",
        created_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
    ),
    Message(
        id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        conversation_id=SAMPLE_CONVERSATION_ID,
        role=MessageRole.USER,
        content="Hello, I need help with my project.",
        created_at=datetime(2024, 1, 1, 10, 0, 5, tzinfo=UTC),
    ),
    Message(
        id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        conversation_id=SAMPLE_CONVERSATION_ID,
        role=MessageRole.ASSISTANT,
        content="I'd be happy to help! What kind of project are you working on?",
        created_at=datetime(2024, 1, 1, 10, 0, 10, tzinfo=UTC),
    ),
    Message(
        id=uuid.UUID("44444444-4444-4444-4444-444444444444"),
        conversation_id=SAMPLE_CONVERSATION_ID,
        role=MessageRole.USER,
        content="It's a voice transcription system with AI analysis.",
        created_at=datetime(2024, 1, 1, 10, 0, 15, tzinfo=UTC),
    ),
]


__all__ = [
    "ACTIVE_CONVERSATION",
    "COMPLETED_CONVERSATION",
    "SAMPLE_CONVERSATION_ID",
    "SAMPLE_MESSAGES",
    "SAMPLE_USER_ID",
]
