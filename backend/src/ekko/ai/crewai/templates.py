"""Pre-built crew templates for common Ekko workflows.

Each template is a factory function that returns a configured ``Crew``
ready to be kicked off. Templates use the YAML agent/task config and
Pydantic output models from this package.

Usage::

    from ekko.ai.crewai.templates import build_intent_pipeline
    crew = build_intent_pipeline(transcript="Hello, I need help...")
    result = await crew.akickoff()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, final

from crewai import Crew, Process

from ekko.ai.crewai.constants import (
    DEFAULT_AGENT_MODEL,
    DEFAULT_CREW_MAX_RPM,
    DEFAULT_CREW_VERBOSE,
)
from ekko.ai.crewai.crew import EkkoCrew

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CrewSpec:
    """Declarative specification for building a crew at runtime.

    Instead of hard-coding crew construction, callers describe
    *what* they want and ``build_crew_from_spec`` assembles it.
    """

    name: str
    crew_type: str  # e.g. "intent_detection", "summarization", "pipeline"
    inputs: dict[str, str] = field(default_factory=dict)
    process: Process = Process.sequential
    verbose: bool = DEFAULT_CREW_VERBOSE
    max_rpm: int = DEFAULT_CREW_MAX_RPM
    model: str = DEFAULT_AGENT_MODEL
    tools: list[object] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ── Template catalogue ───────────────────────────────────────────

_CREW_TYPE_MAP: dict[str, str] = {
    "intent_detection": "intent_detection_crew",
    "conversation_routing": "conversation_routing_crew",
    "summarization": "summarization_crew",
    "voice_response": "voice_response_crew",
    "transcript_analysis": "transcript_analysis_crew",
    "full_pipeline": "full_conversation_pipeline",
}


@final
class CrewTemplateBuilder:
    """Builds crews from ``CrewSpec`` definitions.

    Maps spec ``crew_type`` names to the corresponding ``EkkoCrew``
    factory method, forwarding inputs as keyword arguments.
    """

    def __init__(self, *, tools: list[object] | None = None) -> None:
        self._tools = tools or []

    def build(self, spec: CrewSpec) -> Crew:
        """Build a ``Crew`` from a ``CrewSpec``."""
        method_name = _CREW_TYPE_MAP.get(spec.crew_type)
        if method_name is None:
            msg = f"Unknown crew type: {spec.crew_type!r}. Available: {sorted(_CREW_TYPE_MAP)}"
            raise ValueError(msg)

        ekko_crew = EkkoCrew(tools=spec.tools or self._tools, verbose=spec.verbose)
        builder = getattr(ekko_crew, method_name)

        # Map spec.inputs to the builder's expected positional args
        crew = _call_builder(builder, spec)
        logger.info("Built crew from spec: %s (%s)", spec.name, spec.crew_type)
        return crew

    def available_types(self) -> list[str]:
        """Return sorted list of supported crew type names."""
        return sorted(_CREW_TYPE_MAP)


# ── Convenience factories ────────────────────────────────────────


def build_intent_pipeline(transcript: str, *, verbose: bool = False) -> Crew:
    """Quick factory: intent detection → routing → response."""
    crew = EkkoCrew(verbose=verbose)
    return crew.full_conversation_pipeline(transcript)


def build_analysis_crew(transcript: str, *, verbose: bool = False) -> Crew:
    """Quick factory: transcript analysis crew."""
    crew = EkkoCrew(verbose=verbose)
    return crew.transcript_analysis_crew(transcript)


def build_summarization_crew(transcript: str, *, verbose: bool = False) -> Crew:
    """Quick factory: summarization crew."""
    crew = EkkoCrew(verbose=verbose)
    return crew.summarization_crew(transcript)


# ── Internal helpers ─────────────────────────────────────────────


def _call_builder(builder: Any, spec: CrewSpec) -> Crew:
    """Call a crew builder method with inputs from the spec."""
    import inspect

    sig = inspect.signature(builder)
    params = list(sig.parameters.keys())

    # Positional args — match spec.inputs to parameter names
    kwargs = {k: v for k, v in spec.inputs.items() if k in params}
    return builder(**kwargs)
