from __future__ import annotations

from typing import Any

from voice.config.config import Config
from voice.infrastructure.llm.chat_adapter import ChatModelAdapter


class AzureOpenAIClient:
    """Compatibility shim that delegates to the provider-agnostic ChatModelAdapter.

    Historically this class wrapped the AzureOpenAI SDK. To centralize LLM
    usage and keep a single surface for tests, it now forwards calls to the
    LangChain-based `ChatModelAdapter`.
    """

    def __init__(self, cfg: Config) -> None:
        # Keep the historical constructor signature for backwards compatibility
        # but prefer the ChatModelAdapter implementation under the hood.
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
        """Delegate chat completions to the ChatModelAdapter.

        The ``model`` parameter is mapped to the adapter's ``deployment_name``
        for provider-agnostic invocation.
        """
        return self._adapter.chat(
            system_prompt,
            user_prompt,
            deployment_name=model,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            **kwargs,
        )
