"""GraphQL schema validation and execution tests.

Tests the Strawberry GraphQL schema including:
- Schema structure validation
- Query execution and response shapes
- Mutation execution and side effects
- Subscription structure
- Error handling for invalid queries
- Security extension limits
"""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest
from strawberry.extensions import ParserCache, ValidationCache
from strawberry.extensions.max_aliases import MaxAliasesLimiter
from strawberry.extensions.max_tokens import MaxTokensLimiter
from strawberry.extensions.query_depth_limiter import QueryDepthLimiter

# Import query strings from fixtures
from tests.fixtures.graphql_fixtures import (
    ANONYMIZE_TEXT_MUTATION,
    CHECK_PII_QUERY,
    CONTROL_STREAM_MUTATION,
    CONVERSATION_QUERY,
    CONVERSATIONS_LIST_QUERY,
    END_CONVERSATION_MUTATION,
    HEALTH_QUERY,
    HEALTH_READY_QUERY,
    INVALID_QUERY,
    MALFORMED_QUERY,
    SEND_MESSAGE_MUTATION,
    START_CONVERSATION_MUTATION,
)

from ekko.core.enums import ServiceStatus
from ekko.presentation.graphql.extensions import (
    QueryTimingExtension,
    RequestContextExtension,
    SessionLifecycleExtension,
)
from ekko.presentation.graphql.schema import schema

# ── Schema Structure Tests ───────────────────────────────────


@pytest.mark.unit
class TestGraphQLSchemaStructure:
    """Test GraphQL schema assembly and configuration."""

    def test_schema_has_query_type(self) -> None:
        """Schema includes Query root type."""
        assert schema.query is not None
        assert schema.query.__name__ == "Query"

    def test_schema_has_mutation_type(self) -> None:
        """Schema includes Mutation root type."""
        assert schema.mutation is not None
        assert schema.mutation.__name__ == "Mutation"

    def test_schema_has_subscription_type(self) -> None:
        """Schema includes Subscription root type."""
        assert schema.subscription is not None
        assert schema.subscription.__name__ == "Subscription"

    def test_schema_has_required_extensions(self) -> None:
        """Schema includes security and performance extensions."""
        extension_types = [type(ext) for ext in schema.extensions]

        assert ParserCache in extension_types
        assert ValidationCache in extension_types
        assert QueryDepthLimiter in extension_types
        assert MaxAliasesLimiter in extension_types
        assert MaxTokensLimiter in extension_types
        assert QueryTimingExtension in extension_types
        assert RequestContextExtension in extension_types
        assert SessionLifecycleExtension in extension_types

    def test_query_fields_exist(self) -> None:
        """Query type exposes expected fields."""
        query_fields = schema.query.__strawberry_definition__.fields

        field_names = {field.python_name for field in query_fields}
        expected_fields = {
            "health",
            "health_ready",
            "conversation",
            "conversations",
            "check_pii",
        }

        assert expected_fields.issubset(field_names)

    def test_mutation_fields_exist(self) -> None:
        """Mutation type exposes expected fields."""
        mutation_fields = schema.mutation.__strawberry_definition__.fields

        field_names = {field.python_name for field in mutation_fields}
        expected_fields = {
            "control_stream",
            "start_conversation",
            "end_conversation",
            "send_message",
            "anonymize_text",
        }

        assert expected_fields.issubset(field_names)

    def test_subscription_fields_exist(self) -> None:
        """Subscription type exposes expected fields."""
        subscription_fields = schema.subscription.__strawberry_definition__.fields

        field_names = {field.python_name for field in subscription_fields}
        expected_fields = {"transcript_stream", "agent_status", "conversation_events"}

        assert expected_fields.issubset(field_names)


# ── Query Execution Tests ────────────────────────────────────


