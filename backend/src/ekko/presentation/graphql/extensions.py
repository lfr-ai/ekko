"""Strawberry GraphQL extensions for Ekko."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from strawberry.extensions import SchemaExtension

from ekko.core.correlation_context import get_request_id

if TYPE_CHECKING:
    from collections.abc import Generator

_logger = logging.getLogger(__name__)

_UNKNOWN_OPERATION_TYPE = "unknown"
_STATUS_ERROR = "error"
_STATUS_OK = "ok"
_QUERY_DURATION_DECIMAL_PLACES = 6


class QueryTimingExtension(SchemaExtension):
    """Log execution time for each GraphQL operation."""

    def on_operation(self) -> Generator[None]:
        """Log operation name, type, status, and duration."""
        start = time.monotonic()
        yield
        elapsed = time.monotonic() - start
        operation = getattr(self.execution_context, "operation", None)
        operation_name = getattr(operation, "name", None)
        operation_type_raw = getattr(operation, "operation", None)
        operation_type = str(operation_type_raw) if operation_type_raw is not None else _UNKNOWN_OPERATION_TYPE
        operation_name_text = getattr(operation_name, "value", "anonymous")
        errors = getattr(self.execution_context, "errors", None)
        status = _STATUS_ERROR if errors else _STATUS_OK

        _logger.info(
            "GraphQL operation completed",
            extra={
                "operation_name": operation_name_text,
                "operation_type": operation_type,
                "duration_seconds": round(elapsed, _QUERY_DURATION_DECIMAL_PLACES),
                "status": status,
            },
        )


class RequestContextExtension(SchemaExtension):
    """Inject request metadata into the GraphQL context."""

    def on_operation(self) -> Generator[None]:
        """Bind the request correlation id into the GraphQL context."""
        context = self.execution_context.context
        if context is None:
            context = {}
            self.execution_context.context = context

        request = context.get("request")
        if request:
            context["request_id"] = get_request_id()
        yield
