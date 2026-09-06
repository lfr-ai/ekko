"""Performance benchmarks for core backend hot paths."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import pytest

from ekko.ai.pii.anonymizer import PIIAnonymizer
from ekko.application.services import PromptCatalogService
from ekko.core.enums import Prompt
from ekko.presentation.graphql.schema import schema


@dataclass(frozen=True, kw_only=True, slots=True)
class _FakePromptRegistry:
    """Prompt registry returning deterministic template text."""

    def load_prompt(self, prompt: Prompt) -> str:
        """Build deterministic prompt content."""
        return f"Template for {prompt.value}"


@pytest.mark.performance
def test_pii_anonymization_when_processing_text_then_completes_within_baseline(
    benchmark,
) -> None:
    """Benchmark regex-based anonymization for representative PII payloads."""
    anonymizer = PIIAnonymizer()
    payload = (
        "Customer email alice@example.com called from +45 12 34 56 78 and provided "
        "card 4242 4242 4242 4242 near Nørregade 10"
    )

    result = benchmark(anonymizer.anonymize, payload)

    assert result.has_pii is True


@pytest.mark.performance
def test_graphql_prompt_catalog_query_when_executed_then_completes_within_baseline(
    benchmark,
) -> None:
    """Benchmark GraphQL prompt catalog query execution without network transport."""
    context = {
        "prompt_catalog_service": PromptCatalogService(
            prompt_registry=_FakePromptRegistry(),
            version_set="benchmark",
        )
    }
    query = "query { promptCatalog { versionSet prompts { key } } }"

    result = benchmark(lambda: asyncio.run(schema.execute(query, context_value=context)))

    assert result.errors is None
