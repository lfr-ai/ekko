"""Tests for settings configuration."""

import pytest
from pydantic import ValidationError

from ekko.config.enums import DatabaseBackend
from ekko.config.settings import BaseAppConfig, get_settings
from ekko.config.settings.dev import DevelopmentConfig
from ekko.config.settings.local import LocalConfig
from ekko.config.settings.prod import ProductionConfig
from ekko.config.settings.test_env import TestingConfig
from ekko.core.enums import Environment


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Remove EKKO_ENVIRONMENT so pydantic-settings uses class defaults."""
    get_settings.cache_clear()
    monkeypatch.delenv("EKKO_ENVIRONMENT", raising=False)
    yield
    get_settings.cache_clear()


class TestBaseAppConfig:
    def test_default_environment(self):
        cfg = BaseAppConfig()
        assert cfg.environment == Environment.LOCAL

    def test_default_host(self):
        cfg = BaseAppConfig()
        assert cfg.host == "127.0.0.1"

    def test_frozen(self):
        cfg = BaseAppConfig()
        with pytest.raises(ValidationError):
            cfg.host = "0.0.0.0"  # noqa: S104

    def test_audio_settings_present(self):
        cfg = BaseAppConfig()
        assert cfg.audio_streamer_tcp_port == 6600
        assert cfg.audio_frames_per_buffer == 1024
        assert cfg.audio_channels == 2
        assert cfg.max_read_bytes == 100
        assert cfg.wait_timeout_seconds == 2
        assert cfg.sleep_delay_seconds == 0.1

    def test_duckdb_settings_present(self):
        cfg = BaseAppConfig()
        assert isinstance(cfg.duckdb_enabled, bool)
        assert cfg.duckdb_database_path.endswith(".duckdb")


class TestEnvironmentConfigs:
    def test_local_debug_on(self):
        cfg = LocalConfig()
        assert cfg.debug is True
        assert cfg.environment == Environment.LOCAL

    def test_test_debug_off(self):
        cfg = TestingConfig()
        assert cfg.debug is False

    def test_local_uses_sqlite_backend(self):
        cfg = LocalConfig()
        assert cfg.database_backend == DatabaseBackend.SQLITE

    def test_test_uses_sqlite_backend(self):
        cfg = TestingConfig()
        assert cfg.database_backend == DatabaseBackend.SQLITE

    def test_dev_uses_postgresql_backend(self):
        cfg = DevelopmentConfig()
        assert cfg.environment == Environment.DEV
        assert cfg.database_backend == DatabaseBackend.POSTGRESQL

    def test_prod_uses_postgresql_backend(self):
        cfg = ProductionConfig()
        assert cfg.environment == Environment.PROD
        assert cfg.database_backend == DatabaseBackend.POSTGRESQL


class TestDatabaseUrls:
    def test_sqlite_database_urls_when_backend_is_sqlite(self):
        cfg = LocalConfig(database_path="./tmp.sqlite3")
        assert cfg.database_url.startswith("sqlite+aiosqlite:///")
        assert cfg.database_sync_url.startswith("sqlite:///")

    def test_postgresql_database_urls_when_backend_is_postgresql(self):
        cfg = DevelopmentConfig(
            postgresql_host="db.internal",
            postgresql_port=5439,
            postgresql_name="ekko_dev",
            postgresql_user="ekko_user",
            postgresql_password="test-password",
            postgresql_sslmode="require",
        )
        assert cfg.database_url.startswith("postgresql+asyncpg://ekko_user:test-password@db.internal:5439/ekko_dev")
        assert cfg.database_url.endswith("sslmode=require")
        assert cfg.database_sync_url.startswith(
            "postgresql+psycopg://ekko_user:test-password@db.internal:5439/ekko_dev"
        )

    def test_postgresql_database_urls_support_overrides(self):
        cfg = DevelopmentConfig(
            postgresql_async_database_url_override="postgresql+asyncpg://custom/source",
            postgresql_sync_database_url_override="postgresql+psycopg://custom/sync",
        )
        assert cfg.postgresql_async_database_url == "postgresql+asyncpg://custom/source"
        assert cfg.postgresql_sync_database_url == "postgresql+psycopg://custom/sync"


class TestGetSettings:
    def test_returns_base_app_config(self):
        # get_settings is cached; just verify it returns the right type
        s = get_settings()
        assert isinstance(s, BaseAppConfig)
