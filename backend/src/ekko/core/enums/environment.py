"""Environment enum."""

from __future__ import annotations

from enum import auto, unique

from ekko.core.enums.base import ParseableEnum


@unique
class Environment(ParseableEnum):
    LOCAL = auto()
    DEV = auto()
    TEST = auto()
    STAGING = auto()
    PROD = auto()


__all__ = ["Environment"]
