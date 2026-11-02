"""LLM provider, credential, and RAG settings."""

from pydantic import SecretStr

from ekko.config.enums import ChatModel, LLMProvider
from ekko.config.settings._shared import ConfiguredSettings


class LLMSettings(ConfiguredSettings):
    """LLM provider credentials, model routing, and PII policy profile.

    Settings:
        llm_provider: LLM provider enum (openai, azure_openai, anthropic, etc.)
        llm_default_deployment: Default model deployment name for summarization.
        llm_fallback_deployments: Optional list of fallback model deployments for routing.
        openai_api_key: OpenAI API key for direct OpenAI provider.
        azure_openai_endpoint: Azure OpenAI endpoint URL.
        azure_openai_version: Azure OpenAI API version.
        azure_openai_key: Azure OpenAI API key.
        litellm_api_key: Generic LiteLLM API key for provider-qualified model names.
        litellm_api_base: Generic LiteLLM API base URL for provider-qualified names.
        litellm_api_version: Generic LiteLLM API version for provider-qualified names.
        llm_track_costs: Enable optional cost tracking for LLM requests (default: False).
        rag_embedding_model: RAG embedding model identifier.
        rag_llm_model: RAG LLM model identifier.
        pii_policy_profile: PII anonymization policy profile name.
    """

    llm_provider: LLMProvider = LLMProvider.OPENAI
    llm_default_deployment: str | None = None
    llm_fallback_deployments: list[str] | None = None
    openai_api_key: SecretStr | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_version: str = "2025-02-01-preview"
    azure_openai_key: SecretStr | None = None
    litellm_api_key: SecretStr | None = None
    litellm_api_base: str | None = None
    litellm_api_version: str | None = None
    llm_track_costs: bool = False
    rag_embedding_model: str = "text-embedding-3-small"
    rag_llm_model: str = ChatModel.GPT_4O
    pii_policy_profile: str = "standard"
