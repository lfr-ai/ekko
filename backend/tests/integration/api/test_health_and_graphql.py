"""Integration tests for REST + GraphQL API endpoints."""

from __future__ import annotations

import pytest


pytestmark = pytest.mark.integration


def test_health_when_integration_app_running_then_returns_details(integration_client) -> None:
    """REST health endpoint should return status payload with queue detail."""
    response = integration_client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["ok"], bool)
    assert "details" in payload
    assert "transcripts_queue_present" in payload["details"]


def test_graphql_health_ready_when_db_engine_injected_then_database_dependency_is_healthy(
    integration_client,
) -> None:
    """GraphQL deep health probe should validate injected database connection."""
    query = {
        "query": "query { healthReady { status dependencies { name healthy detail } } }",
    }

    response = integration_client.post("/graphql/graphql", json=query)

    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload

    dependencies = payload["data"]["healthReady"]["dependencies"]
    database_dependency = next(dep for dep in dependencies if dep["name"] == "database")
    assert database_dependency["healthy"] is True
