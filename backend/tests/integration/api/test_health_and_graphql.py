"""Integration tests for operational REST endpoints and minimal GraphQL."""

from __future__ import annotations

import pytest
from fastapi import status

from ekko.application.services import ReadinessService

pytestmark = pytest.mark.integration


def test_health_reports_process_state(integration_client) -> None:
    """Expose lightweight process liveness over REST."""
    response = integration_client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert isinstance(payload["ok"], bool)
    assert "details" in payload


def test_ready_without_database_returns_service_unavailable(integration_client) -> None:
    """Use HTTP 503 when a required dependency is unavailable."""
    integration_client.app.state.readiness_service = ReadinessService(database_probe=None)

    response = integration_client.get("/ready")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["dependencies"][0]["name"] == "database"


def test_ready_with_database_returns_healthy(integration_client_with_db) -> None:
    """Report healthy readiness when the database probe succeeds."""
    response = integration_client_with_db.get("/ready")

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["dependencies"][0]["healthy"] is True


def test_prompt_catalog_query_returns_real_registry(integration_client) -> None:
    """Expose the active prompt registry as the sole GraphQL feature."""
    response = integration_client.post(
        "/graphql",
        json={
            "operationName": "PromptCatalog",
            "query": "query PromptCatalog { promptCatalog { versionSet prompts { key } } }",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert "errors" not in payload
    assert payload["data"]["promptCatalog"]["versionSet"] == "experimental"
    assert len(payload["data"]["promptCatalog"]["prompts"]) == 3


def test_metrics_endpoint_exposes_http_metrics(integration_client) -> None:
    """Expose HTTP instrumentation metrics."""
    integration_client.get("/health")

    response = integration_client.get("/metrics")

    assert response.status_code == status.HTTP_200_OK
    assert "http_request_duration" in response.text or "http_requests_total" in response.text
