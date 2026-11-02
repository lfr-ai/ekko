"""Strawberry types for the prompt catalog GraphQL API."""

from __future__ import annotations

import strawberry
from strawberry.types import Info


@strawberry.type
class PromptType:
    """Prompt catalog entry."""

    key: str

    @strawberry.field
    async def content(self, info: Info) -> str:
        """Load template content when selected by the client."""
        return info.context["prompt_catalog_service"].get_content(self.key)


@strawberry.type
class PromptCatalogType:
    """Active prompt catalog."""

    version_set: str
    prompts: list[PromptType]
