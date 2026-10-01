"""Tests for the Redis client factory."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from ekko.infrastructure.clients.redis import create_redis_client


@dataclass(frozen=True, kw_only=True, slots=True)
class _FakeRedisClientConfig:
    """Configuration stub exposing only the field the factory reads."""

    redis_url: str | None


@pytest.mark.unit
def test_create_redis_client_without_url_returns_none() -> None:
    """Skip Redis client construction when no URL is configured."""
    client = create_redis_client(_FakeRedisClientConfig(redis_url=None))

    assert client is None


@pytest.mark.unit
def test_create_redis_client_with_url_returns_client() -> None:
    """Build a Redis client bound to the configured URL."""
    client = create_redis_client(_FakeRedisClientConfig(redis_url="redis://localhost:6379/0"))

    assert client is not None
