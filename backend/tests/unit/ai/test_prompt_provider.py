"""Tests for prompt provider adapter."""

import pytest

from ekko.ai.prompts.provider import RegistryPromptProvider
from ekko.core.ports.external.prompts import PromptProviderError


class TestRegistryPromptProvider:
    def test_get_known_prompt(self):
        """Provider should return text for known prompt keys."""
        from ekko.config.settings import get_settings

        settings = get_settings()
        provider = RegistryPromptProvider(settings=settings)
        # conversational_system is a known prompt in the registry
        text = provider.get_prompt_text("conversational_system")
        assert isinstance(text, str)
        assert len(text) > 0

    def test_get_unknown_prompt_raises(self):
        """Unknown keys should raise PromptProviderError."""
        from ekko.config.settings import get_settings

        settings = get_settings()
        provider = RegistryPromptProvider(settings=settings)
        with pytest.raises(PromptProviderError):
            provider.get_prompt_text("nonexistent_key_xyz_12345")
