"""Test environment configuration."""

from __future__ import annotations

from typing import final

from ekko.config.base import BaseAppConfig
from ekko.config.enums import DatabaseBackend, Environment


@final
class TestConfig(BaseAppConfig):
    """Settings for automated test runs."""

    __test__ = False  # not a pytest test class, despite the Test* name

    environment: Environment = Environment.TEST
    debug: bool = False
    log_level: str = "WARNING"
    database_backend: DatabaseBackend = DatabaseBackend.SQLITE
    database_path: str = "./ekko_test.db"
    graphql_enable_ide: bool = False
