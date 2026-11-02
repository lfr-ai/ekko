"""Chat client implementing ChatPort through LiteLLM."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Protocol, Self, final

import litellm
import litellm.types.llms.openai
import litellm.types.utils
from pydantic import BaseModel, ValidationError

from ekko.config.enums import LLMProvider
from ekko.core.exceptions import LLMError
from ekko.core.types import MaxTokens, Temperature
from ekko.infrastructure.helpers.retry import api_retry

if TYPE_CHECKING:
    from pydantic import SecretStr

    from ekko.core.ports.external.metrics import MetricsPort
    from ekko.core.types import ModelDeploymentName
    from ekko.infrastructure.clients.llm_router import LLMRouter

_DEFAULT_MAX_TOKENS = MaxTokens(1024)
_DEFAULT_TEMPERATURE = Temperature(0.0)
_DEFAULT_SUMMARIZER_MODEL = "gpt-4o-mini"
_LLM_TIMEOUT_SECONDS = 30

_MESSAGE_ROLE_SYSTEM = "system"
_MESSAGE_ROLE_USER = "user"

_PROVIDER_PREFIXES = {
    LLMProvider.AZURE_OPENAI: "azure",
    LLMProvider.OPENAI: "openai",
    LLMProvider.ANTHROPIC: "anthropic",
    LLMProvider.COHERE: "cohere",
    LLMProvider.GOOGLE: "gemini",
}

_LITELLM_ERRORS = (
    litellm.exceptions.OpenAIError,
    litellm.exceptions.APIError,
    litellm.exceptions.BudgetExceededError,
)


class _LLMProviderConfig(Protocol):
    """Provider settings needed to build LiteLLM model arguments."""

    llm_provider: LLMProvider
    azure_openai_endpoint: str | None
    azure_openai_version: str
    azure_openai_key: SecretStr | None
    openai_api_key: SecretStr | None
    litellm_api_key: SecretStr | None
    litellm_api_base: str | None
    litellm_api_version: str | None


class _ChatConfig(_LLMProviderConfig, Protocol):
    """Configuration fields required by ChatClient."""

    llm_default_deployment: ModelDeploymentName | None
    llm_track_costs: bool


def _build_model_name(*, model: ModelDeploymentName, settings: _LLMProviderConfig) -> str:
    if "/" in model:
        return model

    provider_prefix = _PROVIDER_PREFIXES.get(settings.llm_provider)
    if provider_prefix is None:
        return model
    return f"{provider_prefix}/{model}"


def _extract_provider_prefix(model: ModelDeploymentName) -> str | None:
    provider_prefix, separator, _ = model.partition("/")
    return provider_prefix if separator else None


def _build_provider_kwargs(
    *,
    model: ModelDeploymentName,
    settings: _LLMProviderConfig,
) -> dict[str, str]:
    provider_prefix = _extract_provider_prefix(model)
    provider_name = provider_prefix or settings.llm_provider.value

    if provider_name in {"azure", LLMProvider.AZURE_OPENAI.value}:
        kwargs = {
            "api_version": settings.azure_openai_version,
        }
        if settings.azure_openai_endpoint:
            kwargs["api_base"] = settings.azure_openai_endpoint
        if settings.azure_openai_key:
            kwargs["api_key"] = settings.azure_openai_key.get_secret_value()
        return kwargs

    if provider_name == LLMProvider.OPENAI.value and settings.openai_api_key:
        kwargs = {"api_key": settings.openai_api_key.get_secret_value()}
        if settings.litellm_api_base:
            kwargs["api_base"] = settings.litellm_api_base
        if settings.litellm_api_version:
            kwargs["api_version"] = settings.litellm_api_version
        if settings.litellm_api_key:
            kwargs["api_key"] = settings.litellm_api_key.get_secret_value()
        return kwargs

    kwargs = {}
    if settings.litellm_api_key:
        kwargs["api_key"] = settings.litellm_api_key.get_secret_value()
    if settings.litellm_api_base:
        kwargs["api_base"] = settings.litellm_api_base
    if settings.litellm_api_version:
        kwargs["api_version"] = settings.litellm_api_version
    return kwargs


def _build_messages(*, system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
    return [
        {"role": _MESSAGE_ROLE_SYSTEM, "content": system_prompt},
        {"role": _MESSAGE_ROLE_USER, "content": user_prompt},
    ]


def _extract_content(response: litellm.ModelResponse) -> str:
    if not response.choices:
        raise LLMError("LLM returned no choices in response.")  # noqa: EM101

    content = response.choices[0].message.content
    if not isinstance(content, str) or not content:
        raise LLMError("LLM response message has no content.")  # noqa: EM101

    return content


@final
class ChatClient:
    """Provider-agnostic chat adapter with optional fallback routing."""

    def __init__(
        self,
        *,
        settings: _ChatConfig,
        router: LLMRouter | None = None,
        metrics_port: MetricsPort | None = None,
    ):
        """Initialize client dependencies.

        Args:
            settings: Typed LLM settings view.
            router: Cached LiteLLM Router for the configured default model.
            metrics_port: Provider-neutral request telemetry port.
        """
        self._settings = settings
        self._router = router
        self._metrics_port = metrics_port

    @classmethod
    def from_config(
        cls,
        config: _ChatConfig,
        *,
        router: LLMRouter | None = None,
        metrics_port: MetricsPort | None = None,
    ) -> Self:
        """Build the adapter from typed configuration and composed ports."""
        return cls(settings=config, router=router, metrics_port=metrics_port)

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
        resolved_model = self._resolve_model(model)
        model_name = _build_model_name(model=resolved_model, settings=self._settings)
        messages = _build_messages(system_prompt=system_prompt, user_prompt=user_prompt)
        start = time.perf_counter()
        succeeded = False

        try:
            response = self._complete(
                model_name=model_name,
                messages=messages,
                max_completion_tokens=max_completion_tokens,
                temperature=temperature,
                provider_kwargs=_build_provider_kwargs(
                    model=resolved_model,
                    settings=self._settings,
                ),
            )
            content = _extract_content(response)
            self._record_usage(operation="chat", response=response)
        except _LITELLM_ERRORS as exc:
            raise LLMError("LLM provider request failed.") from exc  # noqa: EM101
        else:
            succeeded = True
            return content
        finally:
            self._record_outcome(
                operation="chat",
                duration_seconds=time.perf_counter() - start,
                succeeded=succeeded,
            )

    def _complete(
        self,
        *,
        model_name: str,
        messages: list[dict[str, str]],
        max_completion_tokens: MaxTokens,
        temperature: Temperature,
        provider_kwargs: dict[str, str],
    ) -> litellm.ModelResponse:
        if self._router is not None and self._router.should_route(model_name):
            response = self._router.router.completion(
                model=model_name,
                messages=messages,
                stream=False,
                timeout=_LLM_TIMEOUT_SECONDS,
                max_tokens=int(max_completion_tokens),
                temperature=float(temperature),
            )
            if isinstance(response, litellm.CustomStreamWrapper):
                raise LLMError("LLM returned a stream for a non-streaming request.")  # noqa: EM101
            return response

        return self._complete_direct(
            model_name=model_name,
            messages=messages,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
            provider_kwargs=provider_kwargs,
        )

    @api_retry
    def _complete_direct(
        self,
        *,
        model_name: str,
        messages: list[dict[str, str]],
        max_completion_tokens: MaxTokens,
        temperature: Temperature,
        provider_kwargs: dict[str, str],
    ) -> litellm.ModelResponse:
        return litellm.completion(
            model=model_name,
            messages=messages,
            stream=False,
            timeout=_LLM_TIMEOUT_SECONDS,
            num_retries=0,
            max_tokens=int(max_completion_tokens),
            temperature=float(temperature),
            **provider_kwargs,
        )

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
        resolved_model = self._resolve_model(model)
        model_name = _build_model_name(model=resolved_model, settings=self._settings)
        messages = _build_messages(system_prompt=system_prompt, user_prompt=user_prompt)
        start = time.perf_counter()
        succeeded = False

        try:
            response = await self._acomplete(
                model_name=model_name,
                messages=messages,
                max_completion_tokens=max_completion_tokens,
                temperature=temperature,
                provider_kwargs=_build_provider_kwargs(
                    model=resolved_model,
                    settings=self._settings,
                ),
            )
            content = _extract_content(response)
            self._record_usage(operation="achat", response=response)
        except _LITELLM_ERRORS as exc:
            raise LLMError("LLM provider request failed.") from exc  # noqa: EM101
        else:
            succeeded = True
            return content
        finally:
            self._record_outcome(
                operation="achat",
                duration_seconds=time.perf_counter() - start,
                succeeded=succeeded,
            )

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
        """Complete a chat prompt into a validated response model."""
        resolved_model = self._resolve_model(model)
        model_name = _build_model_name(model=resolved_model, settings=self._settings)
        messages = _build_messages(system_prompt=system_prompt, user_prompt=user_prompt)
        start = time.perf_counter()
        succeeded = False

        try:
            response = await self._acomplete(
                model_name=model_name,
                messages=messages,
                max_completion_tokens=max_completion_tokens,
                temperature=temperature,
                provider_kwargs=_build_provider_kwargs(
                    model=resolved_model,
                    settings=self._settings,
                ),
                response_format=response_model,
            )
            content = _extract_content(response)
            result = response_model.model_validate_json(content)
            self._record_usage(operation="achat_structured", response=response)
        except _LITELLM_ERRORS as exc:
            raise LLMError("LLM provider request failed.") from exc  # noqa: EM101
        except ValidationError as exc:
            raise LLMError(
                f"LLM response does not match {response_model.__name__}."  # noqa: EM102
            ) from exc
        else:
            succeeded = True
            return result
        finally:
            self._record_outcome(
                operation="achat_structured",
                duration_seconds=time.perf_counter() - start,
                succeeded=succeeded,
            )

    async def _acomplete(
        self,
        *,
        model_name: str,
        messages: list[dict[str, str]],
        max_completion_tokens: MaxTokens,
        temperature: Temperature,
        provider_kwargs: dict[str, str],
        response_format: type[BaseModel] | None = None,
    ) -> litellm.ModelResponse:
        if self._router is not None and self._router.should_route(model_name):
            router_messages: list[litellm.types.llms.openai.AllMessageValues] = [
                {"role": "system", "content": messages[0]["content"]},
                {"role": "user", "content": messages[1]["content"]},
            ]
            if response_format is None:
                return await self._router.router.acompletion(
                    model=model_name,
                    messages=router_messages,
                    stream=False,
                    timeout=_LLM_TIMEOUT_SECONDS,
                    max_tokens=int(max_completion_tokens),
                    temperature=float(temperature),
                )
            return await self._router.router.acompletion(
                model=model_name,
                messages=router_messages,
                stream=False,
                timeout=_LLM_TIMEOUT_SECONDS,
                max_tokens=int(max_completion_tokens),
                temperature=float(temperature),
                response_format=response_format,
            )

        return await self._acomplete_direct(
            model_name=model_name,
            messages=messages,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
            provider_kwargs=provider_kwargs,
            response_format=response_format,
        )

    @api_retry
    async def _acomplete_direct(
        self,
        *,
        model_name: str,
        messages: list[dict[str, str]],
        max_completion_tokens: MaxTokens,
        temperature: Temperature,
        provider_kwargs: dict[str, str],
        response_format: type[BaseModel] | None,
    ) -> litellm.ModelResponse:
        if response_format is None:
            return await litellm.acompletion(
                model=model_name,
                messages=messages,
                stream=False,
                timeout=_LLM_TIMEOUT_SECONDS,
                num_retries=0,
                max_tokens=int(max_completion_tokens),
                temperature=float(temperature),
                **provider_kwargs,
            )
        return await litellm.acompletion(
            model=model_name,
            messages=messages,
            stream=False,
            timeout=_LLM_TIMEOUT_SECONDS,
            num_retries=0,
            max_tokens=int(max_completion_tokens),
            temperature=float(temperature),
            response_format=response_format,
            **provider_kwargs,
        )

    def _resolve_model(self, requested_model: ModelDeploymentName) -> ModelDeploymentName:
        default_model = self._settings.llm_default_deployment
        if default_model and requested_model == _DEFAULT_SUMMARIZER_MODEL:
            return default_model
        return requested_model

    def _record_outcome(
        self,
        *,
        operation: str,
        duration_seconds: float,
        succeeded: bool,
    ) -> None:
        if self._metrics_port is None:
            return

        if succeeded:
            self._metrics_port.record_request_success(
                operation=operation,
                duration_seconds=duration_seconds,
            )
        else:
            self._metrics_port.record_request_failure(
                operation=operation,
                duration_seconds=duration_seconds,
            )

    def _record_usage(
        self,
        *,
        operation: str,
        response: litellm.ModelResponse,
    ) -> None:
        if not self._settings.llm_track_costs or self._metrics_port is None:
            return

        usage: object = getattr(response, "usage", None)
        if not isinstance(usage, litellm.types.utils.Usage):
            return

        self._metrics_port.record_token_usage(
            operation=operation,
            input_tokens=usage.prompt_tokens or 0,
            output_tokens=usage.completion_tokens or 0,
        )
        cost = litellm.completion_cost(response)
        if cost > 0:
            self._metrics_port.record_cost(operation=operation, cost_usd=cost)
