"""Common transcript fixtures for testing.

Provides pre-built transcript scenarios for consistent testing.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from ekko.core.entities import Transcript
from ekko.core.enums import TranscriptStatus

# Sample conversation ID from conversations fixture
SAMPLE_CONVERSATION_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")

# Various transcript status examples
TRANSCRIPT_RECEIVED = Transcript(
    id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    conversation_id=SAMPLE_CONVERSATION_ID,
    text="Hello, how can I help you today?",
    source="microphone",
    status=TranscriptStatus.RECEIVED,
    confidence=0.95,
    created_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
)

TRANSCRIPT_COMPLETED = Transcript(
    id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
    conversation_id=SAMPLE_CONVERSATION_ID,
    text="I need assistance with my project requirements.",
    source="microphone",
    status=TranscriptStatus.COMPLETED,
    confidence=0.98,
    created_at=datetime(2024, 1, 1, 10, 0, 5, tzinfo=UTC),
)

TRANSCRIPT_LOW_CONFIDENCE = Transcript(
    id=uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
    conversation_id=SAMPLE_CONVERSATION_ID,
    text="[unclear audio]",
    source="microphone",
    status=TranscriptStatus.RECEIVED,
    confidence=0.25,
    created_at=datetime(2024, 1, 1, 10, 0, 10, tzinfo=UTC),
)

TRANSCRIPT_FAILED = Transcript(
    id=uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
    conversation_id=SAMPLE_CONVERSATION_ID,
    text="",
    source="microphone",
    status=TranscriptStatus.FAILED,
    confidence=0.0,
    created_at=datetime(2024, 1, 1, 10, 0, 15, tzinfo=UTC),
)

# Collection of all transcript fixtures for iteration
ALL_TRANSCRIPT_FIXTURES = [
    TRANSCRIPT_RECEIVED,
    TRANSCRIPT_COMPLETED,
    TRANSCRIPT_LOW_CONFIDENCE,
    TRANSCRIPT_FAILED,
]


__all__ = [
    "ALL_TRANSCRIPT_FIXTURES",
    "TRANSCRIPT_COMPLETED",
    "TRANSCRIPT_FAILED",
    "TRANSCRIPT_LOW_CONFIDENCE",
    "TRANSCRIPT_RECEIVED",
]
