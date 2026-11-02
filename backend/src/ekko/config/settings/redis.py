"""Optional Redis connection settings for multi-replica deployments."""

from __future__ import annotations

from ekko.config.settings._shared import ConfiguredSettings


class RedisSettings(ConfiguredSettings):
    """Redis connection shared by rate limiting and transcript fan-out.

    Left unset, both features fall back to single-process, in-memory
    behavior — correct only when exactly one replica is running.
    """

    redis_url: str | None = None
