"""Unit tests for LLM configuration and settings."""

from __future__ import annotations

import pytest
from pydantic import SecretStr

from ekko.config.enums import LLMProvider
from ekko.config.settings.llm import LLMSettings


class TestLLMSettings:
    """Test typed LLM settings and configuration."""

    @pytest.mark.unit
    def test_default_settings(self) -> None:
        """Test default values when no configuration is provided."""
        settings = LLMSettings()
        assert settings.llm_provider == LLMProvider.OPENAI
        assert settings.llm_default_deployment is None
        assert settings.llm_fallback_deployments is None
        assert settings.litellm_api_key is None
        assert settings.litellm_api_base is None
        assert settings.litellm_api_version is None
        assert settings.llm_track_costs is False

    @pytest.mark.unit
    def test_default_model_setting(self) -> None:
        """Test configuration of default deployment model."""
        settings = LLMSettings(llm_default_deployment="gpt-4o")
        assert settings.llm_default_deployment == "gpt-4o"

    @pytest.mark.unit
    def test_fallback_deployments_setting(self) -> None:
        """Test configuration of optional fallback deployment list."""
        fallbacks = ["gpt-4o", "gpt-4-turbo", "gpt-4"]
        settings = LLMSettings(llm_fallback_deployments=fallbacks)
        assert settings.llm_fallback_deployments == fallbacks

    @pytest.mark.unit
    def test_generic_litellm_settings(self) -> None:
        """Test generic LiteLLM API configuration fields."""
        settings = LLMSettings(
            litellm_api_key=SecretStr("sk-test-key"),
            litellm_api_base="https://api.example.com/v1",
            litellm_api_version="2024-10-01",
        )
        assert settings.litellm_api_key.get_secret_value() == "sk-test-key"
        assert settings.litellm_api_base == "https://api.example.com/v1"
        assert settings.litellm_api_version == "2024-10-01"

    @pytest.mark.unit
    def test_cost_tracking_disabled_by_default(self) -> None:
        """Test that cost tracking is opt-in and disabled by default."""
        settings = LLMSettings()
        assert settings.llm_track_costs is False

    @pytest.mark.unit
    def test_cost_tracking_enabled(self) -> None:
        """Test enabling cost tracking."""
        settings = LLMSettings(llm_track_costs=True)
        assert settings.llm_track_costs is True

    @pytest.mark.unit
    def test_azure_openai_with_fallback(self) -> None:
        """Test Azure OpenAI provider with fallback deployments."""
        fallbacks = ["deployment-prod", "deployment-secondary"]
        settings = LLMSettings(
            llm_provider=LLMProvider.AZURE_OPENAI,
            llm_default_deployment="deployment-primary",
            llm_fallback_deployments=fallbacks,
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_key=SecretStr("test-key"),
        )
        assert settings.llm_provider == LLMProvider.AZURE_OPENAI
        assert settings.llm_default_deployment == "deployment-primary"
        assert settings.llm_fallback_deployments == fallbacks

    @pytest.mark.unit
    def test_empty_fallback_list_preserves_direct_call(self) -> None:
        """Test that empty fallback list preserves direct single-model behavior."""
        settings = LLMSettings(
            llm_default_deployment="gpt-4o",
            llm_fallback_deployments=None,  # Empty/not configured
        )
        # Fallback deployments should remain None (no Router constructed)
        assert settings.llm_fallback_deployments is None

    @pytest.mark.unit
    def test_multiple_deployment_types(self) -> None:
        """Test configuration with mixed provider-qualified names."""
        fallbacks = [
            "gpt-4o",  # Default provider suffix applies
            "anthropic/claude-3-opus",  # Already prefixed
            "azure/deployment-prod",  # Already prefixed
        ]
        settings = LLMSettings(
            llm_fallback_deployments=fallbacks,
        )
        assert settings.llm_fallback_deployments == fallbacks
