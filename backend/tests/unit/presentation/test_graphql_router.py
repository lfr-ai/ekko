"""Unit tests for GraphQL router response and websocket handshake behavior."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from strawberry.exceptions import ConnectionRejectionError
from strawberry.types.unset import UNSET

from ekko.presentation.api.middleware.authentication import UserProfile
from ekko.presentation.graphql import router as graphql_router_module
from ekko.presentation.graphql.router import EkkoGraphQLRouter, graphql_router


@pytest.mark.unit
class TestGraphQLSubscriptionConnectAuthorization:
    """Validate subscription connect authorization policy behavior."""

    @pytest.mark.asyncio
    async def test_on_ws_connect_when_auth_disabled_then_accepts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Handshake should be accepted when subscription auth policy is disabled."""
        policy_settings = SimpleNamespace(
            graphql_subscription_auth_required=False,
            graphql_subscription_accept_connection_params_user=True,
            graphql_subscription_required_roles=("admin",),
        )
        monkeypatch.setattr(graphql_router_module, "_settings", policy_settings)

        request = SimpleNamespace(state=SimpleNamespace(user=None))
        context = {"request": request}

        result = await graphql_router.on_ws_connect(context)

        assert result is UNSET

    @pytest.mark.asyncio
    async def test_on_ws_connect_when_request_user_exists_then_accepts(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Handshake should be accepted when request.state.user already exists."""
        policy_settings = SimpleNamespace(
            graphql_subscription_auth_required=True,
            graphql_subscription_accept_connection_params_user=False,
            graphql_subscription_required_roles=("admin",),
        )
        monkeypatch.setattr(graphql_router_module, "_settings", policy_settings)

        request = SimpleNamespace(
            state=SimpleNamespace(
                user=UserProfile(username="dev-user", roles=frozenset({"admin"})),
            )
        )
        context = {"request": request}

        result = await graphql_router.on_ws_connect(context)

        assert result is UNSET

    @pytest.mark.asyncio
    async def test_on_ws_connect_when_connection_params_authorized_then_sets_user_and_accepts(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Handshake should accept and project user from connection params when policy allows."""
        policy_settings = SimpleNamespace(
            graphql_subscription_auth_required=True,
            graphql_subscription_accept_connection_params_user=True,
            graphql_subscription_required_roles=("admin",),
        )
        monkeypatch.setattr(graphql_router_module, "_settings", policy_settings)

        request = SimpleNamespace(state=SimpleNamespace(user=None))
        context = {
            "request": request,
            "connection_params": {
                "username": "alice",
                "roles": ["admin", "subscriber"],
            },
        }

        result = await graphql_router.on_ws_connect(context)

        assert result is UNSET
        assert request.state.user is not None
        assert request.state.user.username == "alice"
        assert request.state.user.roles == frozenset({"admin", "subscriber"})

    @pytest.mark.asyncio
    async def test_on_ws_connect_when_connection_params_missing_required_role_then_rejects(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Handshake should be rejected when required subscription role is missing."""
        policy_settings = SimpleNamespace(
            graphql_subscription_auth_required=True,
            graphql_subscription_accept_connection_params_user=True,
            graphql_subscription_required_roles=("admin",),
        )
        monkeypatch.setattr(graphql_router_module, "_settings", policy_settings)

        request = SimpleNamespace(state=SimpleNamespace(user=None))
        context = {
            "request": request,
            "connection_params": {
                "username": "bob",
                "roles": ["subscriber"],
            },
        }

        with pytest.raises(ConnectionRejectionError):
            await graphql_router.on_ws_connect(context)


@pytest.mark.unit
class TestGraphQLRouterType:
    """Sanity checks for the exported router instance type."""

    def test_graphql_router_is_custom_router_instance(self) -> None:
        """Exported router should be the custom router subclass instance."""
        assert isinstance(graphql_router, EkkoGraphQLRouter)
