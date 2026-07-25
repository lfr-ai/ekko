"""Unit tests for the LiteLLM chat adapter."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ekko.infrastructure.llm.litellm_adapter import (
    LiteLLMChatAdapter,
    _build_litellm_kwargs,
    _build_model_name,
)


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = MagicMock()
    settings.llm_provider = MagicMock()
    settings.llm_provider.value = "openai"
    settings.llm_provider.__eq__ = lambda self, other: self.value == other.value
    settings.openai_api_key = MagicMock()
    settings.openai_api_key.get_secret_value.return_value = "test-key"
    settings.azure_openai_endpoint = None
    settings.azure_openai_version = "2025-02-01-preview"
    settings.azure_openai_key = None
    return settings


@pytest.fixture
def openai_settings(mock_settings):
    """Create OpenAI-configured settings."""
    from ekko.config.enums import LLMProvider

    mock_settings.llm_provider = LLMProvider.OPENAI
    return mock_settings


@pytest.fixture
def azure_settings(mock_settings):
    """Create Azure OpenAI-configured settings."""
    from ekko.config.enums import LLMProvider

    mock_settings.llm_provider = LLMProvider.AZURE_OPENAI
    mock_settings.azure_openai_endpoint = "https://test.openai.azure.com/"
    mock_settings.azure_openai_version = "2025-02-01-preview"
    mock_settings.azure_openai_key = MagicMock()
    mock_settings.azure_openai_key.get_secret_value.return_value = "azure-key"
    return mock_settings


class TestBuildModelName:
    """Test model name prefix construction."""

    @pytest.mark.unit
    def test_openai_prefix(self, openai_settings) -> None:
        """Add openai/ prefix for OpenAI provider."""
        result = _build_model_name(model="gpt-4o", settings=openai_settings)
        assert result == "openai/gpt-4o"

    @pytest.mark.unit
    def test_azure_prefix(self, azure_settings) -> None:
        """Add azure/ prefix for Azure OpenAI provider."""
        result = _build_model_name(model="gpt-4o", settings=azure_settings)
        assert result == "azure/gpt-4o"

    @pytest.mark.unit
    def test_already_prefixed_passthrough(self, openai_settings) -> None:
        """Pass through already-prefixed model names."""
        result = _build_model_name(model="anthropic/claude-3", settings=openai_settings)
        assert result == "anthropic/claude-3"


class TestBuildLitellmKwargs:
    """Test provider kwargs construction."""

    @pytest.mark.unit
    def test_openai_kwargs(self, openai_settings) -> None:
        """Build OpenAI kwargs with API key."""
        kwargs = _build_litellm_kwargs(openai_settings)
        assert kwargs == {"api_key": "test-key"}

    @pytest.mark.unit
    def test_azure_kwargs(self, azure_settings) -> None:
        """Build Azure kwargs with endpoint and key."""
        kwargs = _build_litellm_kwargs(azure_settings)
        assert kwargs["api_base"] == "https://test.openai.azure.com/"
        assert kwargs["api_version"] == "2025-02-01-preview"
        assert kwargs["api_key"] == "azure-key"


class TestLiteLLMChatAdapterSync:
    """Test synchronous chat method."""

    @pytest.mark.unit
    @patch("ekko.infrastructure.llm.litellm_adapter.litellm.completion")
    def test_chat_returns_response_text(self, mock_completion, openai_settings) -> None:
        """Return extracted text from completion response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello world"
        mock_completion.return_value = mock_response

        adapter = LiteLLMChatAdapter(settings=openai_settings)
        result = adapter.chat(
            system_prompt="You are helpful.",
            user_prompt="Say hello.",
            model="gpt-4o",
        )

        assert result == "Hello world"
        mock_completion.assert_called_once()

    @pytest.mark.unit
    @patch("ekko.infrastructure.llm.litellm_adapter.litellm.completion")
    def test_chat_handles_none_content(self, mock_completion, openai_settings) -> None:
        """Return empty string when content is None."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_completion.return_value = mock_response

        adapter = LiteLLMChatAdapter(settings=openai_settings)
        result = adapter.chat(
            system_prompt="system",
            user_prompt="user",
            model="gpt-4o",
        )

        assert result == ""


class TestLiteLLMChatAdapterAsync:
    """Test asynchronous chat method."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch("ekko.infrastructure.llm.litellm_adapter.litellm.acompletion")
    async def test_async_chat_returns_response_text(self, mock_acompletion, openai_settings) -> None:
        """Return extracted text from async completion response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Async hello"
        mock_acompletion.return_value = mock_response

        adapter = LiteLLMChatAdapter(settings=openai_settings)
        result = await adapter.async_chat(
            system_prompt="You are helpful.",
            user_prompt="Say hello.",
            model="gpt-4o",
        )

        assert result == "Async hello"
        mock_acompletion.assert_called_once()
