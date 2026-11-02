"""Prompt catalog DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class PromptDTO:
    """Prompt catalog entry."""

    key: str


@dataclass(frozen=True, kw_only=True, slots=True)
class PromptCatalogDTO:
    """Active prompt catalog."""

    version_set: str
    prompts: tuple[PromptDTO, ...]
