"""Strawberry GraphQL extensions for Ekko."""

from __future__ import annotations

import asyncio
import hashlib
import importlib
import inspect
import logging
import time
from typing import TYPE_CHECKING

from graphql import GraphQLError, parse
from graphql.language import (
    FieldNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    InlineFragmentNode,
    OperationDefinitionNode,
    SelectionNode,
)
from strawberry.extensions import SchemaExtension

try:
    _prometheus_client = importlib.import_module("prometheus_client")
except Exception:  # pragma: no cover - optional runtime dependency guard
    _prometheus_client = None

_counter_factory = None if _prometheus_client is None else getattr(_prometheus_client, "Counter", None)
_histogram_factory = None if _prometheus_client is None else getattr(_prometheus_client, "Histogram", None)

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)

_METRIC_LABEL_UNKNOWN = "unknown"

_GRAPHQL_OPERATION_TOTAL = (
    _counter_factory(
        "ekko_graphql_operation_total",
        "Total number of GraphQL operations by operation type and status.",
        ("operation_type", "status"),
    )
    if callable(_counter_factory)
    else None
)

_GRAPHQL_OPERATION_DURATION_SECONDS = (
    _histogram_factory(
        "ekko_graphql_operation_duration_seconds",
        "GraphQL operation execution duration in seconds.",
        ("operation_type", "status"),
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
    )
    if callable(_histogram_factory)
    else None
)

_GRAPHQL_OPERATION_COST = (
    _histogram_factory(
        "ekko_graphql_operation_cost",
        "Estimated GraphQL operation structural cost.",
        ("operation_type",),
        buckets=(1, 2, 5, 10, 25, 50, 100, 250, 500, 1000),
    )
    if callable(_histogram_factory)
    else None
)

_GRAPHQL_OPERATION_REJECTED_TOTAL = (
    _counter_factory(
        "ekko_graphql_operation_rejected_total",
        "Total number of rejected GraphQL operations by rejection reason.",
        ("reason",),
    )
    if callable(_counter_factory)
    else None
)


def _observe_graphql_outcome(*, operation_type: str, status: str, duration_seconds: float) -> None:
    """Emit Prometheus observations for operation outcome and duration."""
    if _GRAPHQL_OPERATION_TOTAL is not None:
        _GRAPHQL_OPERATION_TOTAL.labels(operation_type=operation_type, status=status).inc()

    if _GRAPHQL_OPERATION_DURATION_SECONDS is not None:
        _GRAPHQL_OPERATION_DURATION_SECONDS.labels(operation_type=operation_type, status=status).observe(
            duration_seconds
        )


def _observe_rejection(*, reason: str) -> None:
    """Emit Prometheus counter for security/policy rejections."""
    if _GRAPHQL_OPERATION_REJECTED_TOTAL is not None:
        _GRAPHQL_OPERATION_REJECTED_TOTAL.labels(reason=reason).inc()


class SessionLifecycleExtension(SchemaExtension):
    """Per-request database session lifecycle.

    Creates an async SQLAlchemy session at the start of each GraphQL operation
    and closes it when the operation completes. The session factory is read
    from the GraphQL context (injected at router level), keeping this
    extension free from infrastructure imports.
    """

    def on_operation(self) -> Generator[None, None, None]:
        context = self.execution_context.context
        if context is None:
            context = {}
            self.execution_context.context = context

        session = None
        try:
            session_factory = context.get("session_factory")
            if session_factory is not None:
                session = session_factory()
                context["db_session"] = session
            else:
                logger.debug("No session_factory in context; skipping DB session setup")
                context["db_session"] = None
        except Exception:
            logger.debug("DB session not available (database may not be configured)")
            context["db_session"] = None

        try:
            yield
        finally:
            if session is not None:
                close_result = session.close()
                if inspect.isawaitable(close_result):
                    try:
                        running_loop = asyncio.get_running_loop()
                    except RuntimeError:
                        asyncio.run(close_result)
                    else:
                        self._pending_close_task = running_loop.create_task(close_result)


class QueryTimingExtension(SchemaExtension):
    """Log execution time for each GraphQL operation."""

    def on_operation(self) -> Generator[None, None, None]:
        start = time.monotonic()
        yield
        elapsed = time.monotonic() - start
        operation = getattr(self.execution_context, "operation", None)
        operation_name = getattr(operation, "name", None)
        operation_type_raw = getattr(operation, "operation", None)
        operation_type = str(operation_type_raw) if operation_type_raw is not None else _METRIC_LABEL_UNKNOWN
        operation_name_text = getattr(operation_name, "value", "anonymous")
        errors = getattr(self.execution_context, "errors", None)
        status = "error" if errors else "ok"

        _observe_graphql_outcome(
            operation_type=operation_type,
            status=status,
            duration_seconds=elapsed,
        )

        context = self.execution_context.context or {}
        operation_cost = context.get("operation_cost")
        operation_sha256 = context.get("operation_sha256")
        logger.info(
            "graphql.operation.completed",
            extra={
                "operation_name": operation_name_text,
                "operation_type": operation_type,
                "duration_seconds": round(elapsed, 6),
                "status": status,
                "operation_cost": operation_cost,
                "operation_sha256": operation_sha256,
            },
        )


class RequestContextExtension(SchemaExtension):
    """Inject request metadata into the GraphQL context."""

    def on_operation(self) -> Generator[None, None, None]:
        context = self.execution_context.context
        if context is None:
            context = {}
            self.execution_context.context = context

        request = context.get("request")
        if request:
            context["request_id"] = getattr(request.state, "request_id", None)
        yield


