"""Test environment configuration."""

from ekko.config.enums import DatabaseBackend, Environment
from ekko.config.settings.base import BaseAppConfig


class TestingConfig(BaseAppConfig):
    """Settings for automated test runs."""

    __test__ = False

    environment: Environment = Environment.TEST
    debug: bool = False
    log_level: str = "WARNING"
    database_backend: DatabaseBackend = DatabaseBackend.SQLITE
    database_path: str = "./ekko_test.db"
