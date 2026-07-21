"""Chat / LLM port protocols."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ChatPort(Protocol):
    """Protocol for provider-agnostic chat/LLM adapters."""

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str: ...

    async def async_chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str: ...
