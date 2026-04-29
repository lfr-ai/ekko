"""Compiled regex patterns for PII detection.

Covers Danish CPR numbers, Danish/international phone numbers,
email addresses, and common address patterns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PIIPattern:
    """A named PII detection pattern."""

    name: str
    pattern: re.Pattern[str]
    replacement: str


# Danish CPR number: DDMMYY-XXXX or DDMMYYXXXX
_CPR_PATTERN = re.compile(r"\b(0[1-9]|[12]\d|3[01])(0[1-9]|1[0-2])(\d{2})[-\s]?(\d{4})\b")

# Phone numbers: Danish (+45), international, or local 8-digit
_PHONE_PATTERN = re.compile(r"(?:\+\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}\b")

# Email addresses
_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

# Danish addresses (street + number pattern)
_ADDRESS_PATTERN = re.compile(
    r"\b[A-ZÆØÅ][a-zæøå]+(?:vej|gade|alle|vænge|plads|torv|stræde)\s+\d+\b",
    re.UNICODE,
)

# Credit card numbers (basic pattern)
_CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")


PII_PATTERNS: tuple[PIIPattern, ...] = (
    PIIPattern(name="cpr", pattern=_CPR_PATTERN, replacement="[CPR-REDACTED]"),
    PIIPattern(name="email", pattern=_EMAIL_PATTERN, replacement="[EMAIL-REDACTED]"),
    PIIPattern(name="phone", pattern=_PHONE_PATTERN, replacement="[PHONE-REDACTED]"),
    PIIPattern(name="address", pattern=_ADDRESS_PATTERN, replacement="[ADDRESS-REDACTED]"),
    PIIPattern(name="credit_card", pattern=_CREDIT_CARD_PATTERN, replacement="[CARD-REDACTED]"),
)
