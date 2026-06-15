"""Core-layer shared type aliases and scalar wrappers.

Centralizes domain-agnostic type definitions used across layers.
Follows the pattern established in the koda_automation golden standard.
"""

from __future__ import annotations

from typing import Self

__all__ = [
    "BaseDict",
    "Confidence",
    "JSONDict",
    "MaxTokens",
    "ModelDeploymentName",
    "PromptContent",
    "Temperature",
]

_MAX_TOKENS_LIMIT = 1_000_000

_MIN_TEMPERATURE = 0.0
_MAX_TEMPERATURE = 2.0

_MIN_CONFIDENCE = 0.0
_MAX_CONFIDENCE = 1.0

type PromptContent = str
type ModelDeploymentName = str

type BaseDict = dict[str, object]
type JSONDict = BaseDict


class MaxTokens(int):
    """Maximum completion token count constrained to a positive integer range."""

    def __new__(cls, max_tokens: int) -> Self:
        """Create and validate a new max tokens value.

        Args:
            max_tokens (int): Maximum tokens value to validate.

        Returns:
            Self: Validated max tokens instance.

        Raises:
            TypeError: If 'max_tokens' is not an integer.
            ValueError: If 'max_tokens' is out of bounds.
        """
        if isinstance(max_tokens, bool) or not isinstance(max_tokens, int):
            raise TypeError("'max_tokens' must be an integer")
        if max_tokens <= 0:
            raise ValueError(f"'max_tokens' must be positive, got: {max_tokens}")
        if max_tokens > _MAX_TOKENS_LIMIT:
            raise ValueError(f"'max_tokens' must not exceed {_MAX_TOKENS_LIMIT:,}, got: {max_tokens:,}")
        return super().__new__(cls, max_tokens)


class Temperature(float):
    """Sampling temperature constrained to the inclusive range '[0.0, 2.0]'."""

    def __new__(cls, temperature: float) -> Self:
        """Create and validate a new temperature value.

        Args:
            temperature (float): Temperature value to validate.

        Returns:
            Self: Validated temperature instance.

        Raises:
            TypeError: If 'temperature' is not numeric.
            ValueError: If 'temperature' is outside supported range.
        """
        if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
            raise TypeError("'temperature' must be a numeric value (int or float)")
        if not _MIN_TEMPERATURE <= temperature <= _MAX_TEMPERATURE:
            raise ValueError(
                f"'temperature' must be between {_MIN_TEMPERATURE} and {_MAX_TEMPERATURE}, got: {temperature}"
            )
        return super().__new__(cls, temperature)


class Confidence(float):
    """Model confidence score constrained to the inclusive range '[0.0, 1.0]'."""

    def __new__(cls, confidence: float) -> Self:
        """Create and validate a new confidence value.

        Args:
            confidence (float): Confidence value to validate.

        Returns:
            Self: Validated confidence instance.

        Raises:
            TypeError: If 'confidence' is not numeric.
            ValueError: If 'confidence' is outside supported range.
        """
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise TypeError("'confidence' must be a numeric value (int or float)")
        if not _MIN_CONFIDENCE <= confidence <= _MAX_CONFIDENCE:
            raise ValueError(f"'confidence' must be between {_MIN_CONFIDENCE} and {_MAX_CONFIDENCE}, got: {confidence}")
        return super().__new__(cls, confidence)
