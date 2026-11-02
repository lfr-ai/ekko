"""Redis client factory backing distributed rate limiting and transcript fan-out."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from redis.asyncio import Redis


class _RedisClientConfig(Protocol):
    """Configuration fields required to build the Redis client."""

    redis_url: str | None


def create_redis_client(settings: _RedisClientConfig) -> Redis | None:
    """Build a shared async Redis client, or None when Redis is not configured."""
    if settings.redis_url is None:
        return None

    from redis.asyncio import Redis as _Redis  # noqa: PLC0415

    return _Redis.from_url(settings.redis_url)
