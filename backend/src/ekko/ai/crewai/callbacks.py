"""CrewAI callbacks for logging and monitoring agent execution."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def on_task_start(task_name: str) -> None:
    """Called when a CrewAI task begins execution."""
    logger.info("Task started: %s", task_name)


def on_task_complete(task_name: str, output: str) -> None:
    """Called when a CrewAI task completes."""
    logger.info("Task completed: %s (output length: %d)", task_name, len(output))


def on_agent_action(agent_role: str, action: str) -> None:
    """Called when an agent takes an action."""
    logger.debug("Agent [%s] action: %s", agent_role, action[:200])


def on_crew_error(crew_name: str, error: Exception) -> None:
    """Called when a crew encounters an error."""
    logger.error("Crew [%s] error: %s", crew_name, error)
