"""Filesystem client for the versioned PromptRegistryPort."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Self, final

from ekko.ai.prompts.registry import PromptRegistryError as _RegistryError
from ekko.ai.prompts.registry import get_prompt_text
from ekko.core.enums.ai import Prompt  # noqa: TC001 — used at runtime in load_prompt parameter and cache key
from ekko.core.ports.external.prompt_registry import PromptRegistryError

if TYPE_CHECKING:
    from pathlib import Path


class _PromptRegistryConfig(Protocol):
    """Configuration fields required by the prompt registry client."""

    prompt_dir_path: Path
    prompt_version: str | None
    prompt_version_set: str
    prompt_auto_provision: bool


@final
class PromptRegistryClient:
    """Versioned filesystem implementation of PromptRegistryPort."""

    def __init__(self, *, settings: _PromptRegistryConfig):
        """Initialize client with application settings.

        Args:
            settings: Application configuration containing prompt directory
                and versioning settings.
        """
        self._settings = settings
        self._cache: dict[Prompt, str] = {}

    @classmethod
    def from_config(cls, config: _PromptRegistryConfig) -> Self:
        """Create client instance from application configuration.

        Args:
            config: Configuration instance containing prompt settings.

        Returns:
            Configured client instance.
        """
        return cls(settings=config)

    def load_prompt(self, prompt: Prompt) -> str:
        """Load prompt template text for the given prompt identifier.

        Args:
            prompt: Prompt template identifier.

        Returns:
            Resolved prompt template text.

        Raises:
            PromptRegistryError: If the prompt is not found or retrieval fails.
        """
        if prompt in self._cache:
            return self._cache[prompt]

        try:
            text = get_prompt_text(prompt.value, settings=self._settings)
        except _RegistryError as exc:
            raise PromptRegistryError(str(exc)) from exc

        self._cache[prompt] = text
        return text
