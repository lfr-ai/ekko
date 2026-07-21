"""Common response schemas for API endpoints."""

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Health check response with status and details.

    Attributes:
        ok: Whether the health check passed.
        details: Additional health check information.
    """

    model_config = ConfigDict(frozen=True)

    ok: bool
    details: dict[str, object]


class StreamResponse(BaseModel):
    """Stream control response.

    Attributes:
        status: Current status of the stream operation.
    """

    model_config = ConfigDict(frozen=True)

    status: str
