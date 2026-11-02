"""HTTP timing middleware."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, final, override

from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from starlette.middleware.base import RequestResponseEndpoint
    from starlette.requests import Request
    from starlette.responses import Response

_logger = logging.getLogger(__name__)

_MILLISECONDS_PER_SECOND = 1000


@final
class TimingMiddleware(BaseHTTPMiddleware):
    """Measure request duration and add Server-Timing header."""

    @override
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Time the downstream request and add a Server-Timing header."""
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * _MILLISECONDS_PER_SECOND
        response.headers["Server-Timing"] = f"total;dur={duration_ms:.1f}"
        _logger.debug(
            "HTTP request completed",
            extra={
                "method": request.method,
                "scheme": request.url.scheme,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 1),
            },
        )
        return response
