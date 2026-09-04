"""Integration tests for canonical REST command endpoints."""

from __future__ import annotations

import pytest
from fastapi import status

pytestmark = pytest.mark.integration


class _FakeStreamController:
    """Stream controller test double for composed API tests."""

    def __init__(self):
        self.commands: list[str] = []
        self.device_check_calls = 0

    async def device_check(self) -> None:
        self.device_check_calls += 1

    async def send_command(self, command: str) -> None:
        self.commands.append(command)

    async def stop(self) -> None:
        """Complete the application-owned controller lifecycle."""


def test_pii_anonymization_uses_rest(integration_client) -> None:
    """Redact sensitive text through the canonical REST API."""
    response = integration_client.post(
        "/pii/anonymize",
        json={"text": "Contact integration-test@example.com"},
    )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["pii_found"] is True
    assert payload["match_count"] == 1
    assert "integration-test@example.com" not in payload["anonymized_text"]


def test_stream_commands_use_rest(integration_client) -> None:
    """Start and pause audio through canonical REST commands."""
    controller = _FakeStreamController()
    integration_client.app.state.controller = controller

    start_response = integration_client.post("/stream/start")
    pause_response = integration_client.post("/stream/pause")

    assert start_response.status_code == status.HTTP_200_OK
    assert pause_response.status_code == status.HTTP_200_OK
    assert controller.device_check_calls == 1
    assert controller.commands == ["start_stream", "pause_stream"]


def test_retired_api_contracts_are_absent(integration_client) -> None:
    """Keep removed compatibility endpoints out of the composed app."""
    assert integration_client.post("/start_stream").status_code == status.HTTP_404_NOT_FOUND
    assert integration_client.post("/pause_stream").status_code == status.HTTP_404_NOT_FOUND
    assert integration_client.post("/graphql/graphql").status_code == status.HTTP_404_NOT_FOUND
