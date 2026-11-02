"""Base enum utilities for the Ekko project.

Provides 'ParseableEnum' — the standard base class for all string enums —
and the 'enum_values' helper.
"""

from __future__ import annotations

from enum import StrEnum


class ParseableEnum(StrEnum):
    """Base class for all Ekko string enums.

    Adds 'from_str()' for case-insensitive parsing.
    """

    @classmethod
    def from_str(cls, value: str) -> ParseableEnum:
        """Parse a string value to an enum member (case-insensitive).

        Args:
            value (str): Text to match against the enum values.

        Returns:
            ParseableEnum: Matching enum member.

        Raises:
            ValueError: If value does not match any member.
        """
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        msg = f"{value!r} is not a valid {cls.__name__}. Valid: {[m.value for m in cls]}"
        raise ValueError(msg)


def enum_values(enum_cls: type[StrEnum]) -> list[str]:
    """List the string values of a StrEnum class in declaration order.

    Args:
        enum_cls (type[StrEnum]): StrEnum class to extract values from.

    Returns:
        list[str]: String values in declaration order.
    """
    return [e.value for e in enum_cls]


__all__ = ["ParseableEnum", "enum_values"]
