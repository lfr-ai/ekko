"""Tests for the rate limiter factory."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from ekko.presentation.api.rate_limiter import create_limiter


@dataclass(frozen=True, kw_only=True, slots=True)
class _FakeRateLimiterConfig:
    """Configuration stub exposing only the field the factory reads."""

    redis_url: str | None


@pytest.mark.unit
def test_create_limiter_without_redis_uses_in_memory_storage() -> None:
    """Fall back to per-process storage when Redis is not configured."""
    limiter = create_limiter(_FakeRateLimiterConfig(redis_url=None))

    assert type(limiter._storage).__name__ == "MemoryStorage"


@pytest.mark.unit
def test_create_limiter_with_redis_uses_shared_storage() -> None:
    """Share rate-limit counters across replicas via Redis when configured."""
    limiter = create_limiter(_FakeRateLimiterConfig(redis_url="redis://localhost:6379/0"))

    assert type(limiter._storage).__name__ == "RedisStorage"
