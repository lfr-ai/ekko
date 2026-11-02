"""LiteLLM Router factory for explicitly configured fallbacks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Self, final

import litellm

from ekko.infrastructure.clients.chat import (
    _DEFAULT_SUMMARIZER_MODEL,
    _build_model_name,
    _build_provider_kwargs,
    _LLMProviderConfig,
)

if TYPE_CHECKING:
    from ekko.core.types import ModelDeploymentName

_ROUTER_NUM_RETRIES = 2


class _LLMRouterConfig(_LLMProviderConfig, Protocol):
    """Configuration fields required to construct the Router."""

    llm_default_deployment: ModelDeploymentName | None
    llm_fallback_deployments: list[ModelDeploymentName] | None


@final
class LLMRouter:
    """Cached Router that maps one primary deployment to ordered fallbacks."""

    def __init__(
        self,
        *,
        router: litellm.Router,
        primary_model_name: ModelDeploymentName,
    ):
        """Initialize the configured Router.

        Args:
            router (litellm.Router): Cached LiteLLM Router instance.
            primary_model_name (ModelDeploymentName): Primary deployment group.
        """
        self._router = router
        self._primary_model_name = primary_model_name

    @classmethod
    def from_config(cls, config: _LLMRouterConfig, /) -> Self | None:
        """Build a Router when one or more fallback deployments are configured."""
        fallback_deployments = config.llm_fallback_deployments or []
        if not fallback_deployments:
            return None

        primary_deployment = config.llm_default_deployment or _DEFAULT_SUMMARIZER_MODEL
        primary_model_name = _build_model_name(
            model=primary_deployment,
            settings=config,
        )
        seen_model_names = {primary_model_name}
        fallback_model_names: list[str] = []
        model_list = [
            {
                "model_name": primary_model_name,
                "litellm_params": {
                    "model": primary_model_name,
                    **_build_provider_kwargs(
                        model=primary_deployment,
                        settings=config,
                    ),
                },
            }
        ]

        for deployment in fallback_deployments:
            model_name = _build_model_name(model=deployment, settings=config)
            if model_name in seen_model_names:
                raise ValueError(
                    "Fallback deployments must not duplicate another model group."  # noqa: EM101
                )

            seen_model_names.add(model_name)
            fallback_model_names.append(model_name)
            model_list.append(
                {
                    "model_name": model_name,
                    "litellm_params": {
                        "model": model_name,
                        **_build_provider_kwargs(
                            model=deployment,
                            settings=config,
                        ),
                    },
                }
            )

        if not fallback_model_names:
            raise ValueError(
                "Fallback configuration must include another deployment."  # noqa: EM101
            )

        router = litellm.Router(
            model_list=model_list,
            fallbacks=[{primary_model_name: fallback_model_names}],
            num_retries=_ROUTER_NUM_RETRIES,
        )
        return cls(router=router, primary_model_name=primary_model_name)

    @property
    def router(self) -> litellm.Router:
        """Cached LiteLLM Router instance."""
        return self._router

    def should_route(self, model_name: ModelDeploymentName) -> bool:
        """Check whether a model name is the configured primary deployment."""
        return model_name == self._primary_model_name
