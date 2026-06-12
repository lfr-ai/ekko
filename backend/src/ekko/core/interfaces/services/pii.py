"""PII anonymizer port protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from ekko.core.value_objects import AnonymizedText


@runtime_checkable
class PIIAnonymizerPort(Protocol):
    """Port for PII anonymization.

    Implementations detect and redact personally identifiable information.
    """

    def anonymize(self, text: str) -> AnonymizedText:
        """Detect and replace PII in the given text."""
        ...

    def contains_pii(self, text: str) -> bool:
        """Quick check whether text contains any PII."""
        ...
