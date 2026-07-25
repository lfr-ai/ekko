"""Unit tests for health check response schemas."""

from __future__ import annotations

import pytest

from ekko.presentation.api.schemas.health import DependencyHealth, HealthResponse


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
class TestHealthResponse:
    """Test HealthResponse schema."""

    def test_construction_minimal(self) -> None:
        """Construct with required fields only."""
        resp = HealthResponse(status="ok", environment="local")
        assert resp.status == "ok"
        assert resp.environment == "local"
        assert resp.dependencies == []

    def test_with_dependencies(self) -> None:
        """Construct with dependency list."""
        deps = [
            DependencyHealth(name="db", healthy=True),
            DependencyHealth(name="stt", healthy=False, detail="unavailable"),
        ]
        resp = HealthResponse(status="degraded", environment="test", dependencies=deps)
        assert len(resp.dependencies) == 2
        assert resp.dependencies[1].healthy is False

    def test_serialization(self) -> None:
        """Serialize complete response."""
        resp = HealthResponse(
            status="ok",
            environment="local",
            dependencies=[DependencyHealth(name="db", healthy=True)],
        )
        data = resp.model_dump()
        assert data["status"] == "ok"
        assert len(data["dependencies"]) == 1
