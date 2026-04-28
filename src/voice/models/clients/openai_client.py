"""Compatibility wrapper for the OpenAI client.

This module kept for backwards compatibility; prefer using the
infrastructure adapter at `voice.infrastructure.openai.openai_client.AzureOpenAIClient`
and the application service `voice.application.services.chat_service.ChatService`.
"""

from voice.config.config import Config
from voice.infrastructure.openai.openai_client import AzureOpenAIClient


def create_client(cfg: Config | None = None) -> AzureOpenAIClient:
    """Create an AzureOpenAIClient instance.

    Kept as a convenience factory for older call sites.
    """
    if cfg is None:
        cfg = Config()
    return AzureOpenAIClient(cfg)
