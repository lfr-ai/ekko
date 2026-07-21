"""Mock LLM adapter for testing."""

from __future__ import annotations

from typing import Any


class MockLLMAdapter:
    """Mock LLM adapter that returns predefined responses."""

    def __init__(self, response_text: str = "Test LLM response") -> None:
        self.response_text = response_text
        self.call_count = 0
        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        deployment_name: str,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        """Return mock response."""
        _ = (deployment_name, max_completion_tokens, temperature, kwargs)
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.response_text

    async def async_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        deployment_name: str,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        """Return mock response asynchronously."""
        _ = (deployment_name, max_completion_tokens, temperature, kwargs)
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.response_text


class FailingLLMAdapter(MockLLMAdapter):
    """Mock LLM adapter that simulates failures."""

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        deployment_name: str,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        """Simulate LLM failure."""
        _ = (
            system_prompt,
            user_prompt,
            deployment_name,
            max_completion_tokens,
            temperature,
            kwargs,
        )
        raise RuntimeError("LLM processing failed")

    async def async_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        deployment_name: str,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        """Simulate async LLM failure."""
        _ = (
            system_prompt,
            user_prompt,
            deployment_name,
            max_completion_tokens,
            temperature,
            kwargs,
        )
        raise RuntimeError("LLM processing failed")
