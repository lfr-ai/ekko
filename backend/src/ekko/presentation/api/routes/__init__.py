"""Presentation routers."""

from ekko.presentation.api.routes.health import router as health_router
from ekko.presentation.api.routes.pii import router as pii_router
from ekko.presentation.api.routes.stream import router as stream_router
from ekko.presentation.api.routes.summarize import router as summarize_router
from ekko.presentation.api.routes.transcript import router as transcript_router

__all__ = ["health_router", "pii_router", "stream_router", "summarize_router", "transcript_router"]
