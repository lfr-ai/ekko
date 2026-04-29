from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ekko.infrastructure.llm.chat_adapter import ChatModelAdapter

if TYPE_CHECKING:
    from ekko.config.settings import BaseAppConfig


class AzureOpenAIClient:
    """Compatibility shim that delegates to the provider-agnostic ChatModelAdapter.

    Historically this class wrapped the AzureOpenAI SDK. To centralize LLM
    usage and keep a single surface for tests, it now forwards calls to the
    LangChain-based `ChatModelAdapter`.
    """

    def __init__(self, settings: BaseAppConfig | None = None) -> None:  # noqa: ARG002
        self._adapter = ChatModelAdapter()

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float,
        max_completion_tokens: int,
        **kwargs: Any,
    ) -> str:
        """Delegate chat completions to the ChatModelAdapter."""
        return self._adapter.chat(
            system_prompt,
            user_prompt,
            deployment_name=model,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            **kwargs,
        )
