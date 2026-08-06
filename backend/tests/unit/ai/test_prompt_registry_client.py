"""Tests for PromptRegistryClient."""

from ekko.core.enums.ai import Prompt
from ekko.infrastructure.clients.prompt_registry import PromptRegistryClient


class TestPromptRegistryClient:
    def test_load_known_prompt(self):
        """Client should return text for known prompt identifiers."""
        from ekko.config.settings import get_settings

        settings = get_settings()
        client = PromptRegistryClient.from_config(settings)
        text = client.load_prompt(Prompt.CONVERSATIONAL_SYSTEM)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_load_prompt_caches(self):
        """Subsequent loads for the same prompt return cached text."""
        from ekko.config.settings import get_settings

        settings = get_settings()
        client = PromptRegistryClient.from_config(settings)
        text1 = client.load_prompt(Prompt.CONVERSATIONAL_SYSTEM)
        text2 = client.load_prompt(Prompt.CONVERSATIONAL_SYSTEM)
        assert text1 is text2
