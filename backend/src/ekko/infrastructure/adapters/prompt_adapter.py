"""Infrastructure adapter implementing PromptProvider via the AI prompt registry."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ekko.ai.prompts import PromptRegistryError, get_prompt_text
from ekko.core.interfaces.services.prompts import PromptProviderError

if TYPE_CHECKING:
    from ekko.config.settings import BaseAppConfig


class RegistryPromptProvider:
    """Adapts the file-backed prompt registry to the PromptProvider protocol."""

    def __init__(self, settings: BaseAppConfig) -> None:
        self._settings = settings

    def get_prompt_text(self, prompt_key: str) -> str:
        """Return prompt text from the registry.

        Raises:
            PromptProviderError: If key is unknown or retrieval fails.
        """
        try:
            return get_prompt_text(prompt_key, settings=self._settings)
        except PromptRegistryError as exc:
            raise PromptProviderError(str(exc)) from exc
