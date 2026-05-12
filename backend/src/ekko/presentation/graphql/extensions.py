"""Strawberry GraphQL extensions for Ekko."""

from __future__ import annotations

import asyncio
import inspect
import logging
import time
from typing import TYPE_CHECKING

from strawberry.extensions import SchemaExtension

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


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
        operation_name = getattr(operation, "name", "anonymous")
        logger.info("GraphQL operation %s completed in %.3fs", operation_name, elapsed)


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
