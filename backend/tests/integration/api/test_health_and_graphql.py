"""Integration tests for REST + GraphQL API endpoints."""

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


def test_graphql_health_ready_when_queried_then_database_dependency_is_reported(integration_client) -> None:
    """GraphQL deep health probe should always include database dependency state."""
    query = {
        "query": "query { healthReady { status dependencies { name healthy detail } } }",
    }

    response = integration_client.post("/graphql/graphql", json=query)

    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload

    dependencies = payload["data"]["healthReady"]["dependencies"]
    database_dependency = next(dep for dep in dependencies if dep["name"] == "database")
    assert isinstance(database_dependency["healthy"], bool)
    if database_dependency["healthy"] is False:
        assert isinstance(database_dependency.get("detail"), str)
