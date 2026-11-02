"""Health check response schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DependencyHealth(BaseModel):
    """Health status of a single dependency."""

    model_config = ConfigDict(frozen=True)

    name: str
    healthy: bool
    detail: str = ""


class ReadinessResponse(BaseModel):
    """Application dependency readiness."""

    model_config = ConfigDict(frozen=True)

    status: str
    dependencies: list[DependencyHealth] = Field(default_factory=list)
