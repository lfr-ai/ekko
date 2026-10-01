"""Tests for the Redis readiness adapter."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from ekko.infrastructure.clients.redis_readiness import RedisReadinessProbe


@dataclass(kw_only=True)
class _FakeRedisClient:
    """Minimal Redis client stub exposing only ``ping``."""

    should_raise: bool = False

    async def ping(self) -> bool:
        """Simulate a Redis PING, raising when configured to fail."""
        if self.should_raise:
            msg = "connection refused"
            raise ConnectionError(msg)
        return True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_with_reachable_redis_returns_healthy() -> None:
    """Report healthy when Redis responds to PING."""
    probe = RedisReadinessProbe(redis_client=_FakeRedisClient())

    result = await probe.check()

    assert result.name == "redis"
    assert result.healthy is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_with_unreachable_redis_returns_unhealthy() -> None:
    """Convert Redis connection failures into degraded readiness."""
    probe = RedisReadinessProbe(redis_client=_FakeRedisClient(should_raise=True))

    result = await probe.check()

    assert result.name == "redis"
    assert result.healthy is False
    assert result.detail
