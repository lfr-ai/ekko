"""Tests for provider-neutral LLM routing, errors, and telemetry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import override
from unittest.mock import AsyncMock, MagicMock, patch

import litellm
import pytest
from pydantic import BaseModel, SecretStr

from ekko.config.enums import LLMProvider
from ekko.config.settings.llm import LLMSettings
from ekko.core.exceptions import LLMError
from ekko.core.ports.external.metrics import MetricsPort
from ekko.infrastructure.clients.chat import ChatClient
from ekko.infrastructure.clients.llm_router import LLMRouter


@dataclass(kw_only=True, slots=True)
class _MetricsRecorder(MetricsPort):
    successes: list[tuple[str, float]] = field(default_factory=list)
    failures: list[tuple[str, float]] = field(default_factory=list)
    token_usage: list[tuple[str, int, int]] = field(default_factory=list)
    costs: list[tuple[str, float]] = field(default_factory=list)

    @override
    def record_request_success(self, *, operation: str, duration_seconds: float) -> None:
        self.successes.append((operation, duration_seconds))

    @override
    def record_request_failure(self, *, operation: str, duration_seconds: float) -> None:
        self.failures.append((operation, duration_seconds))

    @override
    def record_token_usage(
        self,
        *,
        operation: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        self.token_usage.append((operation, input_tokens, output_tokens))

    @override
    def record_cost(self, *, operation: str, cost_usd: float) -> None:
        self.costs.append((operation, cost_usd))


class _Summary(BaseModel):
    summary: str


def _response(content: str) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    response.usage = None
    return response


class TestRouterFallbackBehavior:
    @pytest.mark.unit
    def test_configured_fallbacks_create_ordered_model_mapping(self) -> None:
        settings = LLMSettings(
            llm_default_deployment="gpt-4o-mini",
            llm_fallback_deployments=["gpt-4o"],
            openai_api_key=SecretStr("openai-key"),
        )

        with patch("ekko.infrastructure.clients.llm_router.litellm.Router") as router_factory:
            router_factory.return_value = MagicMock()

            router = LLMRouter.from_config(settings)

        assert router is not None
        router_kwargs = router_factory.call_args.kwargs
        assert router_kwargs["fallbacks"] == [{"openai/gpt-4o-mini": ["openai/gpt-4o"]}]
        assert router_kwargs["model_list"][0]["litellm_params"]["api_key"] == ("openai-key")

    @pytest.mark.unit
    def test_default_model_uses_router_and_non_default_uses_direct_client(self) -> None:
        settings = LLMSettings(llm_default_deployment="gpt-4o-mini")
        router_client = MagicMock()
        router_client.completion.return_value = _response("routed")
        router = MagicMock(spec=LLMRouter)
        router.router = router_client
        router.should_route.side_effect = lambda model_name: model_name == "openai/gpt-4o-mini"
        client = ChatClient(settings=settings, router=router)

        with patch(
            "ekko.infrastructure.clients.chat.litellm.completion",
            return_value=_response("direct"),
        ) as direct_completion:
            routed = client.chat(
                system_prompt="system",
                user_prompt="user",
                model="gpt-4o-mini",
            )
            direct = client.chat(
                system_prompt="system",
                user_prompt="user",
                model="openai/gpt-4o",
            )

        assert routed == "routed"
        assert direct == "direct"
        router_client.completion.assert_called_once()
        direct_completion.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_async_default_model_uses_router(self) -> None:
        settings = LLMSettings(llm_default_deployment="gpt-4o-mini")
        router_client = MagicMock()
        router_client.acompletion = AsyncMock(return_value=_response("routed"))
        router = MagicMock(spec=LLMRouter)
        router.router = router_client
        router.should_route.return_value = True
        client = ChatClient(settings=settings, router=router)

        result = await client.achat(
            system_prompt="system",
            user_prompt="user",
            model="gpt-4o-mini",
        )

        assert result == "routed"
        router_client.acompletion.assert_awaited_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_structured_default_model_uses_router(self) -> None:
        settings = LLMSettings(llm_default_deployment="gpt-4o-mini")
        router_client = MagicMock()
        router_client.acompletion = AsyncMock(return_value=_response('{"summary":"routed"}'))
        router = MagicMock(spec=LLMRouter)
        router.router = router_client
        router.should_route.return_value = True
        client = ChatClient(settings=settings, router=router)

        result = await client.achat_structured(
            system_prompt="system",
            user_prompt="user",
            model="gpt-4o-mini",
            response_model=_Summary,
        )

        assert result == _Summary(summary="routed")
        router_client.acompletion.assert_awaited_once()


class TestRetryExceptionHandling:
    @pytest.mark.unit
    def test_transient_error_retries_before_translation(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("tenacity.nap.time.sleep", lambda _seconds: None)
        settings = LLMSettings()
        client = ChatClient(settings=settings)
        failure = litellm.APIError(
            message="provider unavailable",
            status_code=503,
            model="gpt-4o-mini",
            llm_provider="openai",
        )

        with patch(
            "ekko.infrastructure.clients.chat.litellm.completion",
            side_effect=[failure, failure, _response("recovered")],
        ) as completion:
            result = client.chat(
                system_prompt="system",
                user_prompt="user",
                model="gpt-4o-mini",
            )

        assert result == "recovered"
        assert completion.call_count == 3

    @pytest.mark.unit
    def test_exhausted_transient_error_raises_core_error_after_retries(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("tenacity.nap.time.sleep", lambda _seconds: None)
        settings = LLMSettings()
        client = ChatClient(settings=settings)
        failure = litellm.APIError(
            message="provider unavailable",
            status_code=503,
            model="gpt-4o-mini",
            llm_provider="openai",
        )

        with (
            patch(
                "ekko.infrastructure.clients.chat.litellm.completion",
                side_effect=failure,
            ) as completion,
            pytest.raises(LLMError, match="provider request failed"),
        ):
            client.chat(
                system_prompt="system",
                user_prompt="user",
                model="gpt-4o-mini",
            )

        assert completion.call_count == 3


class TestProviderCredentialResolution:
    @pytest.mark.unit
    def test_anthropic_provider_prefixes_unqualified_model(self) -> None:
        settings = LLMSettings(
            llm_provider=LLMProvider.ANTHROPIC,
            litellm_api_key=SecretStr("anthropic-key"),
        )

        with patch(
            "ekko.infrastructure.clients.chat.litellm.completion",
            return_value=_response("response"),
        ) as completion:
            ChatClient(settings=settings).chat(
                system_prompt="system",
                user_prompt="user",
                model="claude-3-opus",
            )

        call_kwargs = completion.call_args.kwargs
        assert call_kwargs["model"] == "anthropic/claude-3-opus"
        assert call_kwargs["api_key"] == "anthropic-key"

    @pytest.mark.unit
    def test_prefixed_provider_uses_generic_credentials(self) -> None:
        settings = LLMSettings(
            llm_provider=LLMProvider.OPENAI,
            openai_api_key=SecretStr("openai-key"),
            litellm_api_key=SecretStr("anthropic-key"),
            litellm_api_base="https://api.anthropic.com",
        )
        response = _response("response")

        with patch(
            "ekko.infrastructure.clients.chat.litellm.completion",
            return_value=response,
        ) as completion:
            ChatClient(settings=settings).chat(
                system_prompt="system",
                user_prompt="user",
                model="anthropic/claude-3-opus",
            )

        call_kwargs = completion.call_args.kwargs
        assert call_kwargs["api_key"] == "anthropic-key"
        assert call_kwargs["api_base"] == "https://api.anthropic.com"

    @pytest.mark.unit
    def test_azure_prefix_uses_azure_credentials(self) -> None:
        settings = LLMSettings(
            llm_provider=LLMProvider.OPENAI,
            openai_api_key=SecretStr("openai-key"),
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_key=SecretStr("azure-key"),
            azure_openai_version="2025-02-01-preview",
        )

        with patch(
            "ekko.infrastructure.clients.chat.litellm.completion",
            return_value=_response("response"),
        ) as completion:
            ChatClient(settings=settings).chat(
                system_prompt="system",
                user_prompt="user",
                model="azure/deployment",
            )

        call_kwargs = completion.call_args.kwargs
        assert call_kwargs["api_base"] == "https://test.openai.azure.com/"
        assert call_kwargs["api_key"] == "azure-key"


class TestMetricsPortIntegration:
    @pytest.mark.unit
    def test_successful_request_records_usage_and_cost_only_when_enabled(self) -> None:
        response = _response("response")
        response.usage = litellm.types.utils.Usage(
            prompt_tokens=5,
            completion_tokens=3,
            total_tokens=8,
        )
        metrics = _MetricsRecorder()
        settings = LLMSettings(llm_track_costs=True)

        with (
            patch(
                "ekko.infrastructure.clients.chat.litellm.completion",
                return_value=response,
            ),
            patch(
                "ekko.infrastructure.clients.chat.litellm.completion_cost",
                return_value=0.02,
            ),
        ):
            ChatClient(settings=settings, metrics_port=metrics).chat(
                system_prompt="system",
                user_prompt="user",
                model="gpt-4o-mini",
            )

        assert len(metrics.successes) == 1
        assert metrics.token_usage == [("chat", 5, 3)]
        assert metrics.costs == [("chat", 0.02)]

    @pytest.mark.unit
    def test_failed_request_records_failure_without_content(self) -> None:
        metrics = _MetricsRecorder()
        failure = litellm.APIError(
            message="provider unavailable",
            status_code=503,
            model="gpt-4o-mini",
            llm_provider="openai",
        )

        with (
            patch("tenacity.nap.time.sleep", lambda _seconds: None),
            patch(
                "ekko.infrastructure.clients.chat.litellm.completion",
                side_effect=failure,
            ),
            pytest.raises(LLMError, match="provider request failed"),
        ):
            ChatClient(settings=LLMSettings(), metrics_port=metrics).chat(
                system_prompt="not recorded",
                user_prompt="not recorded",
                model="gpt-4o-mini",
            )

        assert len(metrics.failures) == 1
        assert metrics.token_usage == []
        assert metrics.costs == []
