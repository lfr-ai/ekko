"""Settings module with environment-based factory.

Usage::

    from ekko.config.settings import get_settings

    settings = get_settings()
"""

from __future__ import annotations

from functools import lru_cache
from typing import Final

from ekko.config.enums import Environment
from ekko.config.runtime import ENV
from ekko.config.settings.base import BaseAppConfig
from ekko.config.settings.dev import DevelopmentConfig
from ekko.config.settings.local import LocalConfig
from ekko.config.settings.prod import ProductionConfig
from ekko.config.settings.test_env import TestingConfig

_SETTINGS_MAP: Final[dict[Environment, type[BaseAppConfig]]] = {
    Environment.DEV: DevelopmentConfig,
    Environment.LOCAL: LocalConfig,
    Environment.PROD: ProductionConfig,
    Environment.TEST: TestingConfig,
}


@lru_cache(maxsize=1)
def get_settings() -> BaseAppConfig:
    """Create settings instance based on resolved runtime environment.

    Cached so a single instance is reused across the process.
    """
    settings_class = _SETTINGS_MAP[ENV]
    return settings_class()


__all__ = [
    "BaseAppConfig",
    "DevelopmentConfig",
    "LocalConfig",
    "ProductionConfig",
    "TestingConfig",
    "get_settings",
]
