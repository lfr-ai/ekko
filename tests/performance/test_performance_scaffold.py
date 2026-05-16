"""Performance benchmarks for core backend hot paths."""

from __future__ import annotations

import asyncio

import pytest

from ekko.ai.pii.anonymizer import PIIAnonymizer
from ekko.presentation.graphql.schema import schema


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
def test_graphql_health_query_when_executed_then_completes_within_baseline(
    benchmark,
) -> None:
    """Benchmark GraphQL health query execution without network transport."""
    query = "query { health { status environment } }"

    result = benchmark(lambda: asyncio.run(schema.execute(query)))

    assert result.errors is None
