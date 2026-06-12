"""Container-backed end-to-end tests for backend API behavior.

These tests execute against an in-process FastAPI app with real lifespan
startup/shutdown and a PostgreSQL Testcontainer injected for GraphQL readiness
probes.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.integration, pytest.mark.slow]


class _FakeStreamController:
    """Test double for stream controller used by stream route e2e tests."""

    def __init__(self) -> None:
        self.commands: list[str] = []
        self.device_check_calls = 0

    async def device_check(self) -> None:
        self.device_check_calls += 1

    async def send_command(self, command: str) -> None:
        self.commands.append(command)

    async def stop(self) -> None:
        """Lifespan-compatible shutdown hook used by app teardown."""


def test_health_when_lifespan_started_then_reports_ok_payload(
    containerized_client,
) -> None:
    """Health endpoint should return payload with operational details."""
    # Arrange / Act
    response = containerized_client.get("/health")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert isinstance(payload["details"], dict)
    assert payload["details"]["transcripts_queue_present"] is True


def test_graphql_health_when_queried_then_returns_service_status(
    containerized_client,
) -> None:
    """GraphQL health query should be available end-to-end."""
    # Arrange
    query = {"query": "query { health { status environment } }"}

    # Act
    response = containerized_client.post("/graphql/graphql", json=query)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload
    assert payload["data"]["health"]["status"] in {"healthy", "degraded", "unhealthy"}


def test_graphql_health_ready_when_db_available_then_dependency_is_healthy(
    containerized_client,
) -> None:
    """GraphQL readiness should report healthy database dependency with Testcontainer."""
    # Arrange
    query = {
        "query": "query { healthReady { status dependencies { name healthy detail } } }",
    }

    # Act
    response = containerized_client.post("/graphql/graphql", json=query)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload

    dependencies = payload["data"]["healthReady"]["dependencies"]
    database_dependency = next(dep for dep in dependencies if dep["name"] == "database")
    assert database_dependency["healthy"] is True


def test_graphql_anonymize_text_when_pii_present_then_returns_redacted_text(
    containerized_client,
) -> None:
    """Anonymize mutation should redact PII in end-to-end API flow."""
    # Arrange
    mutation = {
        "query": (
            "mutation($input: AnonymizeTextInput!) { "
            "anonymizeText(input: $input) { anonymizedText piiFound matchCount } }"
        ),
        "variables": {
            "input": {
                "text": "My email is integration@example.com and card is 4242 4242 4242 4242",
            },
        },
    }

    # Act
    response = containerized_client.post("/graphql/graphql", json=mutation)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload

    data = payload["data"]["anonymizeText"]
    assert data["piiFound"] is True
    assert data["matchCount"] >= 1
    assert "integration@example.com" not in data["anonymizedText"]


def test_start_stream_when_controller_injected_then_returns_started_status(
    containerized_client,
) -> None:
    """Start stream endpoint should invoke controller and return started status."""
    # Arrange
    controller = _FakeStreamController()
    containerized_client.app.state.controller = controller

    # Act
    response = containerized_client.post("/start_stream")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "started"
    assert controller.device_check_calls == 1
    assert controller.commands == ["start_stream"]


def test_pause_stream_when_controller_injected_then_returns_paused_status(
    containerized_client,
) -> None:
    """Pause stream endpoint should invoke controller and return paused status."""
    # Arrange
    controller = _FakeStreamController()
    containerized_client.app.state.controller = controller

    # Act
    response = containerized_client.post("/pause_stream")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "paused"
    assert controller.commands == ["pause_stream"]


def test_graphql_conversation_lifecycle_when_mutations_called_then_state_transitions_are_valid(
    containerized_client,
) -> None:
    """Conversation start/send/end mutations should produce consistent lifecycle outputs."""
    # Arrange
    start_mutation = {
        "query": ("mutation { startConversation { id startedAt endedAt isActive } }")
    }

    # Act: start conversation
    start_response = containerized_client.post("/graphql/graphql", json=start_mutation)

    # Assert start
    assert start_response.status_code == 200
    start_payload = start_response.json()
    assert "errors" not in start_payload
    started = start_payload["data"]["startConversation"]
    assert started["id"]
    assert started["isActive"] is True
    assert started["endedAt"] is None

    conversation_id = started["id"]

    # Act: send message
    send_mutation = {
        "query": ("mutation($input: SendMessageInput!) { sendMessage(input: $input) }"),
        "variables": {
            "input": {
                "conversationId": conversation_id,
                "content": "Hello from e2e",
                "role": "user",
            }
        },
    }
    send_response = containerized_client.post("/graphql/graphql", json=send_mutation)

    # Assert send
    assert send_response.status_code == 200
    send_payload = send_response.json()
    assert "errors" not in send_payload
    assert conversation_id in send_payload["data"]["sendMessage"]

    # Act: end conversation
    end_mutation = {
        "query": (
            "mutation($conversationId: String!) { "
            "endConversation(conversationId: $conversationId) { id startedAt endedAt isActive } "
            "}"
        ),
        "variables": {"conversationId": conversation_id},
    }
    end_response = containerized_client.post("/graphql/graphql", json=end_mutation)

    # Assert end
    assert end_response.status_code == 200
    end_payload = end_response.json()
    assert "errors" not in end_payload
    ended = end_payload["data"]["endConversation"]
    assert ended["id"] == conversation_id
    assert ended["isActive"] is False
    assert ended["endedAt"] is not None
