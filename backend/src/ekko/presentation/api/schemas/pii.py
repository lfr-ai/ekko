"""PII anonymization API schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PIIAnonymizeRequest(BaseModel):
    """Text submitted for PII anonymization."""

    model_config = ConfigDict(frozen=True)

    text: str = Field(min_length=1)


class PIIAnonymizeResponse(BaseModel):
    """Anonymized text and detection summary."""

    model_config = ConfigDict(frozen=True)

    anonymized_text: str
    pii_found: bool
    match_count: int
