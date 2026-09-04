"""Tests for readiness orchestration at the application boundary."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from ekko.application.services.readiness_service import ReadinessService
from ekko.core.ports import DependencyStatus


@dataclass(frozen=True, slots=True)
class FakeReadinessProbe:
    """Readiness probe returning a configured status."""

    status: DependencyStatus

    async def check(self) -> DependencyStatus:
        """Return the configured dependency status."""
        return self.status


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_database_without_probe_reports_not_configured() -> None:
    """Describe an absent database probe without raising."""
    service = ReadinessService(database_probe=None)

    result = await service.check_database()

    assert result == DependencyStatus(name="database", healthy=False, detail="not configured")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_database_with_healthy_probe_returns_probe_status() -> None:
    """Return a healthy database status from the configured probe."""
    expected = DependencyStatus(name="database", healthy=True)
    service = ReadinessService(database_probe=FakeReadinessProbe(status=expected))

    result = await service.check_database()

    assert result == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_database_with_unhealthy_probe_preserves_diagnostic_detail() -> None:
    """Return an unhealthy database status with its diagnostic detail."""
    expected = DependencyStatus(name="database", healthy=False, detail="connection refused")
    service = ReadinessService(database_probe=FakeReadinessProbe(status=expected))

    result = await service.check_database()

    assert result == expected