@pytest.mark.unit
class TestGraphQLQueryExecution:
    """Test GraphQL query execution and response shapes."""

    def test_health_query_execution(self) -> None:
        """Health query returns expected structure."""
        result = schema.execute_sync(HEALTH_QUERY)

        assert result.errors is None
        assert result.data is not None
        assert "health" in result.data

        health = result.data["health"]
        assert "status" in health
        assert health["status"] in {s.value for s in ServiceStatus}
        assert "environment" in health
        assert "dependencies" in health
        assert isinstance(health["dependencies"], list)

    def test_health_ready_query_without_db(self) -> None:
        """Health ready query handles missing database gracefully."""
        # Execute without context (no db_engine)
        result = schema.execute_sync(HEALTH_READY_QUERY)

        assert result.errors is None
        assert result.data is not None
        assert "healthReady" in result.data

        health = result.data["healthReady"]
        assert "status" in health
        assert "dependencies" in health

        # Should report database as not configured
        deps = health["dependencies"]
        db_dep = next((d for d in deps if d["name"] == "database"), None)
        assert db_dep is not None
        assert db_dep["healthy"] is False
        assert "not configured" in db_dep["detail"]

    def test_health_ready_query_with_mock_db(self) -> None:
        """Health ready query probes database connection."""
        # Create mock database engine
        mock_engine = Mock()
        mock_conn = AsyncMock()
        mock_engine.connect = Mock(return_value=mock_conn)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock()
        mock_conn.execute = AsyncMock()

        context = {"db_engine": mock_engine}
        result = schema.execute_sync(HEALTH_READY_QUERY, context_value=context)

        assert result.errors is None
        assert result.data is not None

        health = result.data["healthReady"]
        deps = health["dependencies"]
        db_dep = next((d for d in deps if d["name"] == "database"), None)
        assert db_dep is not None
        assert db_dep["healthy"] is True

    def test_conversation_query_execution(self) -> None:
        """Conversation query returns expected structure."""
        variables = {"id": "test-123"}
        result = schema.execute_sync(CONVERSATION_QUERY, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        assert "conversation" in result.data
        # Returns None for non-existent conversation
        assert result.data["conversation"] is None

    def test_conversations_list_query(self) -> None:
        """Conversations list query handles pagination."""
        variables = {"limit": 10, "offset": 0}
        result = schema.execute_sync(
            CONVERSATIONS_LIST_QUERY, variable_values=variables
        )

        assert result.errors is None
        assert result.data is not None
        assert "conversations" in result.data
        assert isinstance(result.data["conversations"], list)
        # Empty list for now (no data layer)
        assert len(result.data["conversations"]) == 0

    def test_check_pii_query_with_pii(self) -> None:
        """Check PII query detects PII in text."""
        variables = {"text": "My email is john.doe@example.com"}
        result = schema.execute_sync(CHECK_PII_QUERY, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        assert "checkPii" in result.data

        pii_result = result.data["checkPii"]
        assert "anonymizedText" in pii_result
        assert "piiFound" in pii_result
        assert "matchCount" in pii_result
        assert pii_result["piiFound"] is True
        assert pii_result["matchCount"] > 0

    def test_check_pii_query_without_pii(self) -> None:
        """Check PII query handles clean text."""
        variables = {"text": "The weather is nice today."}
        result = schema.execute_sync(CHECK_PII_QUERY, variable_values=variables)

        assert result.errors is None
        assert result.data is not None

        pii_result = result.data["checkPii"]
        assert pii_result["piiFound"] is False
        assert pii_result["matchCount"] == 0


# ── Mutation Execution Tests ─────────────────────────────────


@pytest.mark.unit
class TestGraphQLMutationExecution:
    """Test GraphQL mutation execution and response shapes."""

    def test_control_stream_mutation_start(self) -> None:
        """Control stream mutation starts stream."""
        variables = {"command": {"action": "start"}}
        result = schema.execute_sync(CONTROL_STREAM_MUTATION, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        assert "controlStream" in result.data

        stream_status = result.data["controlStream"]
        assert stream_status["active"] is True
        assert "start" in stream_status["message"].lower()

    def test_control_stream_mutation_pause(self) -> None:
        """Control stream mutation pauses stream."""
        variables = {"command": {"action": "pause"}}
        result = schema.execute_sync(CONTROL_STREAM_MUTATION, variable_values=variables)

        assert result.errors is None
        assert result.data is not None

        stream_status = result.data["controlStream"]
        assert stream_status["active"] is False
        assert "pause" in stream_status["message"].lower()

    def test_control_stream_mutation_invalid_action(self) -> None:
        """Control stream mutation rejects invalid actions."""
        variables = {"command": {"action": "invalid"}}
        result = schema.execute_sync(CONTROL_STREAM_MUTATION, variable_values=variables)

        assert result.errors is None
        assert result.data is not None

        stream_status = result.data["controlStream"]
        assert stream_status["active"] is False
        assert "unknown" in stream_status["message"].lower()

    def test_start_conversation_mutation(self) -> None:
        """Start conversation mutation creates new conversation."""
        result = schema.execute_sync(START_CONVERSATION_MUTATION)

        assert result.errors is None
        assert result.data is not None
        assert "startConversation" in result.data

        conversation = result.data["startConversation"]
        assert "id" in conversation
        assert len(conversation["id"]) > 0  # UUID generated
        assert "startedAt" in conversation
        assert conversation["isActive"] is True

    def test_start_conversation_mutation_with_metadata(self) -> None:
        """Start conversation mutation accepts optional metadata."""
        variables = {"input": {"metadata": "test metadata"}}
        result = schema.execute_sync(
            START_CONVERSATION_MUTATION, variable_values=variables
        )

        assert result.errors is None
        assert result.data is not None
        assert "startConversation" in result.data

    def test_end_conversation_mutation(self) -> None:
        """End conversation mutation marks conversation as ended."""
        variables = {"conversationId": "test-conv-123"}
        result = schema.execute_sync(
            END_CONVERSATION_MUTATION, variable_values=variables
        )

        assert result.errors is None
        assert result.data is not None
        assert "endConversation" in result.data

        conversation = result.data["endConversation"]
        assert conversation["id"] == "test-conv-123"
        assert conversation["isActive"] is False
        assert conversation["endedAt"] is not None

    def test_send_message_mutation(self) -> None:
        """Send message mutation returns acknowledgment."""
        variables = {
            "input": {
                "conversationId": "test-conv-456",
                "content": "Hello, world!",
                "role": "user",
            }
        }
        result = schema.execute_sync(SEND_MESSAGE_MUTATION, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        assert "sendMessage" in result.data
        assert "test-conv-456" in result.data["sendMessage"]

    def test_anonymize_text_mutation(self) -> None:
        """Anonymize text mutation redacts PII."""
        variables = {
            "input": {
                "text": "My SSN is 123-45-6789 and email is test@example.com",
            }
        }
        result = schema.execute_sync(ANONYMIZE_TEXT_MUTATION, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        assert "anonymizeText" in result.data

        pii_result = result.data["anonymizeText"]
        assert pii_result["piiFound"] is True
        assert pii_result["matchCount"] > 0
        # Original text should be redacted
        assert "123-45-6789" not in pii_result["anonymizedText"]

    def test_anonymize_text_mutation_with_types(self) -> None:
        """Anonymize text mutation accepts enabled types filter."""
        variables = {
            "input": {
                "text": "My email is test@example.com and phone is 555-1234",
                "enabledTypes": ["email"],
            }
        }
        result = schema.execute_sync(ANONYMIZE_TEXT_MUTATION, variable_values=variables)

        assert result.errors is None
        assert result.data is not None


# ── Error Handling Tests ─────────────────────────────────────


@pytest.mark.unit
class TestGraphQLErrorHandling:
    """Test GraphQL error handling for invalid queries."""

    def test_invalid_query_field(self) -> None:
        """Invalid field in query returns error."""
        result = schema.execute_sync(INVALID_QUERY)

        assert result.errors is not None
        assert len(result.errors) > 0
        # Strawberry returns validation error for unknown field
        assert any("nonExistentField" in str(error) for error in result.errors)

    def test_malformed_query_syntax(self) -> None:
        """Malformed query syntax returns parse error."""
        result = schema.execute_sync(MALFORMED_QUERY)

        assert result.errors is not None
        assert len(result.errors) > 0
        # Parse error for unclosed braces

    def test_missing_required_argument(self) -> None:
        """Missing required argument returns error."""
        # conversation query requires 'id' argument
        query = """
            query {
                conversation {
                    id
                }
            }
        """
        result = schema.execute_sync(query)

        assert result.errors is not None
        assert len(result.errors) > 0

    def test_wrong_argument_type(self) -> None:
        """Wrong argument type returns validation error."""
        query = """
            query {
                conversation(id: 123) {
                    id
                }
            }
        """
        result = schema.execute_sync(query)

        assert result.errors is not None
        assert len(result.errors) > 0

    def test_missing_input_field(self) -> None:
        """Missing required input field returns error."""
        mutation = """
            mutation {
                sendMessage(input: { conversationId: "test-123" })
            }
        """
        result = schema.execute_sync(mutation)

        # Missing 'content' field in SendMessageInput
        assert result.errors is not None
        assert len(result.errors) > 0


# ── Subscription Structure Tests ─────────────────────────────


@pytest.mark.unit
class TestGraphQLSubscriptionStructure:
    """Test GraphQL subscription resolver structure.

    Note: Full subscription execution requires async context and WebSocket
    transport. These tests validate structure only.
    """

    def test_transcript_stream_subscription_exists(self) -> None:
        """Transcript stream subscription is defined."""
        subscription_fields = schema.subscription.__strawberry_definition__.fields
        field_names = {field.python_name for field in subscription_fields}
        assert "transcript_stream" in field_names

    def test_agent_status_subscription_exists(self) -> None:
        """Agent status subscription is defined."""
        subscription_fields = schema.subscription.__strawberry_definition__.fields
        field_names = {field.python_name for field in subscription_fields}
        assert "agent_status" in field_names

    def test_conversation_events_subscription_exists(self) -> None:
        """Conversation events subscription is defined."""
        subscription_fields = schema.subscription.__strawberry_definition__.fields
        field_names = {field.python_name for field in subscription_fields}
        assert "conversation_events" in field_names

    def test_transcript_stream_has_source_parameter(self) -> None:
        """Transcript stream subscription accepts source parameter."""
        subscription_fields = schema.subscription.__strawberry_definition__.fields
        transcript_field = next(
            (f for f in subscription_fields if f.python_name == "transcript_stream"),
            None,
        )
        assert transcript_field is not None

        # Check field has arguments
        arg_names = {arg.python_name for arg in transcript_field.arguments}
        assert "source" in arg_names

    def test_conversation_events_has_id_parameter(self) -> None:
        """Conversation events subscription requires conversation_id."""
        subscription_fields = schema.subscription.__strawberry_definition__.fields
        events_field = next(
            (f for f in subscription_fields if f.python_name == "conversation_events"),
            None,
        )
        assert events_field is not None

        arg_names = {arg.python_name for arg in events_field.arguments}
        assert "conversation_id" in arg_names


# ── Schema Introspection Tests ───────────────────────────────


@pytest.mark.unit
class TestGraphQLIntrospection:
    """Test GraphQL schema introspection capabilities."""

    def test_introspection_query_works(self) -> None:
        """Schema supports introspection queries."""
        introspection_query = """
            query {
                __schema {
                    types {
                        name
                    }
                }
            }
        """
        result = schema.execute_sync(introspection_query)

        assert result.errors is None
        assert result.data is not None
        assert "__schema" in result.data
        assert "types" in result.data["__schema"]
        assert len(result.data["__schema"]["types"]) > 0

    def test_type_introspection(self) -> None:
        """Schema supports type introspection."""
        type_query = """
            query {
                __type(name: "HealthType") {
                    name
                    kind
                    fields {
                        name
                        type {
                            name
                        }
                    }
                }
            }
        """
        result = schema.execute_sync(type_query)

        assert result.errors is None
        assert result.data is not None
        assert "__type" in result.data
        health_type = result.data["__type"]
        assert health_type["name"] == "HealthType"
        assert "fields" in health_type

        field_names = {field["name"] for field in health_type["fields"]}
        assert "status" in field_names
        assert "environment" in field_names
        assert "dependencies" in field_names
