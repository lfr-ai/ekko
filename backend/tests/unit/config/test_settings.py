"""Tests for settings configuration."""

import pytest
from pydantic import ValidationError

from ekko.config.settings import BaseAppConfig, get_settings
from ekko.config.settings.local import LocalConfig
from ekko.config.settings.test_env import TestingConfig
from ekko.core.enums import Environment


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Remove EKKO_ENVIRONMENT so pydantic-settings uses class defaults."""
    monkeypatch.delenv("EKKO_ENVIRONMENT", raising=False)


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


class TestEnvironmentConfigs:
    def test_local_debug_on(self):
        cfg = LocalConfig()
        assert cfg.debug is True
        assert cfg.environment == Environment.LOCAL

    def test_test_debug_off(self):
        cfg = TestingConfig()
        assert cfg.debug is False


class TestGetSettings:
    def test_returns_base_app_config(self):
        # get_settings is cached; just verify it returns the right type
        s = get_settings()
        assert isinstance(s, BaseAppConfig)
