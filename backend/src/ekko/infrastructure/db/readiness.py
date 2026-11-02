"""SQLAlchemy readiness adapter for the configured database."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import text

from ekko.core.ports import DependencyStatus
from ekko.infrastructure.db import create_engine

_DATABASE_DEPENDENCY_NAME = "database"
_READINESS_QUERY = "SELECT 1"

_logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True, slots=True)
class SQLAlchemyReadinessProbe:
    """Database readiness probe backed by a configured SQLAlchemy URL."""

    database_url: str

    async def check(self) -> DependencyStatus:
        """Open, probe, and dispose a short-lived database connection."""
        engine = None
        try:
            engine = create_engine(self.database_url)
            async with engine.connect() as connection:
                await connection.execute(text(_READINESS_QUERY))
        except Exception as exc:  # noqa: BLE001  # readiness probe reports any failure as unhealthy
            _logger.warning("Database readiness check failed", extra={"error": str(exc)})
            return DependencyStatus(name=_DATABASE_DEPENDENCY_NAME, healthy=False, detail=str(exc))
        finally:
            if engine is not None:
                await engine.dispose()

        return DependencyStatus(name=_DATABASE_DEPENDENCY_NAME, healthy=True)
