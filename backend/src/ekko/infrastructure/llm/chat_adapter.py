"""Provider-agnostic LangChain-based chat adapter for the voice app.

This mirrors the pattern used in the golden-standard `koda_automation` project:
- lazy model initialization per deployment
- provider-agnostic kwargs construction (Azure vs OpenAI)
- both sync and async invocation surfaces
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from ekko.config.enums import LLMProvider
from ekko.config.settings import BaseAppConfig, get_settings
from ekko.core.interfaces import ChatPort
from ekko.infrastructure.helpers.retry import api_retry

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel


def _build_provider_kwargs(settings: BaseAppConfig) -> dict[str, Any]:
    if settings.llm_provider == LLMProvider.AZURE_OPENAI:
        return {
            "azure_endpoint": settings.azure_openai_endpoint,
            "openai_api_version": settings.azure_openai_version,
            "api_key": settings.azure_openai_key.get_secret_value() if settings.azure_openai_key else None,
        }
    if settings.llm_provider == LLMProvider.OPENAI:
        return {"api_key": settings.openai_api_key.get_secret_value() if settings.openai_api_key else None}
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def _provider_deployment_key(provider: LLMProvider) -> str:
    match provider:
        case LLMProvider.AZURE_OPENAI:
            return "azure_deployment"
        case LLMProvider.OPENAI:
            return "model"
    raise ValueError(f"No deployment key for provider: {provider}")


def _extract_response_text(response: BaseMessage) -> str:
    content = response.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return str(content)


class ChatModelAdapter(ChatPort):
    """Adapter that exposes a provider-agnostic chat interface using LangChain."""

    def __init__(self, *, settings: BaseAppConfig | None = None) -> None:
        self._settings = settings or get_settings()
        self._provider = self._settings.llm_provider
        self._provider_kwargs = _build_provider_kwargs(self._settings)
        self._models: dict[str, BaseChatModel] = {}

    @classmethod
    def from_settings(cls, settings: BaseAppConfig) -> ChatModelAdapter:
        return cls(settings=settings)

    def _get_model(self, deployment_name: str) -> BaseChatModel:
        if deployment_name not in self._models:
            init_kwargs = {k: v for k, v in self._provider_kwargs.items() if v is not None}
            # set deployment key name depending on provider
            key = _provider_deployment_key(self._provider)
            init_kwargs[key] = deployment_name
            self._models[deployment_name] = init_chat_model(
                model=deployment_name,
                model_provider=self._provider,
                configurable_fields=None,
                **init_kwargs,
            )
        return self._models[deployment_name]

    @staticmethod
    def _build_messages(system: str, user: str) -> list[BaseMessage]:
        return [SystemMessage(content=system), HumanMessage(content=user)]

    @api_retry
    async def _run_completion_async(self, model: BaseChatModel, messages: list[BaseMessage], **kwargs: Any) -> str:
        response = await model.bind(**kwargs).ainvoke(messages)
        return _extract_response_text(response)

    @api_retry
    def _run_completion(self, model: BaseChatModel, messages: list[BaseMessage], **kwargs: Any) -> str:
        response = model.bind(**kwargs).invoke(messages)
        return _extract_response_text(response)

    def _prepare_invocation(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
        kwargs: dict[str, Any] | None = None,
    ) -> tuple[BaseChatModel, list[BaseMessage], dict[str, Any]]:
        llm = self._get_model(model)
        messages = self._build_messages(system_prompt, user_prompt)
        invoke_kwargs: dict[str, Any] = {
            "max_tokens": max_completion_tokens,
            "temperature": temperature,
        }
        if kwargs:
            invoke_kwargs.update(kwargs)
        return llm, messages, invoke_kwargs

    async def async_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        model: str,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        llm, messages, invoke_kwargs = self._prepare_invocation(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
            kwargs=kwargs,
        )
        return await self._run_completion_async(llm, messages, **invoke_kwargs)

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_completion_tokens: int = 1024,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        llm, messages, invoke_kwargs = self._prepare_invocation(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
            kwargs=kwargs,
        )
        return self._run_completion(llm, messages, **invoke_kwargs)
