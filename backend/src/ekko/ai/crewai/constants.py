"""CrewAI configuration constants."""

from __future__ import annotations

from typing import Final

from ekko.config.enums import ChatModel

# ── HMAS settings ────────────────────────────────────────────────
HMAS_MAX_DEPTH: Final[int] = 3

# ── Crew defaults ────────────────────────────────────────────────
DEFAULT_CREW_VERBOSE: Final[bool] = False
DEFAULT_CREW_MAX_RPM: Final[int] = 10
DEFAULT_MANAGER_MODEL: Final[str] = ChatModel.GPT_4O
DEFAULT_AGENT_MODEL: Final[str] = ChatModel.GPT_4O

# ── Memory scoring ───────────────────────────────────────────────
DEFAULT_MEMORY_SCORING: Final[str] = "default"
