"""Tests for settings configuration."""

import pytest
from pydantic import ValidationError

from ekko.config.enums import DatabaseBackend, Environment
from ekko.config.settings import BaseAppConfig, get_settings
from ekko.config.settings.dev import DevelopmentConfig
from ekko.config.settings.local import LocalConfig
from ekko.config.settings.prod import ProductionConfig
from ekko.config.settings.test_env import TestingConfig


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

    def test_sqlite_settings_present(self):
        cfg = BaseAppConfig()
        assert cfg.database_backend == DatabaseBackend.SQLITE
        assert cfg.database_path.endswith(".db")

    def test_graphql_security_defaults_present(self):
        cfg = BaseAppConfig()
        assert cfg.graphql_batch_max_operations == 5
        assert cfg.graphql_max_query_depth == 10
        assert cfg.graphql_max_alias_count == 25
        assert cfg.graphql_max_token_count == 2500
        assert cfg.graphql_enable_legacy_ws_protocol is True
        assert cfg.graphql_enable_sse_subscriptions is False


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

    def test_dev_uses_sqlite_backend(self):
        cfg = DevelopmentConfig()
        assert cfg.environment == Environment.DEV
        assert cfg.database_backend == DatabaseBackend.SQLITE

    def test_prod_uses_sqlite_backend(self):
        cfg = ProductionConfig()
        assert cfg.environment == Environment.PROD
        assert cfg.database_backend == DatabaseBackend.SQLITE

    def test_prod_disables_legacy_websocket_protocol(self):
        cfg = ProductionConfig()
        assert cfg.graphql_enable_legacy_ws_protocol is False


class TestDatabaseUrls:
    def test_sqlite_database_urls_when_backend_is_sqlite(self):
        cfg = LocalConfig(database_path="./tmp.sqlite3")
        assert cfg.database_url.startswith("sqlite+aiosqlite:///")
        assert cfg.database_sync_url.startswith("sqlite:///")


class TestGetSettings:
    def test_returns_base_app_config(self):
        # get_settings is cached; just verify it returns the right type
        s = get_settings()
        assert isinstance(s, BaseAppConfig)
