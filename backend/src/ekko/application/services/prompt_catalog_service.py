"""Application service for browsing the active prompt catalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from ekko.application.dtos import PromptCatalogDTO, PromptDTO
from ekko.core.enums import Prompt

if TYPE_CHECKING:
    from ekko.core.ports import PromptRegistryPort


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class PromptCatalogService:
    """Expose active prompt templates as one read-only catalog."""

    prompt_registry: PromptRegistryPort
    version_set: str

    def get_catalog(self) -> PromptCatalogDTO:
        """Build the active prompt catalog."""
        prompts = tuple(PromptDTO(key=prompt.value) for prompt in Prompt)
        return PromptCatalogDTO(version_set=self.version_set, prompts=prompts)

    def get_content(self, key: str) -> str:
        """Load one prompt template by catalog key."""
        return self.prompt_registry.load_prompt(Prompt(key))
