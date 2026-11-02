"""Intent classification value object."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, kw_only=True, slots=True)
class IntentClassification:
    """Result of intent detection from user speech."""

    intent: str = "unknown"
    confidence: float = 0.0
    entities: dict[str, str] = field(default_factory=dict)
