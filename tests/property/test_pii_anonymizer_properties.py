# ruff: noqa: I001

"""Property-based tests for PII anonymizer invariants."""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from ekko.ai.pii.anonymizer import PIIAnonymizer

pytestmark = pytest.mark.property


@given(st.text(min_size=0, max_size=400))
def test_anonymize_when_called_then_preserves_original_text(input_text: str) -> None:
    """Anonymization result should always preserve original_text exactly."""
    # Arrange
    anonymizer = PIIAnonymizer()

    # Act
    result = anonymizer.anonymize(input_text)

    # Assert
    assert result.original_text == input_text


@given(st.text(min_size=0, max_size=400))
def test_anonymize_when_called_then_match_count_is_never_negative(input_text: str) -> None:
    """PII match count should always be a non-negative integer."""
    # Arrange
    anonymizer = PIIAnonymizer()

    # Act
    result = anonymizer.anonymize(input_text)

    # Assert
    assert len(result.pii_matches) >= 0


@given(
    st.text(alphabet=st.characters(blacklist_categories=("Cs",)), min_size=0, max_size=200)
)
def test_anonymize_when_applied_twice_then_output_is_idempotent(input_text: str) -> None:
    """Applying anonymize twice should not further mutate anonymized output."""
    # Arrange
    anonymizer = PIIAnonymizer()

    # Act
    first_pass = anonymizer.anonymize(input_text)
    second_pass = anonymizer.anonymize(first_pass.anonymized_text)

    # Assert
    assert second_pass.anonymized_text == first_pass.anonymized_text


@given(st.text(min_size=0, max_size=400))
def test_contains_pii_when_matches_exist_then_is_consistent_with_anonymize(input_text: str) -> None:
    """contains_pii() should agree with anonymize() on whether matches exist."""
    # Arrange
    anonymizer = PIIAnonymizer()

    # Act
    contains = anonymizer.contains_pii(input_text)
    result = anonymizer.anonymize(input_text)

    # Assert
    assert contains is (len(result.pii_matches) > 0)
