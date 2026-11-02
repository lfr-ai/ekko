"""Prompt registry, versioning, and provisioning utilities.

The low-level registry functions live here.  New code should prefer the
``Prompt`` enum (``ekko.core.enums.Prompt``) and the
``PromptRegistryPort`` / ``PromptRegistryClient`` for type-safe prompt
loading.
"""

from ekko.ai.prompts.registry import (
    PromptRegistryError,
    PromptVersionInfo,
    get_active_prompt_version,
    get_active_prompt_versions,
    get_prompt_text,
    get_prompt_version_info,
    get_prompt_versions,
    provision_all_prompts,
    provision_prompt,
)

__all__ = [
    "PromptRegistryError",
    "PromptVersionInfo",
    "get_active_prompt_version",
    "get_active_prompt_versions",
    "get_prompt_text",
    "get_prompt_version_info",
    "get_prompt_versions",
    "provision_all_prompts",
    "provision_prompt",
]
