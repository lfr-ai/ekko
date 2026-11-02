"""API rate-limiting configuration."""

from __future__ import annotations

from typing import Final, Protocol

from slowapi import Limiter
from slowapi.util import get_remote_address

RATE_LIMIT_DEFAULT: Final[str] = "30/second"


class _RateLimiterConfig(Protocol):
    """Configuration fields required to build the rate limiter."""

    redis_url: str | None


def create_limiter(settings: _RateLimiterConfig) -> Limiter:
    """Build a limiter sharing state via Redis when configured.

    Without a configured Redis URL, falls back to per-process in-memory
    counters — correct only when a single replica is running.

    Args:
        settings (_RateLimiterConfig): Redis URL and rate-limiter settings.

    Returns:
        Limiter: Configured SlowAPI limiter.
    """
    return Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)