class PersistedOperationsExtension(SchemaExtension):
    """Optional persisted-operation policy for trusted first-party clients.

    The extension computes a SHA-256 hash of the incoming GraphQL document and
    rejects unknown operations when trusted-documents mode is enabled.
    """

    def __init__(
        self,
        *,
        trusted_operation_hashes: set[str],
        require_trusted_documents: bool,
    ) -> None:
        self._trusted_operation_hashes = {value.lower() for value in trusted_operation_hashes}
        self._require_trusted_documents = require_trusted_documents

    def on_operation(self) -> Generator[None, None, None]:
        query = getattr(self.execution_context, "query", None)
        if not isinstance(query, str) or not query.strip():
            yield
            return

        operation_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()

        context = self.execution_context.context
        if context is None:
            context = {}
            self.execution_context.context = context
        context["operation_sha256"] = operation_hash

        if (
            self._require_trusted_documents
            and self._trusted_operation_hashes
            and operation_hash.lower() not in self._trusted_operation_hashes
        ):
            _observe_rejection(reason="untrusted_operation")
            raise GraphQLError(
                "Operation is not trusted. Use a persisted operation registered in the trusted allowlist."
            )

        yield


class QueryCostLimiterExtension(SchemaExtension):
    """Estimate and enforce a maximum GraphQL operation cost budget."""

    def __init__(self, *, max_cost: int) -> None:
        self._max_cost = max_cost

    def on_operation(self) -> Generator[None, None, None]:
        query = getattr(self.execution_context, "query", None)
        if not isinstance(query, str) or not query.strip():
            yield
            return

        parsed = self._parse_cost_input(query=query)
        if parsed is None:
            yield
            return

        operation, fragments = parsed
        cost = self._estimate_cost(operation.selection_set.selections, fragments=fragments, depth=1)

        self._observe_cost(operation=operation, cost=cost)
        self._store_cost(cost=cost)
        self._enforce_cost_limit(cost=cost)

        yield

    def _parse_cost_input(
        self,
        *,
        query: str,
    ) -> tuple[OperationDefinitionNode, dict[str, FragmentDefinitionNode]] | None:
        """Parse GraphQL query and resolve operation/fragments for cost estimation."""
        try:
            document = parse(query)
        except Exception:
            # Let GraphQL parse/validation produce canonical errors.
            return None

        operation_name = getattr(self.execution_context, "operation_name", None)
        operation = self._resolve_operation(document.definitions, operation_name=operation_name)
        if operation is None:
            return None

        fragments = {
            definition.name.value: definition
            for definition in document.definitions
            if isinstance(definition, FragmentDefinitionNode)
        }
        return operation, fragments

    @staticmethod
    def _observe_cost(*, operation: OperationDefinitionNode, cost: int) -> None:
        """Record estimated operation cost metric when available."""
        operation_type_raw = getattr(operation, "operation", None)
        operation_type = str(operation_type_raw) if operation_type_raw is not None else _METRIC_LABEL_UNKNOWN
        if _GRAPHQL_OPERATION_COST is not None:
            _GRAPHQL_OPERATION_COST.labels(operation_type=operation_type).observe(cost)

    def _store_cost(self, *, cost: int) -> None:
        """Persist computed operation cost in GraphQL execution context."""
        context = self.execution_context.context
        if context is None:
            context = {}
            self.execution_context.context = context
        context["operation_cost"] = cost

    def _enforce_cost_limit(self, *, cost: int) -> None:
        """Raise GraphQL policy error when operation cost exceeds configured budget."""
        if cost > self._max_cost:
            _observe_rejection(reason="cost_limit")
            raise GraphQLError(f"Query cost {cost} exceeds max allowed {self._max_cost}.")

    @staticmethod
    def _resolve_operation(
        definitions: tuple[object, ...],
        *,
        operation_name: str | None,
    ) -> OperationDefinitionNode | None:
        operation_definitions = [
            definition for definition in definitions if isinstance(definition, OperationDefinitionNode)
        ]
        if not operation_definitions:
            return None

        if operation_name is None:
            return operation_definitions[0]

        for definition in operation_definitions:
            name = getattr(definition, "name", None)
            if name is not None and name.value == operation_name:
                return definition
        return operation_definitions[0]

    def _estimate_cost(
        self,
        selections: tuple[SelectionNode, ...],
        *,
        fragments: dict[str, FragmentDefinitionNode],
        depth: int,
    ) -> int:
        total_cost = 0
        for selection in selections:
            if isinstance(selection, FieldNode):
                total_cost += depth
                if selection.selection_set is not None:
                    total_cost += self._estimate_cost(
                        selection.selection_set.selections,
                        fragments=fragments,
                        depth=depth + 1,
                    )
                continue

            if isinstance(selection, InlineFragmentNode):
                total_cost += self._estimate_cost(
                    selection.selection_set.selections,
                    fragments=fragments,
                    depth=depth,
                )
                continue

            if isinstance(selection, FragmentSpreadNode):
                fragment_name = selection.name.value
                fragment = fragments.get(fragment_name)
                if fragment is not None:
                    total_cost += self._estimate_cost(
                        fragment.selection_set.selections,
                        fragments=fragments,
                        depth=depth,
                    )

        return total_cost
