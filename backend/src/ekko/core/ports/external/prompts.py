"""Protocol for prompt text retrieval."""

from __future__ import annotations

from typing import Protocol


class PromptProvider(Protocol):
    """Port for retrieving prompt templates by key."""

    def get_prompt_text(self, prompt_key: str) -> str:
        """Return the prompt template text for the given key.

        Raises:
            PromptProviderError: If the key is not found or retrieval fails.
        """
        ...


class PromptProviderError(Exception):
    """Raised when prompt retrieval fails."""
