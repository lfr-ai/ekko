"""Shared PII policy behavior for GraphQL ingress paths."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, cast

_PII_POLICY_PROFILE_STANDARD = "standard"
_PII_POLICY_PROFILE_STRICT = "strict"

_PII_POLICY_VIOLATION_CODE = "PII_POLICY_VIOLATION"
_PII_POLICY_ANONYMIZER_FAILURE_CODE = "PII_ANONYMIZER_FAILURE"


class _AnonymizerResultProtocol(Protocol):
    """Protocol for PII anonymizer result payload."""

    anonymized_text: str
    has_pii: bool
    pii_matches: tuple[object, ...]


class _PIIAnonymizerProtocol(Protocol):
    """Protocol for PII anonymizer used in GraphQL context."""

    def anonymize(self, text: str) -> _AnonymizerResultProtocol:
        """Anonymize the provided text payload."""


@dataclass(frozen=True, slots=True)
class PIIPolicyError:
    """PII policy error contract used by GraphQL typed results."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class PIIPolicyOutcome:
    """Result of applying PII policy to a text payload."""

    anonymized_text: str
    pii_found: bool
    match_count: int
    errors: tuple[PIIPolicyError, ...] = ()


@dataclass(frozen=True, slots=True)
class PIIPolicySettings:
    """Minimal PII policy configuration for GraphQL operations."""

    profile: str

    @property
    def strict(self) -> bool:
        """Whether strict fail-closed policy should be applied."""
        return self.profile.strip().lower() == _PII_POLICY_PROFILE_STRICT


def apply_pii_policy(*, text: str, anonymizer: object | None, settings: PIIPolicySettings) -> PIIPolicyOutcome:  # noqa: PLR0911
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
    if not hasattr(candidate, "anonymize"):
        if strict_mode:
            return _strict_violation(message="PII anonymizer in context is invalid for strict policy.")

        return PIIPolicyOutcome(anonymized_text=text, pii_found=False, match_count=0)

    try:
        typed_candidate = cast("_PIIAnonymizerProtocol", candidate)
        result = typed_candidate.anonymize(text)
    except Exception:
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


def render_subscription_text(
    *,
    text: str,
    anonymizer: object | None,
    settings: PIIPolicySettings,
) -> str:
    """Render transcript text according to policy for subscription streaming."""
    outcome = apply_pii_policy(text=text, anonymizer=anonymizer, settings=settings)
    if outcome.errors and settings.strict:
        return "[PII-REDACTION-UNAVAILABLE]"
    return outcome.anonymized_text
