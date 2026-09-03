"""Tests for the SQLAlchemy database readiness adapter."""

from __future__ import annotations

import pytest

from ekko.infrastructure.db.readiness import SQLAlchemyReadinessProbe


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_with_available_sqlite_database_returns_healthy() -> None:
    """Report healthy when a database accepts the readiness query."""
    probe = SQLAlchemyReadinessProbe(database_url="sqlite+aiosqlite://")

    result = await probe.check()

    assert result.name == "database"
    assert result.healthy is True
    assert result.detail == ""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_with_invalid_database_url_returns_unhealthy() -> None:
    """Convert database configuration failures into degraded readiness."""
    probe = SQLAlchemyReadinessProbe(database_url="unknown-driver://invalid")

    result = await probe.check()

    assert result.name == "database"
    assert result.healthy is False
    assert result.detail
