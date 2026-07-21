"""Tests for legacy REST stream routes.

These routes remain available only when explicitly enabled and should emit
migration guidance toward GraphQL.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ekko.presentation.api.routes.stream import router


class _FakeStreamController:
    """Simple async-compatible stream controller test double."""

    def __init__(self) -> None:
        self.commands: list[str] = []
        self.device_check_calls = 0

    async def device_check(self) -> None:
        self.device_check_calls += 1

    async def send_command(self, command: str) -> None:
        self.commands.append(command)


def _build_stream_client() -> tuple[TestClient, _FakeStreamController]:
    """Create a test client with stream routes and fake app controller."""
    app = FastAPI()
    app.include_router(router)

    controller = _FakeStreamController()
    app.state.controller = controller

    return TestClient(app), controller


def test_start_stream_when_called_then_returns_status_and_deprecation_headers() -> None:
    """Start route should preserve behavior and emit migration metadata headers."""
    client, controller = _build_stream_client()

    response = client.post("/start_stream")

    assert response.status_code == 200
    assert response.json() == {"status": "started"}
    assert response.headers["deprecation"] == "true"
    assert response.headers["link"] == '</graphql>; rel="successor-version"; title="GraphQL endpoint"'
    assert "deprecated" in response.headers["warning"].lower()
    assert "controlstream" in response.headers["warning"].lower()
    assert response.headers["sunset"] == "2027-01-31T00:00:00Z"
    assert response.headers["x-api-removal-target"] == "2027-04-30T00:00:00Z"
    assert controller.device_check_calls == 1
    assert controller.commands == ["start_stream"]


def test_pause_stream_when_called_then_returns_status_and_deprecation_headers() -> None:
    """Pause route should preserve behavior and emit migration metadata headers."""
    client, controller = _build_stream_client()

    response = client.post("/pause_stream")

    assert response.status_code == 200
    assert response.json() == {"status": "paused"}
    assert response.headers["deprecation"] == "true"
    assert response.headers["link"] == '</graphql>; rel="successor-version"; title="GraphQL endpoint"'
    assert "deprecated" in response.headers["warning"].lower()
    assert "controlstream" in response.headers["warning"].lower()
    assert response.headers["sunset"] == "2027-01-31T00:00:00Z"
    assert response.headers["x-api-removal-target"] == "2027-04-30T00:00:00Z"
    assert controller.device_check_calls == 0
    assert controller.commands == ["pause_stream"]
