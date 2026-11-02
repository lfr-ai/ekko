"""Prompt registry versioning settings."""

from ekko.config.settings._shared import ConfiguredSettings


class PromptSettings(ConfiguredSettings):
    """Prompt version pinning and provisioning settings."""

    prompt_version: str | None = None
    prompt_version_set: str = "experimental"
    prompt_auto_provision: bool = True
