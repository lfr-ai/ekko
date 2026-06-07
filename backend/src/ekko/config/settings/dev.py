"""Development environment configuration."""

from ekko.config.enums import DatabaseBackend, Environment
from ekko.config.settings.base import BaseAppConfig


class DevelopmentConfig(BaseAppConfig):
    """Settings for shared development environments."""

    environment: Environment = Environment.DEV
    debug: bool = True
    log_level: str = "INFO"
    database_backend: DatabaseBackend = DatabaseBackend.POSTGRESQL
