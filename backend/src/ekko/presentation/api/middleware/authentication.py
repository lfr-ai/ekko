"""Authentication middleware.

In local-only mode (EXE), this always auto-authenticates with a dev user.
Kept as a no-op middleware to preserve the middleware chain structure.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response

logger = logging.getLogger(__name__)

_PUBLIC_PATHS = frozenset({"/health", "/docs", "/openapi.json", "/redoc"})


@dataclass(frozen=True, slots=True)
class UserProfile:
    """Authenticated user profile attached to request state."""

    username: str
    roles: frozenset[str] = frozenset()


@final
class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Auto-authenticate all requests with a local dev user."""

    def __init__(self, app, *, default_user_id: str = "dev-user") -> None:
        super().__init__(app)
        self._default_user_id = default_user_id

    async def dispatch(self, request: Request, call_next) -> Response:
        """Attach dev user to every request."""
        if request.url.path not in _PUBLIC_PATHS:
            request.state.user = UserProfile(username=self._default_user_id, roles=frozenset({"admin"}))
        return await call_next(request)
