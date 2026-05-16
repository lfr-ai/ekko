"""Integration tests for stream routes and GraphQL mutation flows."""

import pytest
pytestmark = pytest.mark.integration


class _FakeStreamController:
    """Test double for stream controller used in integration API tests."""

    def __init__(self) -> None:
        self.commands: list[str] = []
        self.device_check_calls = 0

    async def device_check(self) -> None:
        self.device_check_calls += 1

    async def send_command(self, command: str) -> None:
        self.commands.append(command)

    async def stop(self) -> None:
        return


def test_start_stream_when_controller_injected_then_returns_started_status(integration_client) -> None:
    """Start stream route should invoke controller and return started payload."""
    controller = _FakeStreamController()
    integration_client.app.state.controller = controller

    response = integration_client.post("/start_stream")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "started"
    assert controller.device_check_calls == 1
    assert controller.commands == ["start_stream"]


def test_pause_stream_when_controller_injected_then_returns_paused_status(integration_client) -> None:
    """Pause stream route should invoke controller and return paused payload."""
    controller = _FakeStreamController()
    integration_client.app.state.controller = controller

    response = integration_client.post("/pause_stream")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "paused"
    assert controller.commands == ["pause_stream"]


def test_graphql_anonymize_text_when_pii_present_then_returns_redacted_payload(integration_client) -> None:
    """Anonymize mutation should redact sensitive values in integration flow."""
    mutation = {
        "query": (
            "mutation($input: AnonymizeTextInput!) { "
            "anonymizeText(input: $input) { anonymizedText piiFound matchCount } "
            "}"
        ),
        "variables": {
            "input": {
                "text": "Contact me at integration-test@example.com",
            }
        },
    }

    response = integration_client.post("/graphql/graphql", json=mutation)

    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload
    result = payload["data"]["anonymizeText"]
    assert result["piiFound"] is True
    assert result["matchCount"] >= 1
    assert "integration-test@example.com" not in result["anonymizedText"]


def test_graphql_conversation_lifecycle_when_mutations_called_then_outputs_are_consistent(
    integration_client,
) -> None:
    """Start/send/end mutation sequence should produce consistent conversation outputs."""
    start_mutation = {"query": "mutation { startConversation { id isActive endedAt } }"}

    start_response = integration_client.post("/graphql/graphql", json=start_mutation)

    assert start_response.status_code == 200
    start_payload = start_response.json()
    assert "errors" not in start_payload

    started = start_payload["data"]["startConversation"]
    assert started["id"]
    assert started["isActive"] is True
    assert started["endedAt"] is None

    conversation_id = started["id"]

    send_mutation = {
        "query": "mutation($input: SendMessageInput!) { sendMessage(input: $input) }",
        "variables": {
            "input": {
                "conversationId": conversation_id,
                "content": "Hello integration",
                "role": "user",
            }
        },
    }

    send_response = integration_client.post("/graphql/graphql", json=send_mutation)

    assert send_response.status_code == 200
    send_payload = send_response.json()
    assert "errors" not in send_payload
    assert conversation_id in send_payload["data"]["sendMessage"]

    end_mutation = {
        "query": (
            "mutation($conversationId: String!) { "
            "endConversation(conversationId: $conversationId) { id isActive endedAt } "
            "}"
        ),
        "variables": {"conversationId": conversation_id},
    }

    end_response = integration_client.post("/graphql/graphql", json=end_mutation)

    assert end_response.status_code == 200
    end_payload = end_response.json()
    assert "errors" not in end_payload
    ended = end_payload["data"]["endConversation"]
    assert ended["id"] == conversation_id
    assert ended["isActive"] is False
    assert ended["endedAt"] is not None


def test_graphql_health_ready_when_db_injected_then_reports_database_healthy(integration_client_with_db) -> None:
    """Readiness query should show healthy database dependency when DB engine is injected."""
    query = {
        "query": "query { healthReady { status dependencies { name healthy detail } } }",
    }

    response = integration_client_with_db.post("/graphql/graphql", json=query)

    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload

    dependencies = payload["data"]["healthReady"]["dependencies"]
    db_dependency = next(dep for dep in dependencies if dep["name"] == "database")
    assert db_dependency["healthy"] is True
