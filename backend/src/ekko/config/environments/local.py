"""Local development configuration."""

from __future__ import annotations

from typing import final

from pydantic_settings import SettingsConfigDict

from ekko.config.base import BaseAppConfig
from ekko.config.enums import DatabaseBackend, Environment
from ekko.config.runtime import ROOT_DIR_PATH


@final
class LocalConfig(BaseAppConfig):
    """Settings for local developer machines."""

    model_config = SettingsConfigDict(
        env_file=(
            ROOT_DIR_PATH / ".env",
            ROOT_DIR_PATH / ".env.local",
        ),
    )

    environment: Environment = Environment.LOCAL
    debug: bool = True
    log_level: str = "DEBUG"
    database_backend: DatabaseBackend = DatabaseBackend.SQLITE
    graphql_enable_ide: bool = True
