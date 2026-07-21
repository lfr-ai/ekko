"""GraphQL router for FastAPI integration."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Final, Protocol, cast

from fastapi import Request
from graphql import GraphQLError
from strawberry.exceptions import ConnectionRejectionError
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.http.typevars import Context
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from strawberry.types import ExecutionResult
from strawberry.types.unset import UNSET, UnsetType

try:
    from strawberry.subscriptions import GRAPHQL_SSE_PROTOCOL
except ImportError:  # pragma: no cover - depends on installed Strawberry version
    GRAPHQL_SSE_PROTOCOL = None

from ekko.config.settings import get_settings
from ekko.presentation.graphql.dataloaders import create_dataloaders
from ekko.presentation.graphql.schema import schema

if TYPE_CHECKING:
    from collections.abc import Sequence

_INTERNAL_SERVER_ERROR_MESSAGE: Final[str] = "Internal server error"
_CONNECTION_PARAM_USER_KEYS: Final[tuple[str, ...]] = (
    "user",
    "username",
    "user_id",
)
_CONNECTION_PARAM_ROLES_KEYS: Final[tuple[str, ...]] = ("roles", "role")


class _RequestStateProtocol(Protocol):
    """Typed protocol for request.state user assignment during WS auth."""

    user: object


def _extract_roles(*, value: object) -> frozenset[str]:
    """Normalize role payload into a case-insensitive role set."""
    if isinstance(value, str):
        return frozenset({value.strip().lower()}) if value.strip() else frozenset()

    if isinstance(value, Iterable):
        roles = {str(item).strip().lower() for item in value if str(item).strip()}
        return frozenset(roles)

    return frozenset()


def _resolve_connection_param(*, payload: dict[str, object], keys: tuple[str, ...]) -> object | None:
    """Resolve the first present connection param value by key alias order."""
    for key in keys:
        if key in payload:
            return payload[key]
    return None


def _resolve_request_state(*, context: Context) -> tuple[object, object | None]:
    """Resolve request and request.state from websocket connect context."""
    if not isinstance(context, dict):
        raise ConnectionRejectionError

    context_dict = cast("dict[str, object]", context)
    request = context_dict.get("request")
    if request is None:
        raise ConnectionRejectionError

    return request, getattr(request, "state", None)


def _build_user_from_connection_params(*, context: Context) -> object:
    """Build a user profile from accepted websocket connection params."""
    if not isinstance(context, dict):
        raise ConnectionRejectionError

    context_dict = cast("dict[str, object]", context)
    raw_params = context_dict.get("connection_params")
    if not isinstance(raw_params, dict):
        raise ConnectionRejectionError

    params = {str(key): value for key, value in raw_params.items()}
    username_value = _resolve_connection_param(payload=params, keys=_CONNECTION_PARAM_USER_KEYS)
    if not isinstance(username_value, str) or not username_value.strip():
        raise ConnectionRejectionError

    raw_roles = _resolve_connection_param(payload=params, keys=_CONNECTION_PARAM_ROLES_KEYS)
    roles = _extract_roles(value=raw_roles if raw_roles is not None else ("admin",))
    required_roles = {role.lower() for role in _settings.graphql_subscription_required_roles}
    if required_roles and not required_roles.issubset(roles):
        raise ConnectionRejectionError

    from ekko.presentation.api.middleware.authentication import UserProfile

    return UserProfile(username=username_value.strip(), roles=roles)


def _coerce_request_state(*, state: object | None) -> _RequestStateProtocol:
    """Return request state with a guaranteed user attribute target."""
    if state is None:
        raise ConnectionRejectionError
    if not hasattr(state, "user"):
        raise ConnectionRejectionError
    return cast("_RequestStateProtocol", state)


def _sanitize_graphql_errors(*, errors: Sequence[GraphQLError]) -> list[object]:
    """Mask internal execution details while preserving safe GraphQL metadata.

    Validation and schema errors are preserved as-is because they are expected
    client-facing failures. Resolver/runtime exceptions are normalized to a
    generic message to avoid leaking sensitive internals.
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

        extensions = formatted.get("extensions")
        if isinstance(extensions, dict):
            masked_extensions = {str(key): value for key, value in extensions.items() if str(key) != "exception"}
            if masked_extensions:
                masked_error["extensions"] = masked_extensions

        sanitized.append(masked_error)

    return sanitized


class EkkoGraphQLRouter(GraphQLRouter):
    """GraphQL router with production-safe error shaping."""

    async def on_ws_connect(
        self,
        context: Context,
    ) -> UnsetType | None | dict[str, object]:
        """Authorize subscription handshakes according to explicit policy.

        Policy:
        - when disabled, all connects are accepted.
        - when enabled, request.state.user must exist OR identity must be supplied
          via connection init params and satisfy required roles.
        """
        if not _settings.graphql_subscription_auth_required:
            return UNSET

        _, state = _resolve_request_state(context=context)
        typed_state = _coerce_request_state(state=state)
        existing_user = getattr(typed_state, "user", None)
        if existing_user is not None:
            return UNSET

        if not _settings.graphql_subscription_accept_connection_params_user:
            raise ConnectionRejectionError

        typed_state.user = _build_user_from_connection_params(context=context)
        return UNSET

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


async def get_context(request: Request):
    """Build per-request GraphQL context with dataloaders and infrastructure.

    Infrastructure dependencies (db_engine, session_factory, pii_anonymizer)
    are injected from app.state so the GraphQL layer stays free from
    infrastructure imports.
    """
    ctx: dict[str, object] = {**create_dataloaders(), "request": request}

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


_settings = get_settings()

_subscription_protocols: list[str] = [GRAPHQL_TRANSPORT_WS_PROTOCOL]

if _settings.graphql_enable_legacy_ws_protocol:
    _subscription_protocols.append(GRAPHQL_WS_PROTOCOL)

if _settings.graphql_enable_sse_subscriptions and GRAPHQL_SSE_PROTOCOL is not None:
    _subscription_protocols.append(GRAPHQL_SSE_PROTOCOL)

graphql_router = EkkoGraphQLRouter(
    schema,
    path="/graphql",
    context_getter=get_context,
    graphql_ide="graphiql" if _settings.graphql_enable_ide else None,
    allow_queries_via_get=_settings.graphql_allow_get_queries,
    multipart_uploads_enabled=False,
    subscription_protocols=_subscription_protocols,
)
