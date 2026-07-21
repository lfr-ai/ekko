"""Shared test fixtures and data.

Provides pre-built domain entity instances for consistent testing.
"""

from __future__ import annotations

from tests.fixtures.conversations import (
    ACTIVE_CONVERSATION,
    COMPLETED_CONVERSATION,
    SAMPLE_CONVERSATION_ID,
    SAMPLE_MESSAGES,
    SAMPLE_USER_ID,
)
from tests.fixtures.transcripts import (
    ALL_TRANSCRIPT_FIXTURES,
    TRANSCRIPT_COMPLETED,
    TRANSCRIPT_FAILED,
    TRANSCRIPT_LOW_CONFIDENCE,
    TRANSCRIPT_RECEIVED,
)

__all__ = [
    "ACTIVE_CONVERSATION",
    "ALL_TRANSCRIPT_FIXTURES",
    "COMPLETED_CONVERSATION",
    "SAMPLE_CONVERSATION_ID",
    "SAMPLE_MESSAGES",
    "SAMPLE_USER_ID",
    "TRANSCRIPT_COMPLETED",
    "TRANSCRIPT_FAILED",
    "TRANSCRIPT_LOW_CONFIDENCE",
    "TRANSCRIPT_RECEIVED",
]
