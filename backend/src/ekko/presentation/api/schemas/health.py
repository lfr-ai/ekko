"""Health check response schemas."""

from __future__ import annotations

from pydantic import BaseModel


class DependencyHealth(BaseModel):
    """Health status of a single dependency."""

    name: str
    healthy: bool
    detail: str = ""


class HealthResponse(BaseModel):
    """Application health check response."""

    status: str
    environment: str
    dependencies: list[DependencyHealth] = []
