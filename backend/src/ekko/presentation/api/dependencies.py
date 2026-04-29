"""FastAPI dependency injection functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import Request

    from ekko.core.interfaces.auth import JWTPort

from ekko.config.settings import BaseAppConfig, get_settings


def get_app_settings() -> BaseAppConfig:
    """Dependency that returns the cached application settings."""
    return get_settings()


def get_jwt_adapter(request: Request) -> JWTPort:
    """Dependency that returns the JWT adapter from the DI container."""
    return request.app.state.container.jwt_adapter
