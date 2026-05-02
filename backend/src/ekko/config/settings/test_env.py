"""Test environment configuration."""

from ekko.config.settings.base import BaseAppConfig
from ekko.core.enums import Environment


class TestingConfig(BaseAppConfig):
    """Settings for automated test runs."""

    environment: Environment = Environment.TEST
    debug: bool = False
    log_level: str = "WARNING"
    database_path: str = "./ekko_test.db"
