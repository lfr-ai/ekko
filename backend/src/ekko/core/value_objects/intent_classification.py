"""Intent classification value object."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class IntentClassification:
    """Result of intent detection from user speech."""

    intent: str = "unknown"
    confidence: float = 0.0
    entities: dict[str, str] = field(default_factory=dict)
