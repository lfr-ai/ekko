"""FastAPI dependency injection functions."""

from __future__ import annotations

from ekko.config.settings import BaseAppConfig, get_settings


def get_app_settings() -> BaseAppConfig:
    """Dependency that returns the cached application settings."""
    return get_settings()
