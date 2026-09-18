"""Runtime configuration resolution.

Resolves the active environment from the ``EKKO_ENVIRONMENT`` variable and
exposes the shared runtime constants and configuration factory used during
settings construction.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ekko.config.enums import Environment

if TYPE_CHECKING:
    from ekko.config.base import BaseAppConfig

_ROOT_PARENT_LEVEL = 3
ROOT_DIR_PATH: Final[Path] = Path(__file__).resolve().parents[_ROOT_PARENT_LEVEL]


def _resolve_runtime_environment() -> Environment:
    """Resolve runtime environment from the ``EKKO_ENVIRONMENT`` variable.

    Returns:
        Environment: Resolved environment enum. Defaults to LOCAL.
    """
    env_name = os.getenv("EKKO_ENVIRONMENT", Environment.LOCAL.value)
    try:
        return Environment(env_name.lower())
    except ValueError:
        return Environment.LOCAL


ENV: Final[Environment] = _resolve_runtime_environment()


@lru_cache(maxsize=1)
def get_config() -> BaseAppConfig:
    """Get the active configuration instance for the resolved environment.

    Cached so a single instance is reused across the process.

    Returns:
        BaseAppConfig: Configuration instance for the active environment.
    """
    from ekko.config.environments.dev import DevelopmentConfig
    from ekko.config.environments.local import LocalConfig
    from ekko.config.environments.prod import ProductionConfig
    from ekko.config.environments.test_env import TestingConfig

    config_map: dict[Environment, type[BaseAppConfig]] = {
        Environment.LOCAL: LocalConfig,
        Environment.TEST: TestingConfig,
        Environment.DEV: DevelopmentConfig,
        Environment.PROD: ProductionConfig,
    }

    return config_map[ENV]()
