"""Unit tests for GraphQL router response behavior."""

from __future__ import annotations

import pytest

from ekko.presentation.graphql.router import EkkoGraphQLRouter, graphql_router


@pytest.mark.unit
class TestGraphQLRouterType:
    """Sanity checks for the exported router instance type."""

    def test_graphql_router_is_custom_router_instance(self) -> None:
        """Exported router should be the custom router subclass instance."""
        assert isinstance(graphql_router, EkkoGraphQLRouter)
