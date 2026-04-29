"""Main CrewAI crew definition for Ekko.

Follows koda's pattern: YAML-based agent/task config, structured output,
async execution via akickoff().
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, final

from crewai import Agent, Crew, Process, Task

logger = logging.getLogger(__name__)

_CONFIG_DIR = Path(__file__).parent / "config"


def _load_yaml(filename: str) -> dict[str, Any]:
    """Load a YAML config file."""
    import yaml

    with (_CONFIG_DIR / filename).open() as f:
        return yaml.safe_load(f)


@final
class EkkoCrew:
    """CrewAI crew for Ekko's multi-agent voice conversation workflows.

    Agents and tasks are defined in YAML config files under ``config/``.
    """

    def __init__(self, *, tools: list[object] | None = None, verbose: bool = False) -> None:
        self._agents_config = _load_yaml("agents.yaml")
        self._tasks_config = _load_yaml("tasks.yaml")
        self._tools = tools or []
        self._verbose = verbose

    def _build_agent(self, agent_key: str, *, tools: list[object] | None = None) -> Agent:
        """Create an Agent from YAML config."""
        cfg = self._agents_config[agent_key]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            verbose=self._verbose,
            tools=tools or self._tools,
            max_iter=10,
            memory=True,
        )

    def _build_task(
        self,
        task_key: str,
        agent: Agent,
        *,
        context_vars: dict[str, str] | None = None,
        output_type: type | None = None,
    ) -> Task:
        """Create a Task from YAML config with variable substitution."""
        cfg = self._tasks_config[task_key]
        description = cfg["description"]
        if context_vars:
            description = description.format(**context_vars)

        kwargs: dict[str, Any] = {
            "description": description,
            "expected_output": cfg["expected_output"],
            "agent": agent,
        }
        if output_type is not None:
            kwargs["output_pydantic"] = output_type

        return Task(**kwargs)

    # ── Pre-built crews ──────────────────────────────────────────

    def intent_detection_crew(self, transcript: str) -> Crew:
        """Build a crew for detecting user intent from a transcript."""
        from ekko.ai.crewai.models import IntentDetectionOutput

        agent = self._build_agent("intent_detector")
        task = self._build_task(
            "detect_intent",
            agent,
            context_vars={"transcript": transcript},
            output_type=IntentDetectionOutput,
        )
        return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=self._verbose)

    def conversation_routing_crew(self, intent: str, confidence: float) -> Crew:
        """Build a crew for routing conversation based on intent."""
        from ekko.ai.crewai.models import ConversationRouteOutput

        agent = self._build_agent("conversation_router")
        task = self._build_task(
            "route_conversation",
            agent,
            context_vars={"intent": intent, "confidence": str(confidence)},
            output_type=ConversationRouteOutput,
        )
        return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=self._verbose)

    def summarization_crew(self, transcript: str) -> Crew:
        """Build a crew for summarizing a conversation."""
        from ekko.ai.crewai.models import ConversationSummaryOutput

        agent = self._build_agent("summarizer")
        task = self._build_task(
            "summarize_conversation",
            agent,
            context_vars={"transcript": transcript},
            output_type=ConversationSummaryOutput,
        )
        return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=self._verbose)

    def voice_response_crew(self, query: str) -> Crew:
        """Build a crew for handling a voice query."""
        agent = self._build_agent("voice_assistant")
        task = self._build_task("respond_to_query", agent, context_vars={"query": query})
        return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=self._verbose)

    def transcript_analysis_crew(self, transcript: str) -> Crew:
        """Build a crew for analyzing a conversation transcript."""
        from ekko.ai.crewai.models import TranscriptAnalysisOutput

        agent = self._build_agent("transcript_analyzer")
        task = self._build_task(
            "analyze_transcript",
            agent,
            context_vars={"transcript": transcript},
            output_type=TranscriptAnalysisOutput,
        )
        return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=self._verbose)

    # ── Multi-agent pipeline ─────────────────────────────────────

    def full_conversation_pipeline(self, transcript: str) -> Crew:
        """Build a multi-agent crew: detect intent → route → respond."""
        intent_agent = self._build_agent("intent_detector")
        router_agent = self._build_agent("conversation_router")
        assistant_agent = self._build_agent("voice_assistant")

        detect_task = self._build_task("detect_intent", intent_agent, context_vars={"transcript": transcript})
        route_task = self._build_task(
            "route_conversation",
            router_agent,
            context_vars={"intent": "{detect_intent_output}", "confidence": "0.0"},
        )
        respond_task = self._build_task("respond_to_query", assistant_agent, context_vars={"query": transcript})

        return Crew(
            agents=[intent_agent, router_agent, assistant_agent],
            tasks=[detect_task, route_task, respond_task],
            process=Process.sequential,
            verbose=self._verbose,
        )


def timed_kickoff(crew: Crew, **kwargs: Any) -> tuple[Any, float]:
    """Execute a crew synchronously and return (result, elapsed_seconds)."""
    start = time.monotonic()
    result = crew.kickoff(**kwargs)
    elapsed = time.monotonic() - start
    logger.info("Crew finished in %.2fs", elapsed)
    return result, elapsed
