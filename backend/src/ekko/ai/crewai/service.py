"""CrewAI service — application-layer orchestrator.

Golden-standard pattern: single service that unifies crew execution,
flow orchestration, and HMAS delegation behind a clean API.

All inputs are PII-scrubbed before reaching LLM agents.
"""

from __future__ import annotations

import logging
from typing import Any, final

from ekko.ai.crewai.constants import DEFAULT_CREW_VERBOSE
from ekko.ai.crewai.crew import EkkoCrew, timed_kickoff
from ekko.ai.crewai.flows import FlowRegistry, FlowRunResult
from ekko.ai.crewai.hmas import CrewAIHMASSupervisor
from ekko.ai.crewai.knowledge import KnowledgeProvider
from ekko.ai.crewai.memory import MemoryManager
from ekko.ai.crewai.templates import CrewSpec, CrewTemplateBuilder
from ekko.ai.pii.anonymizer import PIIAnonymizer

logger = logging.getLogger(__name__)


@final
class CrewAIService:
    """Application service for all CrewAI interactions.

    Provides three execution modes:

    1. **Direct crew execution** — call a named crew method on ``EkkoCrew``.
    2. **Template-based execution** — build a crew from a ``CrewSpec``.
    3. **Flow execution** — run a registered flow via ``FlowRegistry``.
    4. **HMAS orchestration** — delegate to the hierarchical supervisor.

    All text inputs pass through PII anonymization before reaching agents.
    """

    def __init__(
        self,
        *,
        crew: EkkoCrew | None = None,
        anonymizer: PIIAnonymizer | None = None,
        hmas: CrewAIHMASSupervisor | None = None,
        flow_registry: FlowRegistry | None = None,
        template_builder: CrewTemplateBuilder | None = None,
        knowledge_provider: KnowledgeProvider | None = None,
        memory_manager: MemoryManager | None = None,
        verbose: bool = DEFAULT_CREW_VERBOSE,
    ) -> None:
        self._crew = crew or EkkoCrew(verbose=verbose)
        self._anonymizer = anonymizer or PIIAnonymizer()
        self._hmas = hmas or CrewAIHMASSupervisor()
        self._flow_registry = flow_registry or FlowRegistry()
        self._template_builder = template_builder or CrewTemplateBuilder()
        self._knowledge = knowledge_provider or KnowledgeProvider()
        self._memory = memory_manager or MemoryManager()
        self._verbose = verbose

    # ── PII ──────────────────────────────────────────────────────

    def _scrub(self, text: str) -> str:
        """Anonymize PII before sending to agent."""
        result = self._anonymizer.anonymize(text)
        if result.has_pii:
            logger.info("Scrubbed %d PII items before agent call", len(result.pii_matches))
        return result.anonymized_text

    # ── Direct crew execution ────────────────────────────────────

    def detect_intent(self, transcript: str) -> Any:
        """Detect user intent from a transcript (PII-scrubbed)."""
        crew = self._crew.intent_detection_crew(self._scrub(transcript))
        result, elapsed = timed_kickoff(crew)
        logger.info("Intent detection completed in %.2fs", elapsed)
        return result

    def summarize_conversation(self, transcript: str) -> Any:
        """Summarize a conversation transcript (PII-scrubbed)."""
        crew = self._crew.summarization_crew(self._scrub(transcript))
        result, elapsed = timed_kickoff(crew)
        logger.info("Summarization completed in %.2fs", elapsed)
        return result

    def respond_to_query(self, query: str) -> Any:
        """Generate a voice response (PII-scrubbed)."""
        crew = self._crew.voice_response_crew(self._scrub(query))
        result, elapsed = timed_kickoff(crew)
        logger.info("Voice response completed in %.2fs", elapsed)
        return result

    def analyze_transcript(self, transcript: str) -> Any:
        """Analyze a transcript for quality metrics (PII-scrubbed)."""
        crew = self._crew.transcript_analysis_crew(self._scrub(transcript))
        result, elapsed = timed_kickoff(crew)
        logger.info("Transcript analysis completed in %.2fs", elapsed)
        return result

    # ── Template-based execution ─────────────────────────────────

    def execute_from_spec(self, spec: CrewSpec) -> Any:
        """Build and execute a crew from a declarative spec.

        Inputs in the spec are PII-scrubbed before crew construction.
        """
        scrubbed_inputs = {k: self._scrub(v) for k, v in spec.inputs.items()}
        clean_spec = CrewSpec(
            name=spec.name,
            crew_type=spec.crew_type,
            inputs=scrubbed_inputs,
            process=spec.process,
            verbose=spec.verbose,
            max_rpm=spec.max_rpm,
            model=spec.model,
            tools=spec.tools,
            metadata=spec.metadata,
        )
        crew = self._template_builder.build(clean_spec)
        memory_kwargs = self._memory.get_crew_kwargs()
        crew.memory = memory_kwargs.get("memory", True)
        result, elapsed = timed_kickoff(crew)
        logger.info("Spec crew [%s] completed in %.2fs", spec.name, elapsed)
        return result

    def list_crew_templates(self) -> list[str]:
        """Return available crew template types."""
        return self._template_builder.available_types()

    # ── Flow execution ───────────────────────────────────────────

    async def execute_flow(
        self,
        flow_name: str,
        *,
        inputs: dict[str, object] | None = None,
    ) -> FlowRunResult:
        """Execute a registered flow by name."""
        scrubbed = {}
        if inputs:
            scrubbed = {k: self._scrub(str(v)) if isinstance(v, str) else v for k, v in inputs.items()}
        return await self._flow_registry.execute(flow_name, inputs=scrubbed)

    def register_flow(self, name: str, factory: Any) -> None:
        """Register a flow factory for later execution."""
        self._flow_registry.register(name, factory)

    def list_flows(self) -> list[str]:
        """Return names of all registered flows."""
        return self._flow_registry.list_flows()

    # ── HMAS orchestration ───────────────────────────────────────

    async def orchestrate(
        self,
        goal: str,
        *,
        inputs: dict[str, object] | None = None,
    ) -> str:
        """Delegate a high-level goal to the HMAS supervisor.

        The goal text is PII-scrubbed. The supervisor decomposes it,
        routes sub-goals to registered crews, and aggregates results.
        """
        scrubbed_goal = self._scrub(goal)

        # Enrich inputs with knowledge context if available
        enriched_inputs = dict(inputs or {})
        context = self._knowledge.as_context_string(scrubbed_goal)
        if context:
            enriched_inputs["knowledge_context"] = context

        return await self._hmas.orchestrate(scrubbed_goal, inputs=enriched_inputs)

    def register_crew_for_hmas(self, name: str, crew: Any) -> None:
        """Register a crew with the HMAS supervisor for delegation."""
        self._hmas.register_crew(name, crew)

    # ── Knowledge management ─────────────────────────────────────

    @property
    def knowledge(self) -> KnowledgeProvider:
        """Access the knowledge provider for indexing/search."""
        return self._knowledge


# Keep backward-compatible alias
AgentService = CrewAIService
