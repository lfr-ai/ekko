"""Prompt catalog GraphQL query."""

from __future__ import annotations

import strawberry
from strawberry.types import Info

from ekko.presentation.graphql.types import PromptCatalogType, PromptType


@strawberry.type
class Query:
    """Root query type."""

    @strawberry.field
    async def prompt_catalog(self, info: Info) -> PromptCatalogType:
        """Provide the active prompt catalog."""
        catalog = info.context["prompt_catalog_service"].get_catalog()
        return PromptCatalogType(
            version_set=catalog.version_set,
            prompts=[PromptType(key=prompt.key) for prompt in catalog.prompts],
        )
