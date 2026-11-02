"""Application factory that wires the FastAPI app with routers and lifespan."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import FastAPI

from ekko import APP_NAME
from ekko.composition.container import Container
from ekko.composition.lifespan import create_lifespan
from ekko.config.openapi_config import (
    OPENAPI_CONTACT,
    OPENAPI_DESCRIPTION,
    OPENAPI_LICENSE,
    OPENAPI_RESPONSES,
    OPENAPI_SERVERS,
    OPENAPI_TAGS,
    OPENAPI_TITLE,
    OPENAPI_VERSION,
)
from ekko.config.runtime import get_config
from ekko.core.correlation_context import get_request_id
from ekko.core.registry_constants import (
    FIELD_REQUEST_ID,
    ROUTE_DOCS,
    ROUTE_OPENAPI_JSON,
    ROUTE_REDOC,
)
from ekko.infrastructure.logging import (
    ContextInjectingFilter,
    configure_logging,
    resolve_process_log_filename,
)
from ekko.presentation.api.rate_limiter import create_limiter
from ekko.presentation.api.routes import health_router, pii_router, stream_router, summarize_router, transcript_router

_logger = logging.getLogger(__name__)

# Third-party loggers forced to WARNING so their internals do not flood output.
_NOISY_LOGGERS = (
    "httpcore",
    "httpx",
    "hpack",
    "websockets",
    "watchfiles",
    "LiteLLM",
    "azure.core.pipeline.policies.http_logging_policy",
)
_CONTEXT_FIELD_ORDER = (FIELD_REQUEST_ID,)
_CONTEXT_FIELD_PROVIDERS = ((FIELD_REQUEST_ID, get_request_id),)


def _resolve_log_level(value: str | int) -> int:
    """Resolve a configured log level (name or numeric string) to its int value.

    Args:
        value (str | int): Configured level such as ``"INFO"``, ``"20"``, or ``20``.

    Returns:
        int: Numeric logging level; falls back to ``logging.INFO`` when unknown.
    """
    if isinstance(value, int):
        return value
    text = value.strip()
    if text.isdigit():
        return int(text)
    return logging.getLevelNamesMapping().get(text.upper(), logging.INFO)


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
    bundle_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)) if getattr(sys, "frozen", False) else None
    if bundle_dir is None:
        return

    frontend_dir = bundle_dir / "frontend"
    if not frontend_dir.is_dir():
        _logger.warning("Frontend bundle missing", extra={"frontend_dir": str(frontend_dir)})
        return

    from starlette.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


# ── Router registration ──────────────────────────────────────


def _register_routers(app: FastAPI) -> None:
    """Register all API routers on the application."""
    app.include_router(health_router)
    app.include_router(pii_router)
    app.include_router(stream_router)
    app.include_router(summarize_router)
    app.include_router(transcript_router)

    # GraphQL router — canonical endpoint at /graphql
    from ekko.presentation.graphql.router import graphql_router

    app.include_router(graphql_router)


# ── Factory ──────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Create and return a FastAPI application wired with routers."""
    settings = get_config()
    log_filename = resolve_process_log_filename(APP_NAME)
    configure_logging(
        log_dir_path=settings.logs_dir_path,
        log_filename=log_filename,
        log_level=_resolve_log_level(settings.log_level),
        record_filter=ContextInjectingFilter(field_providers=_CONTEXT_FIELD_PROVIDERS),
        prioritized_fields=_CONTEXT_FIELD_ORDER,
        noisy_loggers=_NOISY_LOGGERS,
    )
    _logger.info("Logging configured", extra={"log_file": log_filename, "environment": settings.environment})

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
        openapi_url=ROUTE_OPENAPI_JSON,
        docs_url=ROUTE_DOCS,
        redoc_url=ROUTE_REDOC,
        responses=OPENAPI_RESPONSES,
    )

    # Store container and rate limiter on app state
    app.state.container = container
    app.state.limiter = create_limiter(settings)
    app.state.pii_service = container.pii_service
    app.state.prompt_catalog_service = container.prompt_catalog_service
    app.state.readiness_service = container.readiness_service
    app.state.redis_client = container.redis_client
    app.state.summarizer_service = container.summarizer_service
    app.state.transcript_broadcaster = container.transcript_broadcaster

    # Register middleware
    _register_middleware(app, container)

    # Register routers
    _register_routers(app)

    # Prometheus HTTP metrics at /metrics
    if settings.metrics_enabled:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator(should_group_status_codes=True).instrument(app).expose(
            app,
            include_in_schema=False,
            endpoint="/metrics",
        )

    # Serve built frontend when running as frozen EXE
    _mount_frontend(app)

    _logger.info(
        "Application initialized",
        extra={"environment": settings.environment, "version": OPENAPI_VERSION},
    )
    return app
