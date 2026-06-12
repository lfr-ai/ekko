"""Application factory that wires the FastAPI app with routers and lifespan."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import FastAPI

from ekko.composition.container import Container
from ekko.composition.lifespan import create_lifespan
from ekko.config.logging_config import configure_logging
from ekko.config.openapi_config import (
    OPENAPI_CONTACT,
    OPENAPI_DESCRIPTION,
    OPENAPI_LICENSE,
    OPENAPI_RESPONSES,
    OPENAPI_SERVERS,
    OPENAPI_TAGS,
    OPENAPI_TERMS_OF_SERVICE,
    OPENAPI_TITLE,
    OPENAPI_VERSION,
)
from ekko.config.settings import get_settings
from ekko.core.registry_constants import ROUTE_DOCS, ROUTE_GRAPHQL, ROUTE_OPENAPI_JSON, ROUTE_REDOC
from ekko.presentation.api.rate_limiter import limiter
from ekko.presentation.api.routes import health_router, stream_router

logger = logging.getLogger(__name__)


# ── Middleware wiring ────────────────────────────────────────


def _register_middleware(app: FastAPI, container: Container) -> None:
    """Register all middleware in correct order (last added = first executed)."""
    from ekko.presentation.api.middleware import (
        AuthenticationMiddleware,
        RequestIdMiddleware,
        SecurityHeadersMiddleware,
        TimingMiddleware,
        register_exception_handlers,
        setup_cors,
    )

    # Error handlers (exception → HTTP response mapping)
    register_exception_handlers(app)

    # CORS
    setup_cors(app, settings=container.settings)

    # Middleware stack — order: Request ID → Security → Timing → Auth
    # (added in reverse because Starlette executes last-added first)
    app.add_middleware(AuthenticationMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)


# ── Static frontend serving (frozen EXE) ────────────────────


def _mount_frontend(app: FastAPI) -> None:
    """In a frozen PyInstaller bundle, serve the built frontend at /."""
    bundle_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else None
    if bundle_dir is None:
        return

    frontend_dir = bundle_dir / "frontend"
    if not frontend_dir.is_dir():
        logger.warning("No frontend/ directory found in bundle at %s", frontend_dir)
        return

    from starlette.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


# ── Router registration ──────────────────────────────────────


def _register_routers(app: FastAPI) -> None:
    """Register all API routers on the application."""
    # REST routers
    app.include_router(health_router)
    app.include_router(stream_router)

    # GraphQL router
    from ekko.presentation.graphql.router import graphql_router

    app.include_router(graphql_router, prefix=ROUTE_GRAPHQL)


# ── Factory ──────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Create and return a FastAPI application wired with routers."""
    configure_logging()
    settings = get_settings()
    container = Container(settings=settings)

    app = FastAPI(
        title=OPENAPI_TITLE,
        description=OPENAPI_DESCRIPTION,
        version=OPENAPI_VERSION,
        lifespan=create_lifespan,
        openapi_tags=OPENAPI_TAGS,
        servers=OPENAPI_SERVERS,
        contact=OPENAPI_CONTACT,
        license_info=OPENAPI_LICENSE,
        terms_of_service=OPENAPI_TERMS_OF_SERVICE,
        openapi_url=ROUTE_OPENAPI_JSON,
        docs_url=ROUTE_DOCS,
        redoc_url=ROUTE_REDOC,
        responses=OPENAPI_RESPONSES,
    )

    # Store container and rate limiter on app state
    app.state.container = container
    app.state.limiter = limiter

    # Register middleware
    _register_middleware(app, container)

    # Register routers
    _register_routers(app)

    # Serve built frontend when running as frozen EXE
    _mount_frontend(app)

    return app
