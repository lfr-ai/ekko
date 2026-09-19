"""Core readiness contracts for external dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, kw_only=True, slots=True)
class DependencyStatus:
    """Readiness status for one external dependency."""

    name: str
    healthy: bool
    detail: str = ""


@runtime_checkable
class ReadinessProbe(Protocol):
    """Port for checking one external dependency."""

    async def check(self) -> DependencyStatus:
        """Report the current dependency readiness status."""
        ...
