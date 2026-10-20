"""Tests for the LiteLLM Router factory."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from ekko.config.settings.llm import LLMSettings
from ekko.infrastructure.clients.llm_router import LLMRouter


class TestLLMRouter:
    @pytest.mark.unit
    def test_router_builds_lite_llm_fallback_groups(self) -> None:
        settings = LLMSettings(
            llm_default_deployment="gpt-4o-mini",
            llm_fallback_deployments=["gpt-4o"],
        )

        router = LLMRouter.from_config(settings)

        assert router is not None
        assert router.should_route("openai/gpt-4o-mini")
        assert not router.should_route("openai/gpt-4o")

    @pytest.mark.unit
    def test_no_fallbacks_returns_no_router(self) -> None:
        settings = LLMSettings(llm_fallback_deployments=None)

        with patch("ekko.infrastructure.clients.llm_router.litellm.Router") as factory:
            router = LLMRouter.from_config(settings)

        assert router is None
        factory.assert_not_called()

    @pytest.mark.unit
    def test_primary_repeated_as_fallback_raises_configuration_error(self) -> None:
        settings = LLMSettings(
            llm_default_deployment="gpt-4o",
            llm_fallback_deployments=["openai/gpt-4o"],
        )

        with pytest.raises(ValueError, match="must not duplicate"):
            LLMRouter.from_config(settings)

    @pytest.mark.unit
    def test_fallbacks_configures_primary_and_ordered_fallbacks(self) -> None:
        settings = LLMSettings(
            llm_default_deployment="gpt-4o-mini",
            llm_fallback_deployments=["gpt-4o", "gpt-4.1-mini"],
            openai_api_key=SecretStr("openai-key"),
        )

        with patch("ekko.infrastructure.clients.llm_router.litellm.Router") as factory:
            factory.return_value = MagicMock()

            router = LLMRouter.from_config(settings)

        assert router is not None
        router_kwargs = factory.call_args.kwargs
        assert router_kwargs["fallbacks"] == [{"openai/gpt-4o-mini": ["openai/gpt-4o", "openai/gpt-4.1-mini"]}]
        assert router_kwargs["num_retries"] == 2
        assert [deployment["model_name"] for deployment in router_kwargs["model_list"]] == [
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "openai/gpt-4.1-mini",
        ]
