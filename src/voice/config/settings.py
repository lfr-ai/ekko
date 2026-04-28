"""Central application settings for the voice project.

Expose a single, well-documented :class:`AppSettings` (pydantic BaseSettings)
and a module-level :data:`SETTINGS` convenience instance.
"""

from __future__ import annotations

import logging
from functools import cached_property
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from pydantic import SecretStr

if TYPE_CHECKING:
    # For static type checking prefer the real types from pydantic-settings
    from pydantic_settings import BaseSettings, SettingsConfigDict
else:
    try:
        # pydantic v2+ split package
        from pydantic_settings import BaseSettings, SettingsConfigDict
    except Exception:
        # Runtime fallback: provide minimal shims so the module can be
        # imported in environments without pydantic-settings installed.
        class BaseSettings:  # type: ignore[misc]
            def __init__(self, *args, **kwargs):  # pragma: no cover - shim
                return None

        class SettingsConfigDict(dict):  # pragma: no cover - shim
            """Lightweight compatibility wrapper used when pydantic-settings
            is not available in the environment (tests/local dev).
            """
            pass

from voice.core.enums import Environment, LLMProvider


class AppSettings(BaseSettings):
    """Typed application settings read from environment variables.

    Uses the ``VOICE_`` env prefix by default (e.g. ``VOICE_OPENAI_API_KEY``).
    """

    model_config = SettingsConfigDict(env_prefix="VOICE_", frozen=True, extra="ignore")

    # General
    environment: Environment = Environment.LOCAL
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: int = logging.INFO

    # LLM / OpenAI settings
    llm_provider: LLMProvider = LLMProvider.OPENAI
    llm_default_deployment: Optional[str] = None
    openai_api_key: Optional[SecretStr] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_version: str = "2025-02-01-preview"
    azure_openai_key: Optional[SecretStr] = None

    # RAG defaults
    rag_embedding_model: str = "text-embedding-3-small"
    rag_llm_model: str = "gpt-4o"

    # Database (optional)
    postgresql_user: str = "postgres"
    postgresql_host: str = "127.0.0.1"
    postgresql_port: int = 5432
    postgresql_name: str = "voice"
    postgresql_password: Optional[SecretStr] = None

    # Paths
    logs_dir_path: Path = Path("./logs")

    @cached_property
    def postgresql_url(self) -> str:
        if not self.postgresql_password:
            return f"postgresql://{self.postgresql_user}@{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_name}"
        pw = self.postgresql_password.get_secret_value()
        return f"postgresql://{self.postgresql_user}:{pw}@{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_name}"

    @cached_property
    def postgresql_async_url(self) -> str:
        """Return an asyncpg-compatible DSN for SQLAlchemy async engines."""
        if not self.postgresql_password:
            return f"postgresql+asyncpg://{self.postgresql_user}@{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_name}"
        pw = self.postgresql_password.get_secret_value()
        return f"postgresql+asyncpg://{self.postgresql_user}:{pw}@{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_name}"


_CACHED_SETTINGS: "AppSettings" | None = None


def get_settings() -> AppSettings:
    """Return a cached AppSettings instance.

    Use the accessor in tests when mutating environment variables to avoid
    a module-level SETTINGS singleton being created before env is adjusted.
    """
    global _CACHED_SETTINGS
    if _CACHED_SETTINGS is None:
        _CACHED_SETTINGS = AppSettings()
    return _CACHED_SETTINGS


# Module-level convenience instance
SETTINGS = get_settings()

# Backwards compatible alias
Settings = AppSettings

__all__ = ["AppSettings", "get_settings", "SETTINGS", "Settings"]
