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

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
import strawberry
from graphql import GraphQLError
from strawberry.extensions import ParserCache, ValidationCache
from strawberry.extensions.max_aliases import MaxAliasesLimiter
from strawberry.extensions.max_tokens import MaxTokensLimiter
from strawberry.extensions.query_depth_limiter import QueryDepthLimiter

from ekko.core.enums import ServiceStatus
from ekko.presentation.graphql.extensions import PersistedOperationsExtension, QueryCostLimiterExtension
from ekko.presentation.graphql.mutations import Mutation
from ekko.presentation.graphql.queries import Query
from ekko.presentation.graphql.router import _sanitize_graphql_errors
from ekko.presentation.graphql.schema import schema
from ekko.presentation.graphql.subscriptions import Subscription

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

# Create a test schema without async extensions for async execution
test_schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=[
        ParserCache(maxsize=256),
        ValidationCache(maxsize=256),
        QueryDepthLimiter(max_depth=10),
        MaxAliasesLimiter(max_alias_count=25),
        MaxTokensLimiter(max_token_count=2500),
        # Exclude async extensions as they complicate testing
    ],
)


def _make_context() -> dict:
    """Build a minimal GraphQL context for tests."""
    from ekko.ai.pii.anonymizer import PIIAnonymizer

    return {"pii_anonymizer": PIIAnonymizer()}


