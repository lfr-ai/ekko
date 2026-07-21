"""CrewAI multi-agent orchestration.

Public API::

    from ekko.ai.crewai import (
        # Core crew
        EkkoCrew,
        timed_kickoff,
        # HMAS supervisor
        CrewAIHMASSupervisor,
        HMASPlan,
        SubGoal,
        SubGoalState,
        DelegationTarget,
        # Flows
        FlowRunner,
        FlowRegistry,
        FlowRunResult,
        FlowStatus,
        # Templates
        CrewSpec,
        CrewTemplateBuilder,
        build_intent_pipeline,
        build_analysis_crew,
        build_summarization_crew,
        # Knowledge
        KnowledgeProvider,
        KnowledgeChunk,
        # Memory
        MemoryManager,
        MemoryConfig,
        # Config
        YAMLConfigLoader,
        AgentConfig,
        TaskConfig,
        # Models
        IntentDetectionOutput,
        ConversationRouteOutput,
        ConversationSummaryOutput,
        TranscriptAnalysisOutput,
        VoiceResponse,
        # Service
        CrewAIService,
    )
"""

from ekko.ai.crewai.crew import EkkoCrew, timed_kickoff
from ekko.ai.crewai.flows import FlowRegistry, FlowRunner, FlowRunResult, FlowStatus
from ekko.ai.crewai.hmas import (
    CrewAIHMASSupervisor,
    DelegationTarget,
    HMASPlan,
    SubGoal,
    SubGoalState,
)
from ekko.ai.crewai.knowledge import KnowledgeChunk, KnowledgeProvider
from ekko.ai.crewai.memory import MemoryConfig, MemoryManager
from ekko.ai.crewai.models import (
    ConversationRouteOutput,
    ConversationSummaryOutput,
    IntentDetectionOutput,
    TranscriptAnalysisOutput,
    VoiceResponse,
)
from ekko.ai.crewai.service import CrewAIService
from ekko.ai.crewai.templates import (
    CrewSpec,
    CrewTemplateBuilder,
    build_analysis_crew,
    build_intent_pipeline,
    build_summarization_crew,
)
from ekko.ai.crewai.yaml_config import AgentConfig, TaskConfig, YAMLConfigLoader

__all__ = [
    "AgentConfig",
    "ConversationRouteOutput",
    "ConversationSummaryOutput",
    "CrewAIHMASSupervisor",
    "CrewAIService",
    "CrewSpec",
    "CrewTemplateBuilder",
    "DelegationTarget",
    "EkkoCrew",
    "FlowRegistry",
    "FlowRunResult",
    "FlowRunner",
    "FlowStatus",
    "HMASPlan",
    "IntentDetectionOutput",
    "KnowledgeChunk",
    "KnowledgeProvider",
    "MemoryConfig",
    "MemoryManager",
    "SubGoal",
    "SubGoalState",
    "TaskConfig",
    "TranscriptAnalysisOutput",
    "VoiceResponse",
    "YAMLConfigLoader",
    "build_analysis_crew",
    "build_intent_pipeline",
    "build_summarization_crew",
    "timed_kickoff",
]
