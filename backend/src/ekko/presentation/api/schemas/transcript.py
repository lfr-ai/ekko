"""Live transcript API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TranscriptResponse(BaseModel):
    """One live transcript segment."""

    model_config = ConfigDict(frozen=True)

    text: str
    source: str
    timestamp: datetime
