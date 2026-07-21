"""Tests for presentation health route."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ekko.presentation.api.routes.health import router


@pytest.fixture
def health_app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def health_client(health_app):
    return TestClient(health_app)


class TestHealthRoute:
    def test_health_returns_ok_false_without_state(self, health_client):
        resp = health_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        # Without lifespan, state won't have queue_manager
        assert "ok" in data
        assert "duckdb_enabled" in data["details"]
