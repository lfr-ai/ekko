"""Mock chat client for testing."""

from __future__ import annotations

from ekko.core.types import MaxTokens, ModelDeploymentName, Temperature

_DEFAULT_MAX_TOKENS: MaxTokens = MaxTokens(1024)
_DEFAULT_TEMPERATURE: Temperature = Temperature(0.0)


class MockChatClient:
    """Mock chat client that returns predefined responses."""

    def __init__(self, response_text: str = "Test LLM response") -> None:
        self.response_text = response_text
        self.call_count = 0
        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: ModelDeploymentName = "mock",
        max_completion_tokens: MaxTokens = _DEFAULT_MAX_TOKENS,
        temperature: Temperature = _DEFAULT_TEMPERATURE,
    ) -> str:
        """Return mock response."""
        _ = (model, max_completion_tokens, temperature)
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.response_text

    async def achat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: ModelDeploymentName = "mock",
        max_completion_tokens: MaxTokens = _DEFAULT_MAX_TOKENS,
        temperature: Temperature = _DEFAULT_TEMPERATURE,
    ) -> str:
        """Return mock response asynchronously."""
        _ = (model, max_completion_tokens, temperature)
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.response_text


class FailingChatClient(MockChatClient):
    """Mock chat client that simulates failures."""

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: ModelDeploymentName = "mock",
        max_completion_tokens: MaxTokens = _DEFAULT_MAX_TOKENS,
        temperature: Temperature = _DEFAULT_TEMPERATURE,
    ) -> str:
        """Simulate chat failure."""
        _ = (
            system_prompt,
            user_prompt,
            model,
            max_completion_tokens,
            temperature,
        )
        raise RuntimeError("Chat processing failed")

    async def achat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: ModelDeploymentName = "mock",
        max_completion_tokens: MaxTokens = _DEFAULT_MAX_TOKENS,
        temperature: Temperature = _DEFAULT_TEMPERATURE,
    ) -> str:
        """Simulate async chat failure."""
        _ = (
            system_prompt,
            user_prompt,
            model,
            max_completion_tokens,
            temperature,
        )
        raise RuntimeError("Chat processing failed")
