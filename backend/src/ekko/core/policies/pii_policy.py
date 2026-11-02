"""Domain policy for PII handling on inbound text payloads.

Encodes the strict/standard decision rules for anonymizing user-provided
text before it reaches downstream AI or persistence. Framework-independent:
the anonymizer is consumed structurally so this module stays in the domain
core with no dependency on the AI or infrastructure verticals.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeGuard

_PII_POLICY_PROFILE_STANDARD = "standard"
_PII_POLICY_PROFILE_STRICT = "strict"

_PII_POLICY_VIOLATION_CODE = "PII_POLICY_VIOLATION"
_PII_POLICY_ANONYMIZER_FAILURE_CODE = "PII_ANONYMIZER_FAILURE"


class _AnonymizerResultProtocol(Protocol):
    """Protocol for a PII anonymizer result payload."""

    anonymized_text: str
    has_pii: bool
    pii_matches: tuple[object, ...]


class _PIIAnonymizerProtocol(Protocol):
    """Protocol for a PII anonymizer dependency."""

    def anonymize(self, text: str) -> _AnonymizerResultProtocol:
        """Anonymize the provided text payload."""


def _is_pii_anonymizer(candidate: object) -> TypeGuard[_PIIAnonymizerProtocol]:
    """Check whether *candidate* exposes an anonymize callable."""
    anonymize_attr = getattr(candidate, "anonymize", None)
    return callable(anonymize_attr)


@dataclass(frozen=True, kw_only=True, slots=True)
class PIIPolicyError:
    """PII policy error contract surfaced to callers."""

    code: str
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class PIIPolicyOutcome:
    """Result of applying PII policy to a text payload."""

    anonymized_text: str
    pii_found: bool
    match_count: int
    errors: tuple[PIIPolicyError, ...] = ()


@dataclass(frozen=True, kw_only=True, slots=True)
class PIIPolicyConfig:
    """Minimal PII policy configuration for a single operation."""

    profile: str

    @property
    def strict(self) -> bool:
        """Whether strict fail-closed policy should be applied."""
        return self.profile.strip().lower() == _PII_POLICY_PROFILE_STRICT


def apply_pii_policy(*, text: str, anonymizer: object | None, settings: PIIPolicyConfig) -> PIIPolicyOutcome:  # noqa: PLR0911
    """Apply strict/standard PII policy to one user-provided text payload."""
    strict_mode = settings.strict

    def _strict_violation(*, message: str, code: str = _PII_POLICY_VIOLATION_CODE) -> PIIPolicyOutcome:
        return PIIPolicyOutcome(
            anonymized_text="",
            pii_found=False,
            match_count=0,
            errors=(
                PIIPolicyError(
                    code=code,
                    message=message,
                ),
            ),
        )

    if anonymizer is None:
        if strict_mode:
            return _strict_violation(message="PII anonymizer is required by strict policy but is unavailable.")

        return PIIPolicyOutcome(
            anonymized_text=text,
            pii_found=False,
            match_count=0,
        )

    candidate = anonymizer
    if not _is_pii_anonymizer(candidate):
        if strict_mode:
            return _strict_violation(message="PII anonymizer in context is invalid for strict policy.")

        return PIIPolicyOutcome(anonymized_text=text, pii_found=False, match_count=0)

    try:
        result = candidate.anonymize(text)
    except Exception:  # noqa: BLE001  # anonymizer failure must fail closed under strict policy
        if strict_mode:
            return _strict_violation(
                message="PII anonymizer failed while strict policy is enabled.",
                code=_PII_POLICY_ANONYMIZER_FAILURE_CODE,
            )

        return PIIPolicyOutcome(anonymized_text=text, pii_found=False, match_count=0)

    pii_matches = getattr(result, "pii_matches", ())
    match_count = len(pii_matches) if isinstance(pii_matches, tuple) else 0

    return PIIPolicyOutcome(
        anonymized_text=str(getattr(result, "anonymized_text", text)),
        pii_found=bool(getattr(result, "has_pii", False)),
        match_count=match_count,
    )
