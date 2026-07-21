"""PII anonymizer — scrubs sensitive data before sending to LLM/HMAS."""

from __future__ import annotations

import logging

from ekko.ai.pii.patterns import PII_PATTERNS, PIIPattern
from ekko.core.value_objects import AnonymizedText, PIIMatch

logger = logging.getLogger(__name__)


class PIIAnonymizer:
    """Regex-based PII anonymizer.

    Usage::

        anonymizer = PIIAnonymizer()
        result = anonymizer.anonymize("Ring mig på 12345678")
        assert "[PHONE-REDACTED]" in result.anonymized_text
    """

    def __init__(
        self,
        patterns: tuple[PIIPattern, ...] = PII_PATTERNS,
        *,
        enabled_types: frozenset[str] | None = None,
    ) -> None:
        if enabled_types is not None:
            self._patterns = tuple(p for p in patterns if p.name in enabled_types)
        else:
            self._patterns = patterns

    def anonymize(self, text: str) -> AnonymizedText:
        """Detect and replace PII in the given text."""
        matches: list[PIIMatch] = []
        anonymized = text

        for pattern in self._patterns:
            matches.extend(
                PIIMatch(
                    entity_type=pattern.name,
                    start=match.start(),
                    end=match.end(),
                    text=match.group(),
                    score=1.0,
                )
                for match in pattern.pattern.finditer(text)
            )

            anonymized = pattern.pattern.sub(pattern.replacement, anonymized)

        if matches:
            logger.info("Anonymized %d PII occurrence(s)", len(matches))

        return AnonymizedText(
            original_text=text,
            anonymized_text=anonymized,
            pii_matches=tuple(matches),
        )

    def contains_pii(self, text: str) -> bool:
        """Quick check whether text contains any PII."""
        return any(p.pattern.search(text) for p in self._patterns)
