"""Summarization request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SummarizeRequest(BaseModel):
    """Text chunks submitted for summarization."""

    model_config = ConfigDict(frozen=True)

    chunks: list[str] = Field(min_length=1)


class SummarizeResponse(BaseModel):
    """Generated summary."""

    model_config = ConfigDict(frozen=True)

    summary: str
