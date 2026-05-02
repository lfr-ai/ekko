"""Settings module with environment-based factory.

Usage::

    from ekko.config.settings import get_settings

    settings = get_settings()
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values

from ekko.config.settings.base import BaseAppConfig
from ekko.config.settings.local import LocalConfig
from ekko.config.settings.test_env import TestingConfig
from ekko.core.enums import Environment

_ROOT_DIR = Path(__file__).resolve().parents[4]
_ENV_FILE_BY_ENV: dict[Environment, Path] = {
    Environment.TEST: _ROOT_DIR / ".env.test",
}
_LOCAL_OVERRIDE_FILE = _ROOT_DIR / ".env.local"


def _load_environment_file(*, environment: Environment) -> None:
    """Load stage-specific environment file if it exists.

    Precedence:
    1) existing process environment variables
    2) optional local override (``.env.local``)
    3) environment-specific dotenv (e.g. ``.env.test``)
    4) base ``.env``
    """
    existing_keys = set(os.environ.keys())

    base_values = dotenv_values(_ROOT_DIR / ".env")
    env_file = _ENV_FILE_BY_ENV.get(environment)
    env_values = dotenv_values(env_file) if env_file is not None and env_file.exists() else {}
    local_values = dotenv_values(_LOCAL_OVERRIDE_FILE) if _LOCAL_OVERRIDE_FILE.exists() else {}

    merged: dict[str, str] = {k: v for k, v in base_values.items() if v is not None}
    merged.update({k: v for k, v in env_values.items() if v is not None})
    merged.update({k: v for k, v in local_values.items() if v is not None})

    for key, value in merged.items():
        if key not in existing_keys:
            os.environ[key] = value


_SETTINGS_MAP: dict[Environment, type[BaseAppConfig]] = {
    Environment.LOCAL: LocalConfig,
    Environment.TEST: TestingConfig,
}


@lru_cache(maxsize=1)
def get_settings() -> BaseAppConfig:
    """Create settings instance based on ``EKKO_ENVIRONMENT`` variable.

    Defaults to LOCAL when the variable is absent. Cached so a single
    instance is reused across the process.
    """
    env_name = os.getenv("EKKO_ENVIRONMENT", Environment.LOCAL.value)
    try:
        environment = Environment(env_name.lower())
    except ValueError:
        environment = Environment.LOCAL

    _load_environment_file(environment=environment)
    settings_class = _SETTINGS_MAP[environment]
    return settings_class()


# Backwards-compatible aliases
AppSettings = BaseAppConfig
Settings = BaseAppConfig
TestConfig = TestingConfig  # Renamed to avoid pytest collection
SETTINGS = get_settings()

__all__ = [
    "SETTINGS",
    "AppSettings",
    "BaseAppConfig",
    "LocalConfig",
    "Settings",
    "TestingConfig",
    "get_settings",
]
