"""Test environment configuration."""

from ekko.config.enums import Environment
from ekko.config.settings.base import BaseAppConfig


class TestingConfig(BaseAppConfig):
    """Settings for automated test runs."""

    __test__ = False

    environment: Environment = Environment.TEST
    debug: bool = False
    log_level: str = "WARNING"
    database_path: str = "./ekko_test.db"
