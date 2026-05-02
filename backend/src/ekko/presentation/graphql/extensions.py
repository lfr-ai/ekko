"""Strawberry GraphQL extensions for Ekko."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from strawberry.extensions import SchemaExtension

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logger = logging.getLogger(__name__)


class SessionLifecycleExtension(SchemaExtension):
    """Per-request database session lifecycle.

    Creates an async SQLAlchemy session at the start of each GraphQL operation
    and closes it when the operation completes. The session factory is read
    from the GraphQL context (injected at router level), keeping this
    extension free from infrastructure imports.
    """

    async def on_operation(self) -> AsyncGenerator[None, None]:
        session = None
        try:
            session_factory = self.execution_context.context.get("session_factory")
            if session_factory is not None:
                session = session_factory()
                self.execution_context.context["db_session"] = session
            else:
                logger.debug("No session_factory in context; skipping DB session setup")
                self.execution_context.context["db_session"] = None
        except Exception:
            logger.debug("DB session not available (database may not be configured)")
            self.execution_context.context["db_session"] = None

        try:
            yield
        finally:
            if session is not None:
                await session.close()


class QueryTimingExtension(SchemaExtension):
    """Log execution time for each GraphQL operation."""

    async def on_operation(self) -> AsyncGenerator[None, None]:
        start = time.monotonic()
        yield
        elapsed = time.monotonic() - start
        operation = getattr(self.execution_context, "operation", None)
        operation_name = getattr(operation, "name", "anonymous")
        logger.info("GraphQL operation %s completed in %.3fs", operation_name, elapsed)


class RequestContextExtension(SchemaExtension):
    """Inject request metadata into the GraphQL context."""

    async def on_operation(self) -> AsyncGenerator[None, None]:
        request = self.execution_context.context.get("request")
        if request:
            self.execution_context.context["request_id"] = getattr(request.state, "request_id", None)
        yield
