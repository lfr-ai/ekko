"""Production environment configuration."""

from ekko.config.enums import DatabaseBackend, Environment
from ekko.config.settings.base import BaseAppConfig


class ProductionConfig(BaseAppConfig):
    """Settings for production deployments."""

    environment: Environment = Environment.PROD
    debug: bool = False
    log_level: str = "WARNING"
    database_backend: DatabaseBackend = DatabaseBackend.POSTGRESQL
