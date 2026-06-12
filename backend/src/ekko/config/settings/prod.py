"""Production environment configuration."""

from typing import final

from pydantic_settings import SettingsConfigDict

from ekko.config.enums import DatabaseBackend, Environment
from ekko.config.runtime import ROOT_DIR
from ekko.config.settings.base import BaseAppConfig


@final
class ProductionConfig(BaseAppConfig):
    """Settings for production deployments."""

    model_config = SettingsConfigDict(
        env_file=(
            ROOT_DIR / ".env",
            ROOT_DIR / ".env.prod",
        ),
    )

    environment: Environment = Environment.PROD
    debug: bool = False
    log_level: str = "WARNING"
    database_backend: DatabaseBackend = DatabaseBackend.POSTGRESQL
