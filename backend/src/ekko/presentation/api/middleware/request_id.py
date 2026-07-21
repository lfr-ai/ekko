"""Request ID middleware for tracing."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response

_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Inject or forward X-Request-ID header."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(_HEADER) or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[_HEADER] = request_id
        return response
