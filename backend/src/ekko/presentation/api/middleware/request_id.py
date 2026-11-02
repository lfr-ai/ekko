"""HTTP correlation middleware.

Binds a request correlation id to the execution context so every log record
emitted while handling the request is enriched with it automatically. A pure
ASGI middleware is used (rather than ``BaseHTTPMiddleware``) so the bound
context variable reliably propagates into downstream handlers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from starlette.datastructures import Headers, MutableHeaders

from ekko.core.correlation_context import bind_request_id

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Message, Receive, Scope, Send

_HEADER = "X-Request-ID"


def _resolve_request_id(scope: Scope) -> str:
    """Extract the inbound request id header, or generate a fresh one.

    Args:
        scope (Scope): ASGI connection scope.

    Returns:
        str: Correlation id for the current request.
    """
    if inbound := Headers(scope=scope).get(_HEADER):
        return inbound
    return str(uuid4())


class RequestIdMiddleware:
    """Inject or forward the request correlation id and bind it to the context."""

    def __init__(self, app: ASGIApp):
        """Store the wrapped ASGI application.

        Args:
            app (ASGIApp): Downstream ASGI application.
        """
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Bind the request id for the request lifetime and echo it to the client.

        Args:
            scope (Scope): ASGI connection scope.
            receive (Receive): ASGI receive channel.
            send (Send): ASGI send channel.
        """
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        request_id = _resolve_request_id(scope)

        async def _send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(raw=message["headers"])[_HEADER] = request_id
            await send(message)

        with bind_request_id(request_id):
            await self._app(scope, receive, _send_with_request_id)
