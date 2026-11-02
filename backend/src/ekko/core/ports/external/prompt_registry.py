"""Prompt registry port for versioned prompt template loading."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ekko.core.enums import Prompt  # noqa: TC001 — used at runtime in protocol method signature


@runtime_checkable
class PromptRegistryPort(Protocol):
    """Port for loading versioned prompt templates by key."""

    def load_prompt(self, prompt: Prompt) -> str:
        """Load the prompt template text for the given prompt identifier.

        Args:
            prompt: Prompt template identifier.

        Returns:
            Resolved prompt template text.

        Raises:
            PromptRegistryError: If the prompt is not found or retrieval fails.
        """
        ...


class PromptRegistryError(Exception):
    """Prompt registry operation failure."""
