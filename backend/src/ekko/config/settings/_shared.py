"""Shared base for the settings facets carrying the ``EKKO_`` environment binding."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfiguredSettings(BaseSettings):
    """Shared base settings facet.

    Every settings facet inherits from this base so they read from the same
    ``EKKO_`` environment prefix and share one immutable ``model_config``.
    """

    model_config = SettingsConfigDict(
        env_prefix="EKKO_",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )
