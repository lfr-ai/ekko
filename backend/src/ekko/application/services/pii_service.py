"""Application service enforcing PII policy at use-case boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from ekko.core.policies.pii_policy import PIIPolicyConfig, PIIPolicyOutcome, apply_pii_policy

if TYPE_CHECKING:
    from ekko.core.ports import PIIAnonymizerPort


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class PIIService:
    """Apply the configured PII policy to text."""

    anonymizer: PIIAnonymizerPort
    profile: str

    def anonymize(self, text: str) -> PIIPolicyOutcome:
        """Anonymize text according to the configured policy."""
        return apply_pii_policy(
            text=text,
            anonymizer=self.anonymizer,
            settings=PIIPolicyConfig(profile=self.profile),
        )
