"""Tests for prompt catalog orchestration."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from ekko.application.services import PromptCatalogService
from ekko.core.enums import Prompt


@dataclass(frozen=True, kw_only=True, slots=True)
class _PromptRegistry:
    """Deterministic prompt registry test double."""

    def load_prompt(self, prompt: Prompt) -> str:
        """Build prompt content from its identifier."""
        return f"content:{prompt.value}"


@pytest.mark.unit
def test_get_catalog_returns_every_active_prompt() -> None:
    """Expose all registered prompt templates in one catalog."""
    service = PromptCatalogService(prompt_registry=_PromptRegistry(), version_set="development")

    catalog = service.get_catalog()

    assert catalog.version_set == "development"
    assert {prompt.key for prompt in catalog.prompts} == {prompt.value for prompt in Prompt}


@pytest.mark.unit
def test_get_content_loads_only_requested_prompt() -> None:
    """Load template content through the selected catalog entry."""
    service = PromptCatalogService(prompt_registry=_PromptRegistry(), version_set="development")

    content = service.get_content(Prompt.SUMMARY_CHUNKS)

    assert content == "content:summary_chunks"