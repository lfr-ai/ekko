"""Development environment configuration."""

from typing import final

from pydantic_settings import SettingsConfigDict

from ekko.config.enums import DatabaseBackend, Environment
from ekko.config.runtime import ROOT_DIR
from ekko.config.settings.base import BaseAppConfig


@final
class DevelopmentConfig(BaseAppConfig):
    """Settings for shared development environments."""

    model_config = SettingsConfigDict(
        env_file=(
            ROOT_DIR / ".env",
            ROOT_DIR / ".env.dev",
        ),
    )

    environment: Environment = Environment.DEV
    debug: bool = True
    log_level: str = "INFO"
    database_backend: DatabaseBackend = DatabaseBackend.POSTGRESQL
