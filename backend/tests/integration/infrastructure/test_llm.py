"""Integration tests for LLM chat adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest

if TYPE_CHECKING:
    from ekko.config.settings import AppSettings

pytestmark = pytest.mark.integration


@pytest.fixture
def llm_settings(integration_settings):
    """Settings configured for LLM integration testing."""
    from ekko.config.settings import AppSettings
    from ekko.core.enums import LLMProvider

    return AppSettings(
        environment=integration_settings.environment,
        debug=False,
        llm_provider=LLMProvider.OPENAI,
        openai_api_key="test-key",
        llm_deployment_name="gpt-4",
    )


@pytest.fixture
def azure_llm_settings(integration_settings):
    """Settings configured for Azure OpenAI integration testing."""
    from ekko.config.settings import AppSettings
    from ekko.core.enums import LLMProvider

    return AppSettings(
        environment=integration_settings.environment,
        debug=False,
        llm_provider=LLMProvider.AZURE_OPENAI,
        azure_openai_endpoint="https://test.openai.azure.com/",
        azure_openai_key="test-azure-key",
        azure_openai_version="2024-02-01",
        llm_deployment_name="gpt-4",
    )


@pytest.fixture
def mock_langchain_model():
    """Mock LangChain chat model."""
    mock_model = MagicMock()
    mock_model.bind.return_value = mock_model

    # Mock response with string content
    mock_response = MagicMock()
    mock_response.content = "This is a test response from the LLM."

    mock_model.invoke.return_value = mock_response
    mock_model.ainvoke = AsyncMock(return_value=mock_response)

    return mock_model


def test_chat_adapter_init_openai(llm_settings: AppSettings) -> None:
    """Test initializing chat adapter with OpenAI settings."""
    from ekko.core.enums import LLMProvider
    from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

    adapter = ChatModelAdapter(settings=llm_settings)

    assert adapter._provider == LLMProvider.OPENAI
    assert "api_key" in adapter._provider_kwargs
    assert adapter._provider_kwargs["api_key"] == "test-key"


def test_chat_adapter_init_azure(azure_llm_settings: AppSettings) -> None:
    """Test initializing chat adapter with Azure OpenAI settings."""
    from ekko.core.enums import LLMProvider
    from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

    adapter = ChatModelAdapter(settings=azure_llm_settings)

    assert adapter._provider == LLMProvider.AZURE_OPENAI
    assert "azure_endpoint" in adapter._provider_kwargs
    assert adapter._provider_kwargs["azure_endpoint"] == "https://test.openai.azure.com/"
    assert adapter._provider_kwargs["openai_api_version"] == "2024-02-01"


def test_chat_adapter_from_settings(llm_settings: AppSettings) -> None:
    """Test creating adapter using from_settings factory method."""
    from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

    adapter = ChatModelAdapter.from_settings(llm_settings)

    assert adapter._settings == llm_settings


def test_chat_adapter_build_messages(llm_settings: AppSettings) -> None:
    """Test building message list from system and user prompts."""
    from langchain_core.messages import HumanMessage, SystemMessage

    from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

    adapter = ChatModelAdapter(settings=llm_settings)

    system_prompt = "You are a helpful assistant."
    user_prompt = "What is the capital of France?"

    messages = adapter._build_messages(system_prompt, user_prompt)

    assert len(messages) == 2
    assert isinstance(messages[0], SystemMessage)
    assert messages[0].content == system_prompt
    assert isinstance(messages[1], HumanMessage)
    assert messages[1].content == user_prompt


def test_chat_adapter_sync_chat(llm_settings: AppSettings, mock_langchain_model: MagicMock) -> None:
    """Test synchronous chat invocation."""
    from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

    adapter = ChatModelAdapter(settings=llm_settings)

    # Pre-cache the mock model to avoid init_chat_model call
    adapter._models["gpt-4"] = mock_langchain_model

    response = adapter.chat(
        system_prompt="You are a helpful assistant.",
        user_prompt="Hello!",
        deployment_name="gpt-4",
        max_completion_tokens=512,
        temperature=0.7,
    )

    assert response == "This is a test response from the LLM."
    mock_langchain_model.invoke.assert_called_once()


@pytest.mark.asyncio
async def test_chat_adapter_async_chat(llm_settings: AppSettings, mock_langchain_model: MagicMock) -> None:
    """Test asynchronous chat invocation."""
    from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

    adapter = ChatModelAdapter(settings=llm_settings)

    # Pre-cache the mock model to avoid init_chat_model call
    adapter._models["gpt-4"] = mock_langchain_model

    response = await adapter.async_chat(
        system_prompt="You are a helpful assistant.",
        user_prompt="Hello async!",
        deployment_name="gpt-4",
        max_completion_tokens=512,
        temperature=0.7,
    )

    assert response == "This is a test response from the LLM."
    mock_langchain_model.ainvoke.assert_called_once()


def test_chat_adapter_model_caching(llm_settings: AppSettings, mock_langchain_model: MagicMock) -> None:
    """Test that models are cached per deployment name."""
    from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

    adapter = ChatModelAdapter(settings=llm_settings)

    # Manually cache models to test caching logic
    adapter._models["gpt-4"] = mock_langchain_model
    adapter._models["gpt-3.5-turbo"] = mock_langchain_model

    # First call should return cached model
    model1 = adapter._get_model("gpt-4")
    assert model1 is mock_langchain_model

    # Second call should return same cached model
    model2 = adapter._get_model("gpt-4")
    assert model2 is mock_langchain_model
    assert model2 is model1

    # Different deployment should return different cached model
    model3 = adapter._get_model("gpt-3.5-turbo")
    assert model3 is mock_langchain_model


def test_chat_adapter_extract_string_response() -> None:
    """Test extracting text from string response content."""
    from langchain_core.messages import AIMessage

    from ekko.infrastructure.llm.chat_adapter import _extract_response_text

    response = AIMessage(content="Simple string response")
    text = _extract_response_text(response)

    assert text == "Simple string response"


def test_chat_adapter_extract_list_response() -> None:
    """Test extracting text from list response content."""
    from langchain_core.messages import AIMessage

    from ekko.infrastructure.llm.chat_adapter import _extract_response_text

    response = AIMessage(
        content=[
            {"type": "text", "text": "First part"},
            {"type": "text", "text": "Second part"},
            "String part",
        ]
    )
    text = _extract_response_text(response)

    assert "First part" in text
    assert "Second part" in text
    assert "String part" in text


def test_chat_adapter_provider_kwargs_openai(llm_settings: AppSettings) -> None:
    """Test building provider kwargs for OpenAI."""
    from ekko.infrastructure.llm.chat_adapter import _build_provider_kwargs

    kwargs = _build_provider_kwargs(llm_settings)

    assert "api_key" in kwargs
    assert kwargs["api_key"] == "test-key"
    assert "azure_endpoint" not in kwargs


def test_chat_adapter_provider_kwargs_azure(azure_llm_settings: AppSettings) -> None:
    """Test building provider kwargs for Azure OpenAI."""
    from ekko.infrastructure.llm.chat_adapter import _build_provider_kwargs

    kwargs = _build_provider_kwargs(azure_llm_settings)

    assert "azure_endpoint" in kwargs
    assert kwargs["azure_endpoint"] == "https://test.openai.azure.com/"
    assert "openai_api_version" in kwargs
    assert kwargs["openai_api_version"] == "2024-02-01"
    assert "api_key" in kwargs


def test_chat_adapter_provider_deployment_key_openai() -> None:
    """Test getting deployment key name for OpenAI."""
    from ekko.core.enums import LLMProvider
    from ekko.infrastructure.llm.chat_adapter import _provider_deployment_key

    key = _provider_deployment_key(LLMProvider.OPENAI)
    assert key == "model"


def test_chat_adapter_provider_deployment_key_azure() -> None:
    """Test getting deployment key name for Azure OpenAI."""
    from ekko.core.enums import LLMProvider
    from ekko.infrastructure.llm.chat_adapter import _provider_deployment_key

    key = _provider_deployment_key(LLMProvider.AZURE_OPENAI)
    assert key == "azure_deployment"


@pytest.mark.asyncio
async def test_chat_adapter_kwargs_passthrough(llm_settings: AppSettings, mock_langchain_model: MagicMock) -> None:
    """Test that extra kwargs are passed through to model invocation."""
    from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

    adapter = ChatModelAdapter(settings=llm_settings)

    # Pre-cache the mock model to avoid init_chat_model call
    adapter._models["gpt-4"] = mock_langchain_model

    await adapter.async_chat(
        system_prompt="Test",
        user_prompt="Test",
        deployment_name="gpt-4",
        top_p=0.9,
        frequency_penalty=0.5,
    )

    # Verify extra kwargs were passed
    call_args = mock_langchain_model.bind.call_args
    assert "top_p" in call_args[1]
    assert call_args[1]["top_p"] == 0.9
    assert "frequency_penalty" in call_args[1]
    assert call_args[1]["frequency_penalty"] == 0.5
