"""Unit tests for domain events."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from ekko.core.events import (
    ConversationEnded,
    ConversationStarted,
    PIIDetected,
    SummaryGenerated,
    TranscriptReceived,
)


@pytest.mark.unit
class TestConversationStarted:
    """Test ConversationStarted domain event."""

    def test_construction(self) -> None:
        """Construct event with valid attributes."""
        event = ConversationStarted(
            conversation_id=uuid4(),
            source="desktop_audio",
            occurred_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
        )
        assert event.source == "desktop_audio"
        assert isinstance(event.conversation_id, UUID)

    def test_immutable(self) -> None:
        """Raise on attribute mutation."""
        event = ConversationStarted(
            conversation_id=uuid4(),
            source="mic",
            occurred_at=datetime.now(UTC),
        )
        with pytest.raises(AttributeError):
            event.source = "changed"  # type: ignore[misc]

    def test_equality(self) -> None:
        """Equal events with same field values."""
        cid = uuid4()
        ts = datetime(2026, 7, 1, tzinfo=UTC)
        a = ConversationStarted(conversation_id=cid, source="mic", occurred_at=ts)
        b = ConversationStarted(conversation_id=cid, source="mic", occurred_at=ts)
        assert a == b


@pytest.mark.unit
class TestConversationEnded:
    """Test ConversationEnded domain event."""

    def test_construction(self) -> None:
        """Construct event with duration."""
        event = ConversationEnded(
            conversation_id=uuid4(),
            duration_seconds=120.5,
            occurred_at=datetime.now(UTC),
        )
        assert event.duration_seconds == 120.5

    def test_immutable(self) -> None:
        """Raise on attribute mutation."""
        event = ConversationEnded(
            conversation_id=uuid4(),
            duration_seconds=60.0,
            occurred_at=datetime.now(UTC),
        )
        with pytest.raises(AttributeError):
            event.duration_seconds = 0.0  # type: ignore[misc]


@pytest.mark.unit
class TestTranscriptReceived:
    """Test TranscriptReceived domain event."""

    def test_construction(self) -> None:
        """Construct event with transcript content."""
        event = TranscriptReceived(
            transcript_id=uuid4(),
            conversation_id=uuid4(),
            text="Hello world",
            confidence=0.95,
            occurred_at=datetime.now(UTC),
        )
        assert event.text == "Hello world"
        assert event.confidence == 0.95

    def test_immutable(self) -> None:
        """Raise on attribute mutation."""
        event = TranscriptReceived(
            transcript_id=uuid4(),
            conversation_id=uuid4(),
            text="test",
            confidence=0.9,
            occurred_at=datetime.now(UTC),
        )
        with pytest.raises(AttributeError):
            event.text = "modified"  # type: ignore[misc]


@pytest.mark.unit
class TestSummaryGenerated:
    """Test SummaryGenerated domain event."""

    def test_construction(self) -> None:
        """Construct event with summary text."""
        event = SummaryGenerated(
            conversation_id=uuid4(),
            summary_text="Meeting discussed project deadlines.",
            occurred_at=datetime.now(UTC),
        )
        assert event.summary_text == "Meeting discussed project deadlines."

    def test_immutable(self) -> None:
        """Raise on attribute mutation."""
        event = SummaryGenerated(
            conversation_id=uuid4(),
            summary_text="summary",
            occurred_at=datetime.now(UTC),
        )
        with pytest.raises(AttributeError):
            event.summary_text = "changed"  # type: ignore[misc]


@pytest.mark.unit
class TestPIIDetected:
    """Test PIIDetected domain event."""

    def test_construction(self) -> None:
        """Construct event with entity count."""
        event = PIIDetected(
            conversation_id=uuid4(),
            entity_count=3,
            occurred_at=datetime.now(UTC),
        )
        assert event.entity_count == 3

    def test_immutable(self) -> None:
        """Raise on attribute mutation."""
        event = PIIDetected(
            conversation_id=uuid4(),
            entity_count=1,
            occurred_at=datetime.now(UTC),
        )
        with pytest.raises(AttributeError):
            event.entity_count = 5  # type: ignore[misc]
