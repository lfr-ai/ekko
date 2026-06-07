"""Local development configuration."""

from ekko.config.enums import DatabaseBackend, Environment
from ekko.config.settings.base import BaseAppConfig


class LocalConfig(BaseAppConfig):
    """Settings for local developer machines."""

    environment: Environment = Environment.LOCAL
    debug: bool = True
    log_level: str = "DEBUG"
    database_backend: DatabaseBackend = DatabaseBackend.SQLITE
