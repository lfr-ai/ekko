"""Messaging and queue-related enums."""

from __future__ import annotations

from enum import auto, unique

from ekko.core.enums.base import ParseableEnum


@unique
class QueueName(ParseableEnum):
    TRANSCRIPTS = auto()
    COMMANDS = auto()
    EVENTS = auto()
    METRICS = auto()


@unique
class RecognitionMode(ParseableEnum):
    """Recognition mode identifying the speaker source."""

    ADVISOR = auto()
    CUSTOMER = auto()

    @classmethod
    def from_stream_type(cls, stream_type: str) -> RecognitionMode:
        """Map stream type string to RecognitionMode.

        Args:
            stream_type: Type of stream ("sys" or "mic").

        Raises:
            ValueError: If stream_type is not "sys" or "mic".
        """
        mapping = {"sys": cls.CUSTOMER, "mic": cls.ADVISOR}
        if stream_type not in mapping:
            msg = f"Invalid stream type: {stream_type!r}. Expected 'sys' or 'mic'."
            raise ValueError(msg)
        return mapping[stream_type]


@unique
class TranscriptStatus(ParseableEnum):
    RECEIVED = auto()
    QUEUED = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@unique
class MessageRole(ParseableEnum):
    SYSTEM = auto()
    USER = auto()
    ASSISTANT = auto()
    TOOL = auto()


__all__ = ["MessageRole", "QueueName", "RecognitionMode", "TranscriptStatus"]
