"""Domain events representing significant facts in the voice assistant domain.

Events are named in past tense and represent immutable facts about what
happened in the domain. They use only primitive/serializable field types.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, kw_only=True, slots=True)
class ConversationStarted:
    """Domain event: a new voice conversation session was started.

    Attributes:
        conversation_id (UUID): Identifier of the started conversation.
        source (str): Audio source that initiated the conversation.
        occurred_at (datetime): Timestamp when the event occurred.
    """

    conversation_id: UUID
    source: str
    occurred_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class ConversationEnded:
    """Domain event: a voice conversation session was ended.

    Attributes:
        conversation_id (UUID): Identifier of the ended conversation.
        duration_seconds (float): Total duration of the conversation.
        occurred_at (datetime): Timestamp when the event occurred.
    """

    conversation_id: UUID
    duration_seconds: float
    occurred_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class TranscriptReceived:
    """Domain event: a speech-to-text transcript was received.

    Attributes:
        transcript_id (UUID): Identifier of the transcript.
        conversation_id (UUID): Identifier of the parent conversation.
        text (str): Transcribed text content.
        confidence (float): Confidence score from the STT engine.
        occurred_at (datetime): Timestamp when the event occurred.
    """

    transcript_id: UUID
    conversation_id: UUID
    text: str
    confidence: float
    occurred_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class SummaryGenerated:
    """Domain event: an AI summary was generated for a conversation.

    Attributes:
        conversation_id (UUID): Identifier of the summarized conversation.
        summary_text (str): Generated summary content.
        occurred_at (datetime): Timestamp when the event occurred.
    """

    conversation_id: UUID
    summary_text: str
    occurred_at: datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class PIIDetected:
    """Domain event: PII was detected in text before sending to LLM.

    Attributes:
        conversation_id (UUID): Identifier of the conversation.
        entity_count (int): Number of PII entities detected.
        occurred_at (datetime): Timestamp when the event occurred.
    """

    conversation_id: UUID
    entity_count: int
    occurred_at: datetime
