"""GraphQL test fixtures and query data."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Final

import pytest

if TYPE_CHECKING:
    from ekko.presentation.graphql.types import ConversationType


# ── Query strings ────────────────────────────────────────────


_GRAPHQL_FIXTURES_DIR: Final[Path] = Path(__file__).resolve().parent / "graphql"


def _read_graphql_document(*, relative_path: str) -> str:
    """Read a GraphQL fixture document from disk."""
    return (_GRAPHQL_FIXTURES_DIR / relative_path).read_text(encoding="utf-8").strip()


HEALTH_QUERY = _read_graphql_document(relative_path="queries/health.graphql")

HEALTH_READY_QUERY = _read_graphql_document(relative_path="queries/health-ready.graphql")

CONVERSATION_QUERY = _read_graphql_document(relative_path="queries/conversation.graphql")

CONVERSATIONS_LIST_QUERY = _read_graphql_document(relative_path="queries/conversations-list.graphql")

CHECK_PII_QUERY = _read_graphql_document(relative_path="queries/check-pii.graphql")

INSURANCE_CONDITION_OPTIONS_QUERY = _read_graphql_document(
    relative_path="queries/insurance-condition-options.graphql"
)

CONTROL_STREAM_MUTATION = _read_graphql_document(relative_path="mutations/control-stream.graphql")

START_CONVERSATION_MUTATION = _read_graphql_document(relative_path="mutations/start-conversation.graphql")

END_CONVERSATION_MUTATION = _read_graphql_document(relative_path="mutations/end-conversation.graphql")

SEND_MESSAGE_MUTATION = _read_graphql_document(relative_path="mutations/send-message.graphql")

ANONYMIZE_TEXT_MUTATION = _read_graphql_document(relative_path="mutations/anonymize-text.graphql")

SUBMIT_CLAIM_INTAKE_MUTATION = _read_graphql_document(
    relative_path="mutations/submit-claim-intake.graphql"
)

# Invalid query for error testing
INVALID_QUERY = _read_graphql_document(relative_path="queries/invalid.graphql")

MALFORMED_QUERY = _read_graphql_document(relative_path="queries/malformed.graphql")


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
