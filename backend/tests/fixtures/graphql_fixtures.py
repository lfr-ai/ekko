"""GraphQL test fixtures and query data."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from ekko.presentation.graphql.types import ConversationType


# ── Query strings ────────────────────────────────────────────


HEALTH_QUERY = """
    query {
        health {
            status
            environment
            dependencies {
                name
                healthy
                detail
            }
        }
    }
"""

HEALTH_READY_QUERY = """
    query {
        healthReady {
            status
            environment
            dependencies {
                name
                healthy
                detail
            }
        }
    }
"""

CONVERSATION_QUERY = """
    query GetConversation($id: String!) {
        conversation(id: $id) {
            id
            startedAt
            endedAt
            summary
            isActive
        }
    }
"""

CONVERSATIONS_LIST_QUERY = """
    query ListConversations($limit: Int, $offset: Int) {
        conversations(limit: $limit, offset: $offset) {
            id
            startedAt
            isActive
        }
    }
"""

CHECK_PII_QUERY = """
    query CheckPII($text: String!) {
        checkPii(text: $text) {
            anonymizedText
            piiFound
            matchCount
        }
    }
"""

CONTROL_STREAM_MUTATION = """
    mutation ControlStream($command: StreamCommandInput!) {
        controlStream(command: $command) {
            active
            message
        }
    }
"""

START_CONVERSATION_MUTATION = """
    mutation StartConversation($input: StartConversationInput) {
        startConversation(input: $input) {
            id
            startedAt
            isActive
        }
    }
"""

END_CONVERSATION_MUTATION = """
    mutation EndConversation($conversationId: String!) {
        endConversation(conversationId: $conversationId) {
            id
            endedAt
            isActive
        }
    }
"""

SEND_MESSAGE_MUTATION = """
    mutation SendMessage($input: SendMessageInput!) {
        sendMessage(input: $input)
    }
"""

ANONYMIZE_TEXT_MUTATION = """
    mutation AnonymizeText($input: AnonymizeTextInput!) {
        anonymizeText(input: $input) {
            anonymizedText
            piiFound
            matchCount
        }
    }
"""

# Invalid query for error testing
INVALID_QUERY = """
    query {
        nonExistentField {
            invalidData
        }
    }
"""

MALFORMED_QUERY = """
    query {
        health {
            status
            environment
            # Missing closing brace
"""


# ── Sample data ──────────────────────────────────────────────


@pytest.fixture
def sample_conversation() -> ConversationType:
    """Sample conversation object for testing."""
    from ekko.presentation.graphql.types import ConversationType

    return ConversationType(
        id="test-conversation-123",
        started_at=datetime.now(UTC),
        is_active=True,
        summary=None,
    )


@pytest.fixture
def sample_pii_text() -> str:
    """Sample text containing PII for testing."""
    return "My email is john.doe@example.com and my phone is 555-123-4567."


@pytest.fixture
def sample_clean_text() -> str:
    """Sample text without PII for testing."""
    return "The weather is nice today."
