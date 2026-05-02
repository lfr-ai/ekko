"""Role-based authorization middleware.

In local-only mode (EXE), this always allows all requests.
Kept as a no-op middleware to preserve the middleware chain structure.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, final

from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response

logger = logging.getLogger(__name__)


@final
class AuthorizationMiddleware(BaseHTTPMiddleware):
    """No-op authorization — all requests allowed in local mode."""

    async def dispatch(self, request: Request, call_next) -> Response:
        return await call_next(request)
