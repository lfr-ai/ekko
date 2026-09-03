"""Tests for canonical REST stream-control routes."""

from __future__ import annotations

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from ekko.presentation.api.routes.stream import router


class _FakeStreamController:
    """Async-compatible stream controller test double."""

    def __init__(self):
        self.commands: list[str] = []
        self.device_check_calls = 0

    async def device_check(self) -> None:
        self.device_check_calls += 1

    async def send_command(self, command: str) -> None:
        self.commands.append(command)


def _build_stream_client() -> tuple[TestClient, _FakeStreamController]:
    app = FastAPI()
    app.include_router(router)
    controller = _FakeStreamController()
    app.state.controller = controller
    return TestClient(app), controller


def test_start_stream_invokes_controller() -> None:
    """Start audio through the canonical REST command."""
    client, controller = _build_stream_client()

    response = client.post("/stream/start")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "started"}
    assert controller.device_check_calls == 1
    assert controller.commands == ["start_stream"]


def test_pause_stream_invokes_controller() -> None:
    """Pause audio through the canonical REST command."""
    client, controller = _build_stream_client()

    response = client.post("/stream/pause")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "paused"}
    assert controller.device_check_calls == 0
    assert controller.commands == ["pause_stream"]


def test_start_stream_without_controller_is_unavailable() -> None:
    """Describe missing audio runtime with HTTP availability semantics."""
    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).post("/stream/start")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {"detail": "Stream controller unavailable"}
