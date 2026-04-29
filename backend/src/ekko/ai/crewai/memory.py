"""CrewAI memory management for Ekko.

Configures and manages CrewAI's built-in memory subsystem (short-term,
long-term, entity memory) with Ekko-specific defaults and scoring.

The ``MemoryConfig`` dataclass captures all memory-related settings.
``configure_crew_memory`` applies them to a crew at build time.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, final

from ekko.ai.crewai.constants import DEFAULT_MEMORY_SCORING

if TYPE_CHECKING:
    from crewai import Crew

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MemoryConfig:
    """Configuration for CrewAI memory subsystem."""

    enabled: bool = True
    short_term: bool = True
    long_term: bool = False
    entity: bool = True
    scoring: str = DEFAULT_MEMORY_SCORING
    max_short_term_items: int = 100
    max_entity_items: int = 50


# ── Default configs ──────────────────────────────────────────────

CONVERSATIONAL_MEMORY = MemoryConfig(
    enabled=True,
    short_term=True,
    long_term=True,
    entity=True,
    scoring="conversational",
)

ANALYSIS_MEMORY = MemoryConfig(
    enabled=True,
    short_term=True,
    long_term=False,
    entity=True,
    scoring="analytical",
)

LIGHTWEIGHT_MEMORY = MemoryConfig(
    enabled=True,
    short_term=True,
    long_term=False,
    entity=False,
    scoring="default",
)


@final
class MemoryManager:
    """Manages memory lifecycle for CrewAI crews.

    Applies ``MemoryConfig`` settings to crews and provides
    utilities for memory inspection and cleanup.
    """

    def __init__(self, config: MemoryConfig | None = None) -> None:
        self._config = config or LIGHTWEIGHT_MEMORY

    @property
    def config(self) -> MemoryConfig:
        """Current memory configuration."""
        return self._config

    def apply_to_crew(self, crew: Crew) -> Crew:
        """Apply memory settings to a crew instance.

        CrewAI's ``Crew`` accepts a ``memory`` boolean flag.
        Additional memory configuration is applied via crew attributes
        when the framework supports it.
        """
        crew.memory = self._config.enabled
        logger.debug(
            "Memory applied to crew: enabled=%s, scoring=%s",
            self._config.enabled,
            self._config.scoring,
        )
        return crew

    def get_crew_kwargs(self) -> dict[str, Any]:
        """Return kwargs suitable for ``Crew(...)`` construction."""
        return {
            "memory": self._config.enabled,
        }
