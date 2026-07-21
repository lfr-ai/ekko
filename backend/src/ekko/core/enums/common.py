"""Common utility enums."""

from __future__ import annotations

from enum import IntEnum, auto, unique

from ekko.core.enums.base import ParseableEnum


@unique
class LogLevel(IntEnum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@unique
class ServiceStatus(ParseableEnum):
    """Health status for service dependency checks."""

    HEALTHY = auto()
    DEGRADED = auto()
    UNHEALTHY = auto()
    UNKNOWN = auto()


@unique
class SortOrder(ParseableEnum):
    """Sort direction for list queries."""

    ASC = auto()
    DESC = auto()


__all__ = ["LogLevel", "ServiceStatus", "SortOrder"]
