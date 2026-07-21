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

    response = integration_client.post("/graphql", json=query)

    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload

    dependencies = payload["data"]["healthReady"]["dependencies"]
    database_dependency = next(dep for dep in dependencies if dep["name"] == "database")
    assert isinstance(database_dependency["healthy"], bool)
    if database_dependency["healthy"] is False:
        assert isinstance(database_dependency.get("detail"), str)


def test_metrics_when_graphql_request_executed_then_graphql_metrics_are_exposed(integration_client) -> None:
    """Metrics endpoint should expose GraphQL operation counters after GraphQL traffic."""
    query = {
        "query": "query { health { status } }",
    }
    graphql_response = integration_client.post("/graphql", json=query)
    assert graphql_response.status_code == 200

    metrics_response = integration_client.get("/metrics")

    assert metrics_response.status_code == 200
    body = metrics_response.text
    assert "ekko_graphql_operation_total" in body
    assert "ekko_graphql_operation_duration_seconds" in body
