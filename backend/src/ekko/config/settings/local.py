"""Local development configuration."""

from typing import final

from pydantic_settings import SettingsConfigDict

from ekko.config.enums import DatabaseBackend, Environment
from ekko.config.runtime import ROOT_DIR
from ekko.config.settings.base import BaseAppConfig


@final
class LocalConfig(BaseAppConfig):
    """Settings for local developer machines."""

    model_config = SettingsConfigDict(
        env_file=(
            ROOT_DIR / ".env",
            ROOT_DIR / ".env.local",
        ),
    )

    environment: Environment = Environment.LOCAL
    debug: bool = True
    log_level: str = "DEBUG"
    database_backend: DatabaseBackend = DatabaseBackend.SQLITE
