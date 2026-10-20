"""Unit tests for the ChatClient (LiteLLM chat port implementation)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from ekko.config.enums import LLMProvider
from ekko.config.settings.llm import LLMSettings
from ekko.core.exceptions import LLMError
from ekko.core.types import MaxTokens, Temperature
from ekko.infrastructure.clients.chat import ChatClient


@pytest.fixture
def openai_settings() -> LLMSettings:
    """Create OpenAI-configured settings."""
    return LLMSettings(
        llm_provider=LLMProvider.OPENAI,
        openai_api_key=SecretStr("test-key"),
    )


@pytest.fixture
def azure_settings() -> LLMSettings:
    """Create Azure OpenAI-configured settings."""
    return LLMSettings(
        llm_provider=LLMProvider.AZURE_OPENAI,
        azure_openai_endpoint="https://test.openai.azure.com/",
        azure_openai_version="2025-02-01-preview",
        azure_openai_key=SecretStr("azure-key"),
    )


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
        call_kwargs = mock_litellm.completion.call_args.kwargs
        assert call_kwargs["model"] == "openai/gpt-4o"
        assert call_kwargs["messages"] == [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Say hello."},
        ]
        assert call_kwargs["api_key"] == "test-key"

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
    @patch("ekko.infrastructure.clients.chat.litellm")
    def test_chat_uses_azure_settings_for_azure_deployment(
        self,
        mock_litellm,
        azure_settings,
    ) -> None:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"
        mock_litellm.completion.return_value = mock_response

        ChatClient(settings=azure_settings).chat(
            system_prompt="s",
            user_prompt="u",
            model="gpt-4o",
        )

        call_kwargs = mock_litellm.completion.call_args.kwargs
        assert call_kwargs["model"] == "azure/gpt-4o"
        assert call_kwargs["api_base"] == "https://test.openai.azure.com/"
        assert call_kwargs["api_version"] == "2025-02-01-preview"
        assert call_kwargs["api_key"] == "azure-key"

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
