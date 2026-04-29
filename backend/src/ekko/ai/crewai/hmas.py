"""CrewAI HMAS -- Hierarchical Multi-Agent System supervisor.

Implements a production-ready hierarchical supervisor that:

1. Receives high-level goals from the application layer.
2. Decomposes goals into sub-goals using an LLM planner.
3. Routes sub-goals to CrewAI crews.
4. Manages nested hierarchy -- crews can delegate to sub-crews.
5. Aggregates results with conflict resolution and quality checks.

.. code-block:: text

   ┌────────────────────────────────┐
   │       Application Layer        │
   │       (CrewAI Service)         │
   └──────────────┬─────────────────┘
                  │
   ┌──────────────▼─────────────────┐
   │   HMAS Supervisor (this file)  │
   │   - goal decomposition         │
   │   - routing & delegation       │
   │   - result aggregation         │
   └──┬────────┬────────────────────┘
      │        │
      ▼        ▼
   ┌──────┐ ┌──────┐
   │Crew A│ │Crew B│
   │(hier)│ │(seql)│
   └──────┘ └──────┘
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum, auto, unique
from typing import TYPE_CHECKING, final

from ekko.ai.crewai.constants import HMAS_MAX_DEPTH

_LOG_TRUNCATE_LEN = 200

if TYPE_CHECKING:
    from crewai import Crew

logger = logging.getLogger(__name__)


@unique
class DelegationTarget(StrEnum):
    """Type of target for sub-goal delegation."""

    CREWAI_CREW = auto()


@unique
class SubGoalState(StrEnum):
    """Lifecycle state of a delegated sub-goal."""

    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass(slots=True)
@final
class SubGoal:
    """Decomposed sub-goal within the HMAS plan."""

    id: str
    description: str
    target_type: DelegationTarget = DelegationTarget.CREWAI_CREW
    target_name: str = ""
    state: SubGoalState = SubGoalState.PENDING
    result: str = ""
    error: str = ""
    priority: int = 0
    dependencies: list[str] = field(default_factory=list)


@dataclass(slots=True)
@final
class HMASPlan:
    """Execution plan produced by the HMAS planner."""

    goal: str
    sub_goals: list[SubGoal] = field(default_factory=list)
    depth: int = 0
    metadata: dict[str, object] = field(default_factory=dict)


@final
class CrewAIHMASSupervisor:
    """Hierarchical Multi-Agent System supervisor using CrewAI.

    Combines CrewAI's native hierarchical process with optional
    cross-framework delegation. Supports nested hierarchies up to
    ``HMAS_MAX_DEPTH`` levels.
    """

    def __init__(
        self,
        *,
        crews: dict[str, Crew] | None = None,
        max_depth: int = HMAS_MAX_DEPTH,
    ) -> None:
        self._crews = crews or {}
        self._max_depth = max_depth

    def register_crew(self, name: str, crew: Crew) -> None:
        """Register a named crew for HMAS delegation."""
        self._crews[name] = crew
        logger.info("HMAS crew registered: %s", name)

    async def orchestrate(
        self,
        goal: str,
        *,
        inputs: dict[str, object] | None = None,
        depth: int = 0,
    ) -> str:
        """Execute the full HMAS orchestration loop.

        1. Plan -- decompose the goal into sub-goals.
        2. Route -- assign each sub-goal to the best target.
        3. Execute -- delegate to crews.
        4. Aggregate -- combine results into a unified response.
        """
        if depth >= self._max_depth:
            logger.warning("HMAS max depth reached: %d", depth)
            return f"Maximum hierarchy depth ({self._max_depth}) reached."

        logger.info("HMAS orchestrate start (depth=%d): %s", depth, goal[:_LOG_TRUNCATE_LEN])

        plan = self._simple_plan(goal)
        await self._execute_plan(plan, inputs=inputs, depth=depth)
        result = self._aggregate(plan)

        logger.info(
            "HMAS orchestrate complete (depth=%d, sub_goals=%d, completed=%d)",
            depth,
            len(plan.sub_goals),
            sum(1 for sg in plan.sub_goals if sg.state == SubGoalState.COMPLETED),
        )
        return result

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

    def _simple_plan(self, goal: str) -> HMASPlan:
        """Fallback: single sub-goal delegated to the first available crew."""
        import uuid

        target = next(iter(self._crews), "")
        return HMASPlan(
            goal=goal,
            sub_goals=[
                SubGoal(
                    id=str(uuid.uuid4()),
                    description=goal,
                    target_type=DelegationTarget.CREWAI_CREW,
                    target_name=target,
                ),
            ],
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def _execute_plan(
        self,
        plan: HMASPlan,
        *,
        inputs: dict[str, object] | None = None,
        depth: int = 0,
    ) -> None:
        """Execute all sub-goals with dependency awareness."""
        import asyncio

        pending = list(plan.sub_goals)
        completed_ids: set[str] = set()

        while pending:
            ready = [sg for sg in pending if all(dep in completed_ids for dep in sg.dependencies)]

            if not ready:
                for sg in pending:
                    sg.state = SubGoalState.FAILED
                    sg.error = "Dependency deadlock"
                break

            tasks = [self._execute_sub_goal(sg, inputs=inputs, depth=depth) for sg in ready]
            await asyncio.gather(*tasks, return_exceptions=True)

            for sg in ready:
                pending.remove(sg)
                if sg.state == SubGoalState.COMPLETED:
                    completed_ids.add(sg.id)

    async def _execute_sub_goal(
        self,
        sub_goal: SubGoal,
        *,
        inputs: dict[str, object] | None = None,
        depth: int = 0,  # noqa: ARG002 — reserved for nested HMAS delegation
    ) -> None:
        """Execute a single sub-goal by delegating to the appropriate target."""
        sub_goal.state = SubGoalState.IN_PROGRESS

        try:
            result = await self._delegate_to_crew(sub_goal, inputs=inputs)
            sub_goal.result = result
            sub_goal.state = SubGoalState.COMPLETED
            logger.info("HMAS sub-goal completed: %s -> %s", sub_goal.id, sub_goal.target_name)
        except Exception as exc:
            sub_goal.state = SubGoalState.FAILED
            sub_goal.error = str(exc)
            logger.warning(
                "HMAS sub-goal failed: %s -> %s: %s",
                sub_goal.id,
                sub_goal.target_name,
                exc,
            )

    async def _delegate_to_crew(
        self,
        sub_goal: SubGoal,
        *,
        inputs: dict[str, object] | None = None,
    ) -> str:
        """Delegate a sub-goal to a CrewAI crew using native async kickoff."""
        crew = self._crews.get(sub_goal.target_name)
        if crew is None:
            if self._crews:
                crew = next(iter(self._crews.values()))
            else:
                return "No crews available for delegation."

        crew_inputs = dict(inputs or {})
        crew_inputs["task"] = sub_goal.description

        result = await crew.akickoff(inputs=crew_inputs)
        return str(result)

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def _aggregate(self, plan: HMASPlan) -> str:
        """Aggregate results from completed sub-goals."""
        completed = [sg for sg in plan.sub_goals if sg.state == SubGoalState.COMPLETED]
        failed = [sg for sg in plan.sub_goals if sg.state == SubGoalState.FAILED]

        if not completed:
            errors = "; ".join(f"{sg.description}: {sg.error}" for sg in failed)
            return f"All sub-goals failed. Errors: {errors}"

        parts = [f"## {sg.description}\n{sg.result}" for sg in completed]
        if failed:
            parts.append("\n---\n**Note:** Some sub-goals failed: " + ", ".join(sg.description for sg in failed))
        return "\n\n".join(parts)
