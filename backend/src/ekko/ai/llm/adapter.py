"""LLM adapter that bridges the core LLM protocol to the AI layer.

This module provides a clean interface for the AI layer and CrewAI
components, delegating to any ``ChatPort``-compatible adapter
injected at construction time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ekko.config.settings import BaseAppConfig, get_settings

if TYPE_CHECKING:
    from ekko.core.interfaces import ChatPort


class LLMAdapter:
    """Provider-agnostic LLM adapter.

    Delegates to an injected ``ChatPort`` implementation, keeping the
    AI layer free from infrastructure imports.
    """

    def __init__(
        self,
        *,
        chat_adapter: ChatPort | None = None,
        settings: BaseAppConfig | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._default_deployment = self._settings.llm_default_deployment or self._settings.rag_llm_model
        self._chat_adapter = chat_adapter

    @property
    def default_deployment(self) -> str:
        """Return the default LLM deployment name."""
        return self._default_deployment

    @property
    def chat_adapter(self) -> ChatPort:
        """Return the injected chat adapter.

        Raises:
            RuntimeError: If no chat adapter was injected.
        """
        if self._chat_adapter is None:
            msg = "LLMAdapter requires a chat_adapter; wire it via the DI container."
            raise RuntimeError(msg)
        return self._chat_adapter

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model: str | None = None,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> str:
        """Synchronous chat completion."""
        return self.chat_adapter.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model or self._default_deployment,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
        )

    async def async_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model: str | None = None,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> str:
        """Asynchronous chat completion."""
        return await self.chat_adapter.async_chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model or self._default_deployment,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
        )
