"""Tests for the minimal prompt catalog GraphQL schema."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from ekko.application.services import PromptCatalogService
from ekko.core.enums import Prompt
from ekko.presentation.graphql.extensions import QueryTimingExtension, RequestContextExtension
from ekko.presentation.graphql.schema import schema


@dataclass(frozen=True, kw_only=True, slots=True)
class _FakePromptRegistry:
    """Prompt registry returning deterministic template text."""

    def load_prompt(self, prompt: Prompt) -> str:
        """Build deterministic prompt content."""
        return f"Template for {prompt.value}"


def _context() -> dict[str, object]:
    return {
        "prompt_catalog_service": PromptCatalogService(
            prompt_registry=_FakePromptRegistry(),
            version_set="test",
        )
    }


@pytest.mark.unit
def test_schema_exposes_only_prompt_catalog_query() -> None:
    """Keep GraphQL limited to its one justified read graph."""
    assert schema.query is not None
    assert schema.mutation is None
    assert schema.subscription is None
    assert {field.python_name for field in schema.query.__strawberry_definition__.fields} == {"prompt_catalog"}


@pytest.mark.unit
def test_schema_keeps_lightweight_observability_extensions() -> None:
    """Keep operation timing and request correlation."""
    extension_names = {extension.__name__ for extension in schema.extensions if isinstance(extension, type)}

    assert extension_names == {
        QueryTimingExtension.__name__,
        RequestContextExtension.__name__,
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_prompt_catalog_supports_nested_field_selection() -> None:
    """Query active prompt metadata and nested templates in one request."""
    result = await schema.execute(
        """
        query PromptCatalog {
          promptCatalog {
            versionSet
            prompts { key content }
          }
        }
        """,
        context_value=_context(),
    )

    assert result.errors is None
    assert result.data is not None
    catalog = result.data["promptCatalog"]
    assert catalog["versionSet"] == "test"
    assert {prompt["key"] for prompt in catalog["prompts"]} == {prompt.value for prompt in Prompt}
    assert all(prompt["content"].startswith("Template for ") for prompt in catalog["prompts"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_prompt_catalog_can_omit_template_content() -> None:
    """Let clients request only the catalog metadata they need."""
    result = await schema.execute(
        "query PromptKeys { promptCatalog { prompts { key } } }",
        context_value=_context(),
    )

    assert result.errors is None
    assert result.data is not None
    assert all(set(prompt) == {"key"} for prompt in result.data["promptCatalog"]["prompts"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unknown_query_field_returns_validation_error() -> None:
    """Reject fields outside the intentionally small schema."""
    result = await schema.execute("query Unknown { health { status } }")

    assert result.errors is not None
    assert result.data is None
