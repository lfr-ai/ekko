"""Tests for PromptRegistryClient."""

from enum import StrEnum

import pytest

prompt_registry_module = pytest.importorskip("ekko.infrastructure.clients.prompt_registry")
PromptRegistryClient = prompt_registry_module.PromptRegistryClient


class PromptId(StrEnum):
    """Local prompt identifiers used to avoid coupling to enum re-exports."""

    CONVERSATIONAL_SYSTEM = "conversational_system"


class TestPromptRegistryClient:
    def test_load_known_prompt(self):
        """Client should return text for known prompt identifiers."""
        from ekko.config.settings import get_settings

        settings = get_settings()
        client = PromptRegistryClient.from_config(settings)
        text = client.load_prompt(PromptId.CONVERSATIONAL_SYSTEM)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_load_prompt_caches(self):
        """Subsequent loads for the same prompt return cached text."""
        from ekko.config.settings import get_settings

        settings = get_settings()
        client = PromptRegistryClient.from_config(settings)
        text1 = client.load_prompt(PromptId.CONVERSATIONAL_SYSTEM)
        text2 = client.load_prompt(PromptId.CONVERSATIONAL_SYSTEM)
        assert text1 is text2
