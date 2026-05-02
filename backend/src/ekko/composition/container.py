"""Dependency-injection container.

Follows the cached-property pattern from the golden standard: each service is
built once on first access and reused for the lifetime of the container.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, final

from ekko.config.settings import BaseAppConfig, get_settings

if TYPE_CHECKING:
    from ekko.ai.crewai.flows import FlowRegistry
    from ekko.ai.crewai.hmas import CrewAIHMASSupervisor
    from ekko.ai.crewai.knowledge import KnowledgeProvider
    from ekko.ai.crewai.memory import MemoryManager
    from ekko.ai.crewai.service import CrewAIService
    from ekko.ai.pii.anonymizer import PIIAnonymizer
    from ekko.application.services.summarizer_service import SummarizerService
    from ekko.core.interfaces import (
        AudioStreamerControllerProtocol,
        OpenAIGateway,
        STTService,
    )


# Note: slots=True omitted — cached_property requires __dict__
@final
@dataclass
class Container:
    """Application-scoped DI container.

    Usage::

        container = Container.from_config()
        stt = container.stt_service
    """

    settings: BaseAppConfig

    @classmethod
    def from_config(cls) -> Container:
        """Build a container from the current environment settings."""
        return cls(settings=get_settings())

    # ── OpenAI ───────────────────────────────────────────────
    @cached_property
    def openai_gateway(self) -> OpenAIGateway:
        """Lazily build the OpenAI gateway."""
        from ekko.infrastructure.openai.openai_client import AzureOpenAIClient

        return AzureOpenAIClient(settings=self.settings)

    # ── STT ──────────────────────────────────────────────────
    @cached_property
    def stt_service(self) -> STTService:
        """Lazily build the STT service."""
        from ekko.infrastructure.adapters.stt_adapter import (
            create_faster_whisper_stt,
        )

        return create_faster_whisper_stt(settings=self.settings)

    # ── Audio ────────────────────────────────────────────────
    @cached_property
    def audio_controller(self) -> AudioStreamerControllerProtocol:
        """Lazily build the audio streamer controller."""
        from ekko.infrastructure.adapters.audio_streamer_adapter import (
            create_audio_streamer_controller,
        )

        return create_audio_streamer_controller(self.settings)

    # ── PII ──────────────────────────────────────────────────
    @cached_property
    def pii_anonymizer(self) -> PIIAnonymizer:
        """Lazily build the PII anonymizer."""
        from ekko.ai.pii.anonymizer import PIIAnonymizer as _PIIAnonymizer

        return _PIIAnonymizer()

    # ── CrewAI / HMAS ───────────────────────────────────────
    @cached_property
    def knowledge_provider(self) -> KnowledgeProvider:
        """Lazily build the knowledge provider."""
        from ekko.ai.crewai.knowledge import KnowledgeProvider as _KnowledgeProvider

        return _KnowledgeProvider()

    @cached_property
    def memory_manager(self) -> MemoryManager:
        """Lazily build the memory manager."""
        from ekko.ai.crewai.memory import MemoryManager as _MemoryManager

        return _MemoryManager()

    @cached_property
    def flow_registry(self) -> FlowRegistry:
        """Lazily build the flow registry."""
        from ekko.ai.crewai.flows import FlowRegistry as _FlowRegistry

        return _FlowRegistry()

    @cached_property
    def hmas_supervisor(self) -> CrewAIHMASSupervisor:
        """Lazily build the HMAS supervisor."""
        from ekko.ai.crewai.hmas import CrewAIHMASSupervisor as _CrewAIHMASSupervisor

        return _CrewAIHMASSupervisor()

    @cached_property
    def crewai_service(self) -> CrewAIService:
        """Lazily build the CrewAI service with all subsystems wired."""
        from ekko.ai.crewai.service import CrewAIService as _CrewAIService

        return _CrewAIService(
            anonymizer=self.pii_anonymizer,
            hmas=self.hmas_supervisor,
            flow_registry=self.flow_registry,
            knowledge_provider=self.knowledge_provider,
            memory_manager=self.memory_manager,
        )

    # ── Application services ─────────────────────────────────
    @cached_property
    def summarizer_service(self) -> SummarizerService:
        """Lazily build the summarizer service."""
        from ekko.application.services.summarizer_service import SummarizerService as _SummarizerService

        return _SummarizerService(
            gateway=self.openai_gateway,
            settings=self.settings,
        )