def _make_context_with_controller() -> dict:
    """Build GraphQL context containing a request with a stream controller."""
    context = _make_context()

    controller = Mock()
    controller.device_check = AsyncMock()
    controller.send_command = AsyncMock()

    app = Mock()
    app.state = Mock()
    app.state.controller = controller

    request = Mock()
    request.app = app

    context["request"] = request
    return context


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
        # Handle extension classes, instances, and factory callables (lambdas)
        extension_names: set[str] = set()
        for ext in schema.extensions:
            if isinstance(ext, type):
                extension_names.add(ext.__name__)
            elif callable(ext):
                # Factory callable — invoke to get the instance type name
                instance = ext()
                extension_names.add(type(instance).__name__)
            else:
                extension_names.add(type(ext).__name__)

        # Security and caching extensions
        assert "ParserCache" in extension_names
        assert "ValidationCache" in extension_names
        assert "QueryDepthLimiter" in extension_names
        assert "MaxAliasesLimiter" in extension_names
        assert "MaxTokensLimiter" in extension_names
        assert "QueryCostLimiterExtension" in extension_names

        # Custom async extensions
        assert "QueryTimingExtension" in extension_names
        assert "RequestContextExtension" in extension_names
        assert "SessionLifecycleExtension" in extension_names

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

    @pytest.mark.asyncio
    async def test_health_query_execution(self) -> None:
        """Health query returns expected structure."""
        result = await test_schema.execute(HEALTH_QUERY)

        assert result.errors is None
        assert result.data is not None
        assert "health" in result.data

        health = result.data["health"]
        assert "status" in health
        assert health["status"] in {s.value for s in ServiceStatus}
        assert "environment" in health
        assert "dependencies" in health
        assert isinstance(health["dependencies"], list)

    @pytest.mark.asyncio
    async def test_health_ready_query_without_db(self) -> None:
        """Health ready query handles missing database gracefully."""
        # Execute with empty context (no db_engine)
        result = await test_schema.execute(HEALTH_READY_QUERY, context_value={})

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

    @pytest.mark.asyncio
    async def test_health_ready_query_with_mock_db(self) -> None:
        """Health ready query probes database connection."""
        # Create mock database engine
        mock_engine = Mock()
        mock_conn = AsyncMock()
        mock_engine.connect = Mock(return_value=mock_conn)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock()
        mock_conn.execute = AsyncMock()

        context = {"db_engine": mock_engine}
        result = await test_schema.execute(HEALTH_READY_QUERY, context_value=context)

        assert result.errors is None
        assert result.data is not None

        health = result.data["healthReady"]
        deps = health["dependencies"]
        db_dep = next((d for d in deps if d["name"] == "database"), None)
        assert db_dep is not None
        assert db_dep["healthy"] is True

    @pytest.mark.asyncio
    async def test_conversation_query_execution(self) -> None:
        """Conversation query returns expected structure."""
        variables = {"id": "test-123"}
        result = await test_schema.execute(CONVERSATION_QUERY, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        assert "conversation" in result.data
        # Returns None for non-existent conversation
        assert result.data["conversation"] is None

    @pytest.mark.asyncio
    async def test_conversations_list_query(self) -> None:
        """Conversations list query handles pagination."""
        variables = {"limit": 10, "offset": 0}
        result = await test_schema.execute(CONVERSATIONS_LIST_QUERY, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        assert "conversations" in result.data
        assert isinstance(result.data["conversations"], list)
        # Empty list for now (no data layer)
        assert len(result.data["conversations"]) == 0

    @pytest.mark.asyncio
    async def test_check_pii_query_with_pii(self) -> None:
        """Check PII query detects PII in text."""
        variables = {"text": "My email is john.doe@example.com"}
        result = await test_schema.execute(CHECK_PII_QUERY, variable_values=variables, context_value=_make_context())

        assert result.errors is None
        assert result.data is not None
        assert "checkPii" in result.data

        pii_result = result.data["checkPii"]
        assert "anonymizedText" in pii_result
        assert "piiFound" in pii_result
        assert "matchCount" in pii_result
        assert pii_result["piiFound"] is True
        assert pii_result["matchCount"] > 0

    @pytest.mark.asyncio
    async def test_check_pii_query_without_pii(self) -> None:
        """Check PII query handles clean text."""
        variables = {"text": "The weather is nice today."}
        result = await test_schema.execute(CHECK_PII_QUERY, variable_values=variables, context_value=_make_context())

        assert result.errors is None
        assert result.data is not None

        pii_result = result.data["checkPii"]
        assert pii_result["piiFound"] is False
        assert pii_result["matchCount"] == 0


# ── Mutation Execution Tests ─────────────────────────────────


@pytest.mark.unit
class TestGraphQLMutationExecution:
    """Test GraphQL mutation execution and response shapes."""

    @pytest.mark.asyncio
    async def test_control_stream_mutation_start(self) -> None:
        """Control stream mutation starts stream."""
        variables = {"command": {"action": "start"}}
        result = await test_schema.execute(
            CONTROL_STREAM_MUTATION,
            variable_values=variables,
            context_value=_make_context_with_controller(),
        )

        assert result.errors is None
        assert result.data is not None
        assert "controlStream" in result.data

        stream_status = result.data["controlStream"]
        assert stream_status["active"] is True
        assert "start" in stream_status["message"].lower()

    @pytest.mark.asyncio
    async def test_control_stream_mutation_pause(self) -> None:
        """Control stream mutation pauses stream."""
        variables = {"command": {"action": "pause"}}
        result = await test_schema.execute(
            CONTROL_STREAM_MUTATION,
            variable_values=variables,
            context_value=_make_context_with_controller(),
        )

        assert result.errors is None
        assert result.data is not None

        stream_status = result.data["controlStream"]
        assert stream_status["active"] is False
        assert "pause" in stream_status["message"].lower()

    @pytest.mark.asyncio
    async def test_control_stream_mutation_invalid_action(self) -> None:
        """Control stream mutation rejects invalid actions."""
        variables = {"command": {"action": "invalid"}}
        result = await test_schema.execute(CONTROL_STREAM_MUTATION, variable_values=variables)

        assert result.errors is None
        assert result.data is not None

        stream_status = result.data["controlStream"]
        assert stream_status["active"] is False
        assert "unknown" in stream_status["message"].lower()

    @pytest.mark.asyncio
    async def test_start_conversation_mutation(self) -> None:
        """Start conversation mutation creates new conversation."""
        result = await test_schema.execute(START_CONVERSATION_MUTATION)

        assert result.errors is None
        assert result.data is not None
        assert "startConversation" in result.data

        conversation = result.data["startConversation"]
        assert "id" in conversation
        assert len(conversation["id"]) > 0  # UUID generated
        assert "startedAt" in conversation
        assert conversation["isActive"] is True

    @pytest.mark.asyncio
    async def test_start_conversation_mutation_with_metadata(self) -> None:
        """Start conversation mutation accepts optional metadata."""
        variables = {"input": {"metadata": "test metadata"}}
        result = await test_schema.execute(START_CONVERSATION_MUTATION, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        assert "startConversation" in result.data

    @pytest.mark.asyncio
    async def test_end_conversation_mutation(self) -> None:
        """End conversation mutation marks conversation as ended."""
        variables = {"conversationId": "test-conv-123"}
        result = await test_schema.execute(END_CONVERSATION_MUTATION, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        assert "endConversation" in result.data

        conversation = result.data["endConversation"]
        assert conversation["id"] == "test-conv-123"
        assert conversation["isActive"] is False
        assert conversation["endedAt"] is not None

    @pytest.mark.asyncio
    async def test_send_message_mutation(self) -> None:
        """Send message mutation returns acknowledgment."""
        variables = {
            "input": {
                "conversationId": "test-conv-456",
                "content": "Hello, world!",
                "role": "user",
            }
        }
        result = await test_schema.execute(SEND_MESSAGE_MUTATION, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        assert "sendMessage" in result.data
        assert "test-conv-456" in result.data["sendMessage"]

    @pytest.mark.asyncio
    async def test_anonymize_text_mutation(self) -> None:
        """Anonymize text mutation redacts PII."""
        variables = {
            "input": {
                "text": "My SSN is 123-45-6789 and email is test@example.com",
            }
        }
        result = await test_schema.execute(
            ANONYMIZE_TEXT_MUTATION, variable_values=variables, context_value=_make_context()
        )

        assert result.errors is None
        assert result.data is not None
        assert "anonymizeText" in result.data

        pii_result = result.data["anonymizeText"]
        assert pii_result["piiFound"] is True
        assert pii_result["matchCount"] > 0
        # Original text should be redacted
        assert "123-45-6789" not in pii_result["anonymizedText"]

    @pytest.mark.asyncio
    async def test_anonymize_text_mutation_with_types(self) -> None:
        """Anonymize text mutation accepts enabled types filter."""
        variables = {
            "input": {
                "text": "My email is test@example.com and phone is 555-1234",
                "enabledTypes": ["email"],
            }
        }
        result = await test_schema.execute(
            ANONYMIZE_TEXT_MUTATION, variable_values=variables, context_value=_make_context()
        )

        assert result.errors is None
        assert result.data is not None


# ── Error Handling Tests ─────────────────────────────────────


@pytest.mark.unit
class TestGraphQLErrorHandling:
    """Test GraphQL error handling for invalid queries."""

    @pytest.mark.unit
    def test_sanitize_graphql_errors_when_validation_error_then_preserves_message(self) -> None:
        """Validation/spec errors should remain client-visible after sanitization."""
        validation_error = GraphQLError("Cannot query field 'boom' on type 'Query'.")

        masked = _sanitize_graphql_errors(errors=[validation_error])

        assert len(masked) == 1
        assert masked[0]["message"] == "Cannot query field 'boom' on type 'Query'."

    @pytest.mark.unit
    def test_sanitize_graphql_errors_when_internal_error_then_masks_details(self) -> None:
        """Unhandled execution errors should be normalized to a generic message."""
        runtime_error = GraphQLError(
            "Database connection failed with DSN postgres://username:password@host:5432/db",
            original_error=RuntimeError("database secret leakage"),
        )

        masked = _sanitize_graphql_errors(errors=[runtime_error])

        assert len(masked) == 1
        assert masked[0]["message"] == "Internal server error"
        assert "database" not in masked[0]["message"].lower()

    @pytest.mark.asyncio
    async def test_invalid_query_field(self) -> None:
        """Invalid field in query returns error."""
        result = await test_schema.execute(INVALID_QUERY)

        assert result.errors is not None
        assert len(result.errors) > 0
        # Strawberry returns validation error for unknown field
        assert any("nonExistentField" in str(error) for error in result.errors)

    @pytest.mark.asyncio
    async def test_malformed_query_syntax(self) -> None:
        """Malformed query syntax returns parse error."""
        result = await test_schema.execute(MALFORMED_QUERY)

        assert result.errors is not None
        assert len(result.errors) > 0
        # Parse error for unclosed braces

    @pytest.mark.asyncio
    async def test_missing_required_argument(self) -> None:
        """Missing required argument returns error."""
        # conversation query requires 'id' argument
        query = """
            query {
                conversation {
                    id
                }
            }
        """
        result = await test_schema.execute(query)

        assert result.errors is not None
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_wrong_argument_type(self) -> None:
        """Wrong argument type returns validation error."""
        query = """
            query {
                conversation(id: 123) {
                    id
                }
            }
        """
        result = await test_schema.execute(query)

        assert result.errors is not None
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_missing_input_field(self) -> None:
        """Missing required input field returns error."""
        mutation = """
            mutation {
                sendMessage(input: { conversationId: "test-123" })
            }
        """
        result = await test_schema.execute(mutation)

        # Missing 'content' field in SendMessageInput
        assert result.errors is not None
        assert len(result.errors) > 0


@pytest.mark.unit
class TestGraphQLErrorContractsAsData:
    """Validate expected domain errors are returned as typed GraphQL data."""

    @pytest.mark.asyncio
    async def test_control_stream_when_invalid_action_then_returns_domain_error_payload(self) -> None:
        """Invalid stream action should be represented as data-level domain error."""
        mutation = """
            mutation ControlStream($command: StreamCommandInput!) {
                controlStream(command: $command) {
                    active
                    message
                    errors {
                        code
                        message
                        field
                    }
                }
            }
        """
        variables = {"command": {"action": "invalid"}}
        result = await test_schema.execute(mutation, variable_values=variables)

        assert result.errors is None
        assert result.data is not None
        payload = result.data["controlStream"]
        assert payload["active"] is False
        assert payload["errors"]
        assert payload["errors"][0]["code"] == "INVALID_STREAM_ACTION"

    @pytest.mark.asyncio
    async def test_check_pii_when_strict_policy_and_anonymizer_missing_then_returns_domain_error_data(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Strict policy without anonymizer should avoid top-level exceptions and return typed errors."""
        from ekko.presentation.graphql import queries as queries_module

        monkeypatch.setattr(queries_module, "get_settings", lambda: SimpleNamespace(pii_policy_profile="strict"))

        query = """
            query CheckPII($text: String!) {
                checkPii(text: $text) {
                    anonymizedText
                    piiFound
                    matchCount
                    errors {
                        code
                        message
                        field
                    }
                }
            }
        """
        variables = {"text": "email@example.com"}
        result = await test_schema.execute(query, variable_values=variables, context_value={})

        assert result.errors is None
        assert result.data is not None
        payload = result.data["checkPii"]
        assert payload["piiFound"] is False
        assert payload["errors"]
        assert payload["errors"][0]["code"] == "PII_POLICY_VIOLATION"

    @pytest.mark.asyncio
    async def test_anonymize_text_when_strict_policy_and_anonymizer_missing_then_returns_domain_error_data(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Strict policy for anonymize mutation should return typed errors when anonymizer is unavailable."""
        from ekko.presentation.graphql import mutations as mutations_module

        monkeypatch.setattr(mutations_module, "get_settings", lambda: SimpleNamespace(pii_policy_profile="strict"))

        mutation = """
            mutation AnonymizeText($input: AnonymizeTextInput!) {
                anonymizeText(input: $input) {
                    anonymizedText
                    piiFound
                    matchCount
                    errors {
                        code
                        message
                        field
                    }
                }
            }
        """
        variables = {"input": {"text": "email@example.com"}}
        result = await test_schema.execute(mutation, variable_values=variables, context_value={})

        assert result.errors is None
        assert result.data is not None
        payload = result.data["anonymizeText"]
        assert payload["errors"]
        assert payload["errors"][0]["code"] == "PII_POLICY_VIOLATION"


@pytest.mark.unit
class TestGraphQLDemandControl:
    """Test GraphQL demand-control behavior for cost and trusted operations."""

    @pytest.mark.asyncio
    async def test_query_cost_limit_rejects_expensive_operation(self) -> None:
        """A low budget should reject a structurally expensive query."""
        constrained_schema = strawberry.Schema(
            query=Query,
            mutation=Mutation,
            subscription=Subscription,
            extensions=[
                QueryDepthLimiter(max_depth=10),
                MaxAliasesLimiter(max_alias_count=25),
                MaxTokensLimiter(max_token_count=2500),
                lambda: QueryCostLimiterExtension(max_cost=2),
            ],
        )

        expensive_query = """
            query {
                health {
                    status
                    environment
                    dependencies {
                        name
                        healthy
                        detail
                    }
                }
            }
        """

        result = await constrained_schema.execute(expensive_query)

        assert result.errors is not None
        assert any("Query cost" in str(error) for error in result.errors)

    @pytest.mark.asyncio
    async def test_persisted_operations_reject_unknown_hash(self) -> None:
        """Trusted-documents mode should reject operations absent from allowlist."""
        trusted_schema = strawberry.Schema(
            query=Query,
            mutation=Mutation,
            subscription=Subscription,
            extensions=[
                lambda: PersistedOperationsExtension(
                    trusted_operation_hashes={"deadbeef"},
                    require_trusted_documents=True,
                )
            ],
        )

        result = await trusted_schema.execute(HEALTH_QUERY)

        assert result.errors is not None
        assert any("not trusted" in str(error).lower() for error in result.errors)


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


@pytest.mark.unit
class TestGraphQLSubscriptionRuntime:
    """Test runtime behavior of GraphQL subscriptions with app-state context."""

    @pytest.mark.asyncio
    async def test_transcript_stream_when_queue_payload_then_yields_scrubbed_transcript(self) -> None:
        """Transcript stream should emit queued payloads and apply PII anonymization."""
        from ekko.ai.pii.anonymizer import PIIAnonymizer

        subscription = Subscription()
        async_queue: asyncio.Queue[object] = asyncio.Queue()
        await async_queue.put(
            {
                "text": "contact me at subscription-test@example.com",
                "source": "microphone",
                "timestamp": datetime.now(UTC),
            }
        )

        app_state = SimpleNamespace(async_transcript_queue=async_queue)
        request = SimpleNamespace(app=SimpleNamespace(state=app_state))
        info = SimpleNamespace(context={"request": request, "pii_anonymizer": PIIAnonymizer()})

        stream = subscription.transcript_stream(info=info, source="all")
        item = await asyncio.wait_for(anext(stream), timeout=2.0)
        await stream.aclose()

        assert item.source == "microphone"
        assert item.timestamp.endswith("Z")
        assert "subscription-test@example.com" not in item.text
        assert "[EMAIL-REDACTED]" in item.text

    @pytest.mark.asyncio
    async def test_agent_status_when_bridge_task_running_then_reports_running(self) -> None:
        """Agent status subscription should reflect running transcript bridge state."""
        subscription = Subscription()
        bridge_task = asyncio.create_task(asyncio.sleep(5))
        app_state = SimpleNamespace(_transcript_bridge_task=bridge_task)
        request = SimpleNamespace(app=SimpleNamespace(state=app_state))
        info = SimpleNamespace(context={"request": request})

        stream = subscription.agent_status(info=info)
        status = await asyncio.wait_for(anext(stream), timeout=2.0)
        await stream.aclose()

        bridge_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await bridge_task

        assert status == "running"

    @pytest.mark.asyncio
    async def test_transcript_stream_when_strict_policy_and_missing_anonymizer_then_masks_payload(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Strict PII policy should fail closed for subscription text when anonymizer is unavailable."""
        from ekko.presentation.graphql import subscriptions as subscriptions_module

        monkeypatch.setattr(
            subscriptions_module,
            "get_settings",
            lambda: SimpleNamespace(pii_policy_profile="strict"),
        )

        subscription = Subscription()
        async_queue: asyncio.Queue[object] = asyncio.Queue()
        await async_queue.put(
            {
                "text": "my email is strict-subscription@example.com",
                "source": "microphone",
                "timestamp": datetime.now(UTC),
            }
        )

        app_state = SimpleNamespace(async_transcript_queue=async_queue)
        request = SimpleNamespace(app=SimpleNamespace(state=app_state))
        info = SimpleNamespace(context={"request": request})

        stream = subscription.transcript_stream(info=info, source="all")
        item = await asyncio.wait_for(anext(stream), timeout=2.0)
        await stream.aclose()

        assert item.text == "[PII-REDACTION-UNAVAILABLE]"


# ── Schema Introspection Tests ───────────────────────────────


@pytest.mark.unit
class TestGraphQLIntrospection:
    """Test GraphQL schema introspection capabilities."""

    @pytest.mark.asyncio
    async def test_introspection_query_works(self) -> None:
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
        result = await test_schema.execute(introspection_query)

        assert result.errors is None
        assert result.data is not None
        assert "__schema" in result.data
        assert "types" in result.data["__schema"]
        assert len(result.data["__schema"]["types"]) > 0

    @pytest.mark.asyncio
    async def test_type_introspection(self) -> None:
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
        result = await test_schema.execute(type_query)

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
