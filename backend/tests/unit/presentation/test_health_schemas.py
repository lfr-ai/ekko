"""Unit tests for health check response schemas."""

from __future__ import annotations

import pytest

from ekko.presentation.api.schemas.health import DependencyHealth, ReadinessResponse


@pytest.mark.unit
class TestDependencyHealth:
    """Test DependencyHealth schema."""

    def test_construction(self) -> None:
        """Construct with name and status."""
        dep = DependencyHealth(name="database", healthy=True)
        assert dep.name == "database"
        assert dep.healthy is True
        assert dep.detail == ""

    def test_with_detail(self) -> None:
        """Construct with optional detail."""
        dep = DependencyHealth(name="redis", healthy=False, detail="Connection refused")
        assert dep.detail == "Connection refused"

    def test_serialization(self) -> None:
        """Serialize to dict."""
        dep = DependencyHealth(name="llm", healthy=True, detail="ok")
        data = dep.model_dump()
        assert data == {"name": "llm", "healthy": True, "detail": "ok"}


@pytest.mark.unit
class TestReadinessResponse:
    """Test ReadinessResponse schema."""

    def test_construction_minimal(self) -> None:
        """Construct with required fields only."""
        resp = ReadinessResponse(status="healthy")
        assert resp.status == "healthy"
        assert resp.dependencies == []

    def test_with_dependencies(self) -> None:
        """Construct with dependency list."""
        deps = [
            DependencyHealth(name="db", healthy=True),
            DependencyHealth(name="stt", healthy=False, detail="unavailable"),
        ]
        resp = ReadinessResponse(status="degraded", dependencies=deps)
        assert len(resp.dependencies) == 2
        assert resp.dependencies[1].healthy is False

    def test_serialization(self) -> None:
        """Serialize complete response."""
        resp = ReadinessResponse(
            status="healthy",
            dependencies=[DependencyHealth(name="db", healthy=True)],
        )
        data = resp.model_dump()
        assert data["status"] == "healthy"
        assert len(data["dependencies"]) == 1
