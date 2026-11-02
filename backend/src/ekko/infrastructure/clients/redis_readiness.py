"""Redis readiness adapter for the configured cache/pub-sub connection."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from ekko.core.ports import DependencyStatus

if TYPE_CHECKING:
    from collections.abc import Awaitable

_REDIS_DEPENDENCY_NAME = "redis"

_logger = logging.getLogger(__name__)


class _RedisPingable(Protocol):
    """Structural dependency: report liveness via ``PING``."""

    def ping(self) -> Awaitable[object]:
        """Issue a Redis ``PING`` command."""
        ...


@dataclass(frozen=True, kw_only=True, slots=True)
class RedisReadinessProbe:
    """Readiness probe backed by a configured Redis client."""

    redis_client: _RedisPingable

    async def check(self) -> DependencyStatus:
        """Ping Redis and report the result as a dependency status."""
        try:
            await self.redis_client.ping()
        except Exception as exc:  # noqa: BLE001  # readiness probe reports any failure as unhealthy
            _logger.warning("Redis readiness check failed", extra={"error": str(exc)})
            return DependencyStatus(name=_REDIS_DEPENDENCY_NAME, healthy=False, detail=str(exc))

        return DependencyStatus(name=_REDIS_DEPENDENCY_NAME, healthy=True)
