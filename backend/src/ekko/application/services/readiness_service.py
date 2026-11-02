"""Application-layer orchestration for dependency readiness checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ekko.core.ports import DependencyStatus, ReadinessProbe


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class ReadinessService:
    """Application service for external dependency readiness."""

    database_probe: ReadinessProbe | None
    redis_probe: ReadinessProbe | None = None

    async def check_database(self) -> DependencyStatus:
        """Check database readiness without exposing adapter details."""
        if self.database_probe is None:
            return DependencyStatus(name="database", healthy=False, detail="not configured")
        return await self.database_probe.check()

    async def check_redis(self) -> DependencyStatus:
        """Check Redis readiness without exposing adapter details.

        Redis is an optional dependency: absent configuration is healthy, not
        degraded, since single-replica deployments do not require it.

        Returns:
            DependencyStatus: Redis readiness and diagnostic detail.
        """
        if self.redis_probe is None:
            return DependencyStatus(name="redis", healthy=True, detail="not configured")
        return await self.redis_probe.check()
