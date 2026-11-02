"""Chat / LLM port protocols."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from ekko.core.types import MaxTokens, ModelDeploymentName, Temperature

if TYPE_CHECKING:
    from pydantic import BaseModel

_DEFAULT_MAX_TOKENS = MaxTokens(1024)
_DEFAULT_TEMPERATURE = Temperature(0.0)


@runtime_checkable
class ChatPort(Protocol):
    """Protocol for provider-agnostic chat/LLM adapters."""

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: ModelDeploymentName,
        max_completion_tokens: MaxTokens = _DEFAULT_MAX_TOKENS,
        temperature: Temperature = _DEFAULT_TEMPERATURE,
    ) -> str:
        """Complete a chat prompt synchronously."""
        ...

    async def achat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: ModelDeploymentName,
        max_completion_tokens: MaxTokens = _DEFAULT_MAX_TOKENS,
        temperature: Temperature = _DEFAULT_TEMPERATURE,
    ) -> str:
        """Complete a chat prompt asynchronously."""
        ...

    async def achat_structured[T: BaseModel](
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: ModelDeploymentName,
        response_model: type[T],
        max_completion_tokens: MaxTokens = _DEFAULT_MAX_TOKENS,
        temperature: Temperature = _DEFAULT_TEMPERATURE,
    ) -> T:
        """Complete a chat prompt into a typed response model."""
        ...
