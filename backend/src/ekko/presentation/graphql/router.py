"""GraphQL router for FastAPI integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Request
from graphql import GraphQLError
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult

from ekko.config.runtime import get_config
from ekko.presentation.graphql.schema import schema

if TYPE_CHECKING:
    from collections.abc import Sequence

_INTERNAL_SERVER_ERROR_MESSAGE = "Internal server error"


def _sanitize_graphql_errors(*, errors: Sequence[GraphQLError]) -> list[object]:
    """Mask internal execution details while preserving safe GraphQL metadata.

    Validation and schema errors are preserved as-is because they are expected
    client-facing failures. Resolver/runtime exceptions are normalized to a
    generic message to avoid leaking sensitive internals.

    Args:
        errors (Sequence[GraphQLError]): GraphQL execution errors.

    Returns:
        list[object]: Safe formatted errors for the client response.
    """
    sanitized: list[object] = []

    for error in errors:
        formatted = error.formatted

        # Validation/spec errors: keep original detail for client feedback.
        if error.original_error is None:
            sanitized.append({str(key): value for key, value in formatted.items()})
            continue

        masked_error: dict[str, object] = {
            "message": _INTERNAL_SERVER_ERROR_MESSAGE,
        }

        path = formatted.get("path")
        if path is not None:
            masked_error["path"] = path

        locations = formatted.get("locations")
        if locations is not None:
            masked_error["locations"] = locations

        sanitized.append(masked_error)

    return sanitized


class EkkoGraphQLRouter(GraphQLRouter[dict[str, object], None]):
    """GraphQL router with production-safe error shaping."""

    async def process_result(
        self,
        request: Request,
        result: ExecutionResult,
    ) -> GraphQLHTTPResponse:
        """Post-process GraphQL responses to avoid leaking internal errors."""
        response = await super().process_result(request, result)

        # Keep full detail in debug mode for local diagnostics.
        if _settings.debug:
            return response

        if not result.errors:
            return response

        masked_response: GraphQLHTTPResponse = {"data": result.data}
        masked_response["errors"] = _sanitize_graphql_errors(errors=result.errors)
        return masked_response


async def get_context(request: Request) -> dict[str, object]:
    """Build per-request GraphQL context with application services.

    Dependencies are injected from app state and the composition container so
    the GraphQL layer stays free from infrastructure imports.

    Args:
        request (Request): Current FastAPI request.

    Returns:
        dict[str, object]: FastAPI request and application-service dependencies.
    """
    return {
        "request": request,
        "prompt_catalog_service": request.app.state.prompt_catalog_service,
    }


_settings = get_config()

graphql_router = EkkoGraphQLRouter(
    schema,
    path="/graphql",
    context_getter=get_context,
    graphql_ide="graphiql" if _settings.graphql_enable_ide else None,
    allow_queries_via_get=_settings.graphql_allow_get_queries,
    multipart_uploads_enabled=False,
)
