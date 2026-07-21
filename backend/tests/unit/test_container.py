"""Tests for the DI container."""

from ekko.composition.container import Container
from ekko.config.settings import BaseAppConfig


class TestContainer:
    def test_from_config(self):
        container = Container.from_config()
        assert isinstance(container.settings, BaseAppConfig)

    def test_settings_injection(self):
        settings = BaseAppConfig()
        container = Container(settings=settings)
        assert container.settings is settings
