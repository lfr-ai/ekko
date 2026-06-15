"""GraphQL router for FastAPI integration."""

from __future__ import annotations

from fastapi import Request
from strawberry.fastapi import GraphQLRouter

from ekko.presentation.graphql.dataloaders import create_dataloaders
from ekko.presentation.graphql.schema import schema


async def get_context(request: Request) -> dict:
    """Build per-request GraphQL context with dataloaders and infrastructure.

    Infrastructure dependencies (db_engine, session_factory, pii_anonymizer)
    are injected from app.state so the GraphQL layer stays free from
    infrastructure imports.
    """
    ctx: dict = {**create_dataloaders(), "request": request}

    container = getattr(request.app.state, "container", None)
    if container is not None:
        ctx["pii_anonymizer"] = container.pii_anonymizer

    # Inject DB engine and session factory if available
    db_engine = getattr(request.app.state, "db_engine", None)
    if db_engine is not None:
        ctx["db_engine"] = db_engine

    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is not None:
        ctx["session_factory"] = session_factory

    return ctx


graphql_router = GraphQLRouter(
    schema,
    path="/",
    context_getter=get_context,
)
