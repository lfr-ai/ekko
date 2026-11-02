"""Transcript segment value object."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Final

SOURCE_MICROPHONE: Final[str] = "microphone"
SOURCE_SYSTEM: Final[str] = "system"


@dataclass(frozen=True, kw_only=True, slots=True)
class TranscriptSegment:
    """A segment of transcribed audio with timing info."""

    text: str = ""
    start_seconds: float = 0.0
    end_seconds: float = 0.0
    confidence: float = 0.0
    source: str = SOURCE_MICROPHONE
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
