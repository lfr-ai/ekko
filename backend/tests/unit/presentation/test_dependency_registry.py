"""Unit tests for FastAPI dependency injection registry."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient

from ekko.presentation.api.dependency_registry import (
    _get_config,
    _get_container,
)


@pytest.fixture
def app_with_container() -> FastAPI:
    """Create test app with container attached to state."""
    app = FastAPI()
    container = MagicMock()
    container.settings = MagicMock()
    container.settings.app_name = "ekko-test"
    app.state.container = container
    return app


@pytest.fixture
def app_without_container() -> FastAPI:
    """Create test app without container."""
    return FastAPI()


@pytest.mark.unit
class TestGetContainer:
    """Test _get_container dependency."""

    def test_returns_container_from_state(self, app_with_container: FastAPI) -> None:
        """Return container when attached to app state."""

        @app_with_container.get("/test")
        async def _endpoint(request: Request) -> dict[str, bool]:
            _get_container(request)
            return {"ok": True}

        client = TestClient(app_with_container)
        response = client.get("/test")
        assert response.status_code == status.HTTP_200_OK

    def test_raises_when_container_missing(self, app_without_container: FastAPI) -> None:
        """Raise RuntimeError when container not initialized."""

        @app_without_container.get("/test")
        async def _endpoint(request: Request) -> dict[str, bool]:
            _get_container(request)
            return {"ok": True}

        client = TestClient(app_without_container, raise_server_exceptions=False)
        response = client.get("/test")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.unit
class TestGetConfig:
    """Test _get_config dependency."""

    def test_returns_settings_from_container(self, app_with_container: FastAPI) -> None:
        """Return settings object from container."""

        @app_with_container.get("/test")
        async def _endpoint(request: Request) -> dict[str, object]:
            config = _get_config(_get_container(request))
            return {"name": config.app_name}

        client = TestClient(app_with_container)
        response = client.get("/test")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "ekko-test"
