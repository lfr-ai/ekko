"""Tests for PII policy orchestration."""

from __future__ import annotations

import pytest

from ekko.ai.pii.anonymizer import PIIAnonymizer
from ekko.application.services import PIIService


@pytest.mark.unit
def test_anonymize_applies_configured_policy() -> None:
    """Redact detected PII through the application boundary."""
    service = PIIService(anonymizer=PIIAnonymizer(), profile="strict")

    result = service.anonymize("Email me at test@example.com")

    assert result.errors == ()
    assert result.pii_found is True
    assert result.match_count == 1
    assert "test@example.com" not in result.anonymized_text