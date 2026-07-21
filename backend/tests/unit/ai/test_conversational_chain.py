"""Tests for conversational chain."""

import asyncio

import pytest

from ekko.ai.chains.conversational import ConversationalChain
from ekko.ai.prompts.templates import CONVERSATIONAL_SYSTEM
from ekko.core.enums import MessageRole


class MockLLMAdapter:
    """Mock LLM adapter for testing."""

    def __init__(self, response: str = "mock response"):
        self.response = response
        self.call_count = 0
        self.last_system_prompt = None
        self.last_user_prompt = None

    async def async_chat(self, *, system_prompt: str, user_prompt: str) -> str:
        """Mock async chat method."""
        await asyncio.sleep(0)
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.response


@pytest.fixture(autouse=True)
def stub_prompt_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ekko.ai.chains.conversational.get_prompt_text",
        lambda *_args, **_kwargs: CONVERSATIONAL_SYSTEM,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_conversational_chain_basic():
    # Arrange
    llm = MockLLMAdapter(response="Hello, how can I help?")
    chain = ConversationalChain(llm=llm)

    # Act
    response = await chain.run("Hi there")

    # Assert
    assert response == "Hello, how can I help?"
    assert len(chain.history) == 2
    assert chain.history[0]["role"] == MessageRole.USER
    assert chain.history[0]["content"] == "Hi there"
    assert chain.history[1]["role"] == MessageRole.ASSISTANT
    assert chain.history[1]["content"] == "Hello, how can I help?"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_conversational_chain_maintains_history():
    # Arrange
    llm = MockLLMAdapter(response="Response 1")
    chain = ConversationalChain(llm=llm)

    # Act
    await chain.run("Message 1")
    llm.response = "Response 2"
    await chain.run("Message 2")

    # Assert
    assert len(chain.history) == 4
    assert chain.history[0]["content"] == "Message 1"
    assert chain.history[1]["content"] == "Response 1"
    assert chain.history[2]["content"] == "Message 2"
    assert chain.history[3]["content"] == "Response 2"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_conversational_chain_respects_max_history():
    # Arrange
    llm = MockLLMAdapter(response="Response")
    chain = ConversationalChain(llm=llm, max_history=2)

    # Act
    await chain.run("Message 1")
    await chain.run("Message 2")
    await chain.run("Message 3")

    # Assert - All messages stored in history
    assert len(chain.history) == 6

    # Context building should only use last 2 messages
    context = chain._build_context()
    assert "Message 1" not in context
    assert "Message 3" in context


@pytest.mark.unit
@pytest.mark.asyncio
async def test_conversational_chain_clear_history():
    # Arrange
    llm = MockLLMAdapter(response="Response")
    chain = ConversationalChain(llm=llm)
    await chain.run("Message 1")
    await chain.run("Message 2")

    # Act
    chain.clear_history()

    # Assert
    assert len(chain.history) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_conversational_chain_builds_context_from_empty_history():
    # Arrange
    llm = MockLLMAdapter(response="Response")
    chain = ConversationalChain(llm=llm)

    # Act
    context = chain._build_context()

    # Assert
    assert context == "No prior conversation."


@pytest.mark.unit
@pytest.mark.asyncio
async def test_conversational_chain_injects_context_in_system_prompt():
    # Arrange
    llm = MockLLMAdapter(response="Response")
    chain = ConversationalChain(llm=llm)

    # Act
    await chain.run("Test message")

    # Assert
    assert llm.last_system_prompt is not None
    assert "context" in llm.last_system_prompt.lower() or "conversation" in llm.last_system_prompt.lower()
    assert llm.last_user_prompt == "Test message"


@pytest.mark.unit
def test_conversational_chain_default_max_history():
    # Arrange / Act
    llm = MockLLMAdapter()
    chain = ConversationalChain(llm=llm)

    # Assert
    assert chain.max_history == 20
