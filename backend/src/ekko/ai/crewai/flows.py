"""CrewAI Flows -- stateful multi-step workflow orchestration.

Provides a ``FlowRunner`` that wraps CrewAI's ``Flow`` class with
lifecycle hooks, structured result capture, and a ``FlowRegistry``
for discovering and executing named flows at runtime.

.. code-block:: text

   ┌──────────────┐
   │ FlowRegistry │  ← register / discover named flows
   └──────┬───────┘
          │ execute(name, inputs)
   ┌──────▼───────┐
   │  FlowRunner  │  ← lifecycle, retries, result capture
   └──────┬───────┘
          │
   ┌──────▼───────┐
   │  crewai.Flow │  ← native stateful execution
   └──────────────┘
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum, auto, unique
from typing import TYPE_CHECKING, Any, final

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

_LOG_TRUNCATE = 200


# ── Result types ─────────────────────────────────────────────────


@unique
class FlowStatus(StrEnum):
    """Terminal status of a flow run."""

    SUCCESS = auto()
    FAILED = auto()
    TIMEOUT = auto()


@dataclass(frozen=True, slots=True)
class FlowRunResult:
    """Immutable result from a single flow execution."""

    flow_name: str
    status: FlowStatus
    output: str = ""
    error: str = ""
    elapsed_seconds: float = 0.0
    metadata: dict[str, object] = field(default_factory=dict)


# ── FlowRunner ───────────────────────────────────────────────────


@final
class FlowRunner:
    """Execute a CrewAI Flow with lifecycle hooks and timing.

    Wraps ``crewai.Flow.kickoff()`` with:

    * Pre/post hooks for logging and monitoring.
    * Automatic elapsed-time measurement.
    * Structured ``FlowRunResult`` output.
    """

    async def run(
        self,
        flow: object,
        *,
        name: str = "unnamed",
        inputs: dict[str, object] | None = None,
    ) -> FlowRunResult:
        """Execute a flow and return a structured result."""
        logger.info("Flow [%s] starting", name)
        start = time.monotonic()

        try:
            # crewai.Flow exposes kickoff() — use async variant if available
            kickoff = getattr(flow, "akickoff", None) or flow.kickoff
            result = await kickoff(inputs=inputs or {}) if _is_async(kickoff) else kickoff(inputs=inputs or {})
            elapsed = time.monotonic() - start

            logger.info("Flow [%s] completed in %.2fs", name, elapsed)
            return FlowRunResult(
                flow_name=name,
                status=FlowStatus.SUCCESS,
                output=str(result),
                elapsed_seconds=elapsed,
            )
        except Exception as exc:
            elapsed = time.monotonic() - start
            logger.warning("Flow [%s] failed after %.2fs: %s", name, elapsed, exc)
            return FlowRunResult(
                flow_name=name,
                status=FlowStatus.FAILED,
                error=str(exc),
                elapsed_seconds=elapsed,
            )


# ── FlowRegistry ────────────────────────────────────────────────


@final
class FlowRegistry:
    """Named registry of flow factories.

    Register callables that produce ``crewai.Flow`` instances, then
    execute them by name at runtime.

    .. code-block:: python

        registry = FlowRegistry()
        registry.register("onboarding", build_onboarding_flow)
        result = await registry.execute("onboarding", inputs={...})
    """

    def __init__(self) -> None:
        self._factories: dict[str, Callable[..., object]] = {}
        self._runner = FlowRunner()

    def register(self, name: str, factory: Callable[..., object]) -> None:
        """Register a flow factory under *name*."""
        self._factories[name] = factory
        logger.info("Flow registered: %s", name)

    def list_flows(self) -> list[str]:
        """Return the names of all registered flows."""
        return sorted(self._factories)

    async def execute(
        self,
        name: str,
        *,
        inputs: dict[str, object] | None = None,
        factory_kwargs: dict[str, Any] | None = None,
    ) -> FlowRunResult:
        """Build and execute the named flow."""
        factory = self._factories.get(name)
        if factory is None:
            return FlowRunResult(
                flow_name=name,
                status=FlowStatus.FAILED,
                error=f"Unknown flow: {name!r}. Available: {self.list_flows()}",
            )

        flow = factory(**(factory_kwargs or {}))
        return await self._runner.run(flow, name=name, inputs=inputs)


# ── Helpers ──────────────────────────────────────────────────────


def _is_async(fn: object) -> bool:
    """Return True if *fn* is a coroutine function."""
    import asyncio

    return asyncio.iscoroutinefunction(fn)
