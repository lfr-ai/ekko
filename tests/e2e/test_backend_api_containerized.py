"""End-to-end tests for the canonical backend API surface.

Exercises the in-process FastAPI app with real lifespan startup/shutdown and an
in-memory SQLite database. Health, readiness, PII, and stream control use REST;
the prompt catalog is the single GraphQL read surface.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.integration, pytest.mark.slow]


class _FakeStreamController:
    """Stream controller test double for REST command tests."""

    def __init__(self) -> None:
        self.commands: list[str] = []
        self.device_check_calls = 0

    async def device_check(self) -> None:
        self.device_check_calls += 1

    async def send_command(self, command: str) -> None:
        self.commands.append(command)

    async def stop(self) -> None:
        """Complete the application-owned controller lifecycle."""


def test_health_reports_sqlite_state(containerized_client) -> None:
    """Health endpoint returns an operational payload including SQLite state."""
    response = containerized_client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["ok"], bool)
    assert "sqlite_database_present" in payload["details"]


def test_ready_reports_database_dependency(containerized_client) -> None:
    """Readiness endpoint reports the database dependency status over REST."""
    response = containerized_client.get("/ready")

    assert response.status_code == 200
    payload = response.json()
    dependency = next(dep for dep in payload["dependencies"] if dep["name"] == "database")
    assert dependency["healthy"] is True


def test_pii_anonymize_redacts_email(containerized_client) -> None:
    """PII anonymization endpoint redacts sensitive text over REST."""
    response = containerized_client.post(
        "/pii/anonymize",
        json={"text": "Reach me at e2e-test@example.com"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pii_found"] is True
    assert payload["match_count"] >= 1
    assert "e2e-test@example.com" not in payload["anonymized_text"]


def test_stream_commands_use_rest(containerized_client) -> None:
    """Audio stream start and pause run through canonical REST commands."""
    controller = _FakeStreamController()
    containerized_client.app.state.controller = controller

    start = containerized_client.post("/stream/start")
    pause = containerized_client.post("/stream/pause")

    assert start.status_code == 200
    assert pause.status_code == 200
    assert controller.device_check_calls == 1
    assert controller.commands == ["start_stream", "pause_stream"]


def test_retired_contracts_return_404(containerized_client) -> None:
    """Removed compatibility endpoints stay absent from the composed app."""
    assert containerized_client.post("/start_stream").status_code == 404
    assert containerized_client.post("/pause_stream").status_code == 404
    assert containerized_client.post("/graphql/graphql").status_code == 404


def test_prompt_catalog_graphql_query(containerized_client) -> None:
    """The prompt catalog is the single GraphQL read surface end-to-end."""
    response = containerized_client.post(
        "/graphql",
        json={
            "operationName": "PromptCatalog",
            "query": "query PromptCatalog { promptCatalog { versionSet prompts { key } } }",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload
    catalog = payload["data"]["promptCatalog"]
    assert isinstance(catalog["versionSet"], str)
    assert catalog["versionSet"]
    assert isinstance(catalog["prompts"], list)
