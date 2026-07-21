"""PII detection and anonymization value objects."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PIIMatch:
    """A detected PII occurrence."""

    entity_type: str = ""
    start: int = 0
    end: int = 0
    text: str = ""
    score: float = 0.0


@dataclass(frozen=True, slots=True)
class AnonymizedText:
    """Result of PII anonymization."""

    original_text: str = ""
    anonymized_text: str = ""
    pii_matches: tuple[PIIMatch, ...] = ()

    @property
    def has_pii(self) -> bool:
        """Whether any PII was detected."""
        return len(self.pii_matches) > 0
