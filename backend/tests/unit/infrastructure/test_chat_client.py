"""Unit tests for the ChatClient (LiteLLM chat port implementation)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ekko.core.exceptions import LLMError
from ekko.core.types import MaxTokens, Temperature
from ekko.infrastructure.clients.chat import (
    ChatClient,
    _build_messages,
    _build_model_name,
    _build_provider_kwargs,
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
        result = _build_model_name(model="gpt-4o", settings=openai_settings)
        assert result == "openai/gpt-4o"

    @pytest.mark.unit
    def test_azure_prefix(self, azure_settings) -> None:
        result = _build_model_name(model="gpt-4o", settings=azure_settings)
        assert result == "azure/gpt-4o"

    @pytest.mark.unit
    def test_already_prefixed_passthrough(self, openai_settings) -> None:
        result = _build_model_name(model="anthropic/claude-3", settings=openai_settings)
        assert result == "anthropic/claude-3"


class TestBuildProviderKwargs:
    """Test provider kwargs construction."""

    @pytest.mark.unit
    def test_openai_kwargs(self, openai_settings) -> None:
        kwargs = _build_provider_kwargs(openai_settings)
        assert kwargs == {"api_key": "test-key"}

    @pytest.mark.unit
    def test_azure_kwargs(self, azure_settings) -> None:
        kwargs = _build_provider_kwargs(azure_settings)
        assert kwargs["api_base"] == "https://test.openai.azure.com/"
        assert kwargs["api_version"] == "2025-02-01-preview"
        assert kwargs["api_key"] == "azure-key"


class TestBuildMessages:
    """Test message list construction."""

    @pytest.mark.unit
    def test_builds_system_and_user_messages(self) -> None:
        messages = _build_messages(system_prompt="Be helpful.", user_prompt="Hello")
        assert len(messages) == 2
        assert messages[0] == {"role": "system", "content": "Be helpful."}
        assert messages[1] == {"role": "user", "content": "Hello"}


class TestChatClientSync:
    """Test synchronous chat method."""

    @pytest.mark.unit
    @patch("ekko.infrastructure.clients.chat.litellm")
    def test_chat_returns_response_text(self, mock_litellm, openai_settings) -> None:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello world"
        mock_litellm.completion.return_value = mock_response

        client = ChatClient(settings=openai_settings)
        result = client.chat(
            system_prompt="You are helpful.",
            user_prompt="Say hello.",
            model="gpt-4o",
        )

        assert result == "Hello world"
        mock_litellm.completion.assert_called_once()

    @pytest.mark.unit
    @patch("ekko.infrastructure.clients.chat.litellm")
    def test_chat_raises_on_none_content(self, mock_litellm, openai_settings) -> None:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_litellm.completion.return_value = mock_response

        client = ChatClient(settings=openai_settings)
        with pytest.raises(LLMError, match="no content"):
            client.chat(system_prompt="s", user_prompt="u", model="gpt-4o")

    @pytest.mark.unit
    @patch("ekko.infrastructure.clients.chat.litellm")
    def test_chat_passes_temperature_and_tokens(self, mock_litellm, openai_settings) -> None:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"
        mock_litellm.completion.return_value = mock_response

        client = ChatClient(settings=openai_settings)
        client.chat(
            system_prompt="s",
            user_prompt="u",
            model="gpt-4o",
            temperature=Temperature(0.7),
            max_completion_tokens=MaxTokens(2048),
        )

        call_kwargs = mock_litellm.completion.call_args[1]
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 2048

    @pytest.mark.unit
    def test_from_config_factory(self, openai_settings) -> None:
        client = ChatClient.from_config(openai_settings)
        assert isinstance(client, ChatClient)


class TestChatClientAsync:
    """Test asynchronous chat method."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch("ekko.infrastructure.clients.chat.litellm")
    async def test_achat_returns_response_text(self, mock_litellm, openai_settings) -> None:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Async hello"
        mock_litellm.acompletion = AsyncMock(return_value=mock_response)

        client = ChatClient(settings=openai_settings)
        result = await client.achat(
            system_prompt="You are helpful.",
            user_prompt="Say hello.",
            model="gpt-4o",
        )

        assert result == "Async hello"
        mock_litellm.acompletion.assert_called_once()
