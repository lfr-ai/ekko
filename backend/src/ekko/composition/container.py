"""Dependency-injection container.

Each service is built once on first access and reused for the lifetime of the
container.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, final

import litellm

from ekko.config.runtime import get_config

if TYPE_CHECKING:
    from collections.abc import Callable

    from redis.asyncio import Redis

    from ekko.application.services.pii_service import PIIService
    from ekko.application.services.prompt_catalog_service import PromptCatalogService
    from ekko.application.services.readiness_service import ReadinessService
    from ekko.application.services.summarizer_service import SummarizerService
    from ekko.application.services.transcript_broadcaster import TranscriptBroadcaster
    from ekko.config.base import BaseAppConfig
    from ekko.core.ports import (
        AudioStreamerControllerPort,
        ChatPort,
        PIIAnonymizerPort,
        PromptRegistryPort,
        STTPort,
    )
    from ekko.core.ports.external.metrics import MetricsPort
    from ekko.core.value_objects import TranscriptSegment
    from ekko.infrastructure.clients.llm_router import LLMRouter


# Note: slots=True omitted — cached_property requires __dict__
@final
@dataclass(frozen=True, kw_only=True)
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
        litellm.suppress_debug_info = True
        return cls(settings=get_config())

    # ── Chat / LLM ────────────────────────────────────────────
    @cached_property
    def llm_router(self) -> LLMRouter | None:
        """Lazily build the LLM Router if fallback deployments are configured."""
        if not self.settings.llm_fallback_deployments:
            return None

        from ekko.infrastructure.clients.llm_router import LLMRouter

        return LLMRouter.from_config(self.settings)

    @cached_property
    def metrics_port(self) -> MetricsPort:
        """Lazily build the metrics adapter."""
        from ekko.infrastructure.prometheus_metrics_adapter import (
            PrometheusMetricsAdapter,
        )

        return PrometheusMetricsAdapter()

    @cached_property
    def chat_client(self) -> ChatPort:
        """Lazily build the chat client with Router and MetricsPort wired."""
        from ekko.infrastructure.clients.chat import ChatClient

        return ChatClient.from_config(
            self.settings,
            router=self.llm_router,
            metrics_port=self.metrics_port,
        )

    # ── STT ──────────────────────────────────────────────────
    @cached_property
    def stt_service(self) -> STTPort:
        """Lazily build the STT service."""
        from ekko.infrastructure.factories.stt_factory import (
            create_azure_speech_stt,
        )

        return create_azure_speech_stt(settings=self.settings)

    def build_stt_service(
        self,
        *,
        on_transcript: Callable[[TranscriptSegment], object] | None = None,
    ) -> STTPort:
        """Build an STT service with request-specific callbacks."""
        from ekko.infrastructure.factories.stt_factory import create_azure_speech_stt

        return create_azure_speech_stt(settings=self.settings, on_transcript=on_transcript)

    # ── Audio ────────────────────────────────────────────────
    @cached_property
    def audio_controller(self) -> AudioStreamerControllerPort:
        """Lazily build the audio streamer controller."""
        from ekko.infrastructure.factories.audio_streamer_factory import (
            create_audio_streamer_controller,
        )

        return create_audio_streamer_controller(self.settings)

    # ── PII ──────────────────────────────────────────────────
    @cached_property
    def pii_anonymizer(self) -> PIIAnonymizerPort:
        """Lazily build the PII anonymizer."""
        from ekko.ai.pii.anonymizer import PIIAnonymizer as _PIIAnonymizer

        return _PIIAnonymizer()

    @cached_property
    def pii_service(self) -> PIIService:
        """Lazily build the PII policy service."""
        from ekko.application.services.pii_service import PIIService as _PIIService

        return _PIIService(
            anonymizer=self.pii_anonymizer,
            profile=self.settings.pii_policy_profile,
        )

    @cached_property
    def readiness_service(self) -> ReadinessService:
        """Lazily build the dependency readiness service."""
        from ekko.application.services.readiness_service import ReadinessService as _ReadinessService
        from ekko.infrastructure.clients.redis_readiness import RedisReadinessProbe
        from ekko.infrastructure.db.readiness import SQLAlchemyReadinessProbe

        redis_client = self.redis_client
        return _ReadinessService(
            database_probe=SQLAlchemyReadinessProbe(database_url=self.settings.database_url),
            redis_probe=RedisReadinessProbe(redis_client=redis_client) if redis_client is not None else None,
        )

    # ── Prompt registry ────────────────────────────────────────
    @cached_property
    def prompt_registry(self) -> PromptRegistryPort:
        """Lazily build the prompt registry client."""
        from ekko.ai.prompts.prompt_registry_client import PromptRegistryClient

        return PromptRegistryClient.from_config(self.settings)

    @cached_property
    def prompt_catalog_service(self) -> PromptCatalogService:
        """Lazily build the prompt catalog service."""
        from ekko.application.services.prompt_catalog_service import PromptCatalogService as _PromptCatalogService

        return _PromptCatalogService(
            prompt_registry=self.prompt_registry,
            version_set=self.settings.prompt_version_set,
        )

    @cached_property
    def transcript_broadcaster(self) -> TranscriptBroadcaster:
        """Lazily build the live transcript broadcaster."""
        from ekko.application.services.transcript_broadcaster import TranscriptBroadcaster as _TranscriptBroadcaster

        return _TranscriptBroadcaster()

    # ── Redis ──────────────────────────────────────────────────
    @cached_property
    def redis_client(self) -> Redis | None:
        """Lazily build the shared Redis client, or None when not configured."""
        from ekko.infrastructure.clients.redis import create_redis_client

        return create_redis_client(self.settings)

    # ── Application services ─────────────────────────────────
    @cached_property
    def summarizer_service(self) -> SummarizerService:
        """Lazily build the summarizer service."""
        from ekko.application.services.summarizer_service import SummarizerService as _SummarizerService

        return _SummarizerService(
            gateway=self.chat_client,
            prompt_registry=self.prompt_registry,
            pii_service=self.pii_service,
        )
