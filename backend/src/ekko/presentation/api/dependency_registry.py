"""FastAPI dependency injection wiring for the presentation layer."""

from __future__ import annotations

from typing import Annotated, Protocol, cast

from fastapi import Depends, Request

from ekko.config.settings import BaseAppConfig


class _ContainerProtocol(Protocol):
    """Structural container contract consumed by presentation dependencies."""

    settings: BaseAppConfig


def _get_container(request: Request) -> _ContainerProtocol:
    """Get composition root container from application state.

    Args:
        request (Request): Incoming HTTP request.

    Returns:
        _ContainerProtocol: Application composition root.

    Raises:
        RuntimeError: If container is not attached to app state.
    """
    if not hasattr(request.app.state, "container"):
        raise RuntimeError("Application container is not initialized")
    return cast("_ContainerProtocol", request.app.state.container)


type ContainerDep = Annotated[_ContainerProtocol, Depends(_get_container)]


def _get_config(container: Annotated[_ContainerProtocol, Depends(_get_container)]) -> BaseAppConfig:
    """Get shared application configuration from container.

    Args:
        container: Injected composition root.

    Returns:
        BaseAppConfig: Application configuration.
    """
    return container.settings


type ConfigDep = Annotated[BaseAppConfig, Depends(_get_config)]
