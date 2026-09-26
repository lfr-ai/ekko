"""End-to-end API checks for backend routes.

These tests execute against an in-process FastAPI app and run real lifespan
startup/shutdown logic, ensuring deterministic and CI-friendly behavior.
"""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.e2e, pytest.mark.integration]


@pytest.fixture
def e2e_client():
    """Create in-process HTTP client with full app lifespan."""
    from ekko.composition import create_app

    with TestClient(create_app(), raise_server_exceptions=False) as client:
        yield client


def test_backend_health_when_app_starts_then_reports_ok(e2e_client: TestClient) -> None:
    """Health endpoint should return 200 and expose status payload."""
    response = e2e_client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("ok"), bool)
    assert isinstance(payload.get("details"), dict)


def test_graphql_prompt_catalog_when_queried_then_returns_prompts(e2e_client: TestClient) -> None:
    """Prompt catalog GraphQL query should be reachable end-to-end."""
    query = {"query": "query { promptCatalog { versionSet prompts { key } } }"}
    response = e2e_client.post("/graphql", json=query)

    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload
    catalog = payload["data"]["promptCatalog"]
    assert isinstance(catalog["versionSet"], str)
    assert isinstance(catalog["prompts"], list)
