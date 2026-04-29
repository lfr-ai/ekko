"""YAML configuration loader for CrewAI agents and tasks.

Centralises YAML loading, validation, and variable substitution
for agent/task definitions. All other modules should use this
loader instead of reading YAML directly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, final

logger = logging.getLogger(__name__)

_CONFIG_DIR = Path(__file__).parent / "config"


@dataclass(frozen=True, slots=True)
class AgentConfig:
    """Validated agent configuration from YAML."""

    role: str
    goal: str
    backstory: str
    verbose: bool = False
    allow_delegation: bool = False
    max_iter: int = 10
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TaskConfig:
    """Validated task configuration from YAML."""

    description: str
    expected_output: str
    agent_key: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@final
class YAMLConfigLoader:
    """Load and validate YAML config for CrewAI agents and tasks.

    Usage::

        loader = YAMLConfigLoader()
        agents = loader.load_agents()
        tasks = loader.load_tasks()
        agent_cfg = agents["intent_detector"]
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        self._config_dir = config_dir or _CONFIG_DIR

    def load_agents(self) -> dict[str, AgentConfig]:
        """Load and validate all agent configurations."""
        raw = self._load_yaml("agents.yaml")
        agents = {}
        for key, cfg in raw.items():
            agents[key] = AgentConfig(
                role=cfg["role"],
                goal=cfg["goal"],
                backstory=cfg["backstory"],
                verbose=cfg.get("verbose", False),
                allow_delegation=cfg.get("allow_delegation", False),
                max_iter=cfg.get("max_iter", 10),
                extra={k: v for k, v in cfg.items() if k not in _AGENT_KNOWN_KEYS},
            )
        logger.debug("Loaded %d agent configs from %s", len(agents), self._config_dir)
        return agents

    def load_tasks(self) -> dict[str, TaskConfig]:
        """Load and validate all task configurations."""
        raw = self._load_yaml("tasks.yaml")
        tasks = {}
        for key, cfg in raw.items():
            tasks[key] = TaskConfig(
                description=cfg["description"],
                expected_output=cfg["expected_output"],
                agent_key=cfg.get("agent", ""),
                extra={k: v for k, v in cfg.items() if k not in _TASK_KNOWN_KEYS},
            )
        logger.debug("Loaded %d task configs from %s", len(tasks), self._config_dir)
        return tasks

    def _load_yaml(self, filename: str) -> dict[str, Any]:
        """Load a YAML file from the config directory."""
        import yaml

        path = self._config_dir / filename
        if not path.exists():
            logger.warning("Config file not found: %s", path)
            return {}

        with path.open() as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}


_AGENT_KNOWN_KEYS = frozenset(
    {
        "role",
        "goal",
        "backstory",
        "verbose",
        "allow_delegation",
        "max_iter",
    }
)
_TASK_KNOWN_KEYS = frozenset(
    {
        "description",
        "expected_output",
        "agent",
    }
)
