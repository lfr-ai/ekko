"""Base application configuration.

All environment-specific settings classes inherit from :class:`BaseAppConfig`.
"""

from __future__ import annotations

import logging
from functools import cached_property
from pathlib import Path

from pydantic import SecretStr

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # pragma: no cover

    class BaseSettings:  # type: ignore[no-redef]
        def __init__(self, **kwargs) -> None: ...

    class SettingsConfigDict(dict):  # type: ignore[no-redef]
        pass


from ekko.core.enums import ChatModel, Environment, LLMProvider


class BaseAppConfig(BaseSettings):
    """Typed application settings read from environment variables.

    Uses the ``EKKO_`` env prefix (e.g. ``EKKO_OPENAI_API_KEY``).
    """

    model_config = SettingsConfigDict(
        env_prefix="EKKO_",
        frozen=True,
        extra="ignore",
    )

    # ── General ───────────────────────────────────────────────
    environment: Environment = Environment.LOCAL
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = str(logging.INFO)

    # ── LLM / OpenAI ─────────────────────────────────────────
    llm_provider: LLMProvider = LLMProvider.OPENAI
    llm_default_deployment: str | None = None
    openai_api_key: SecretStr | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_version: str = "2025-02-01-preview"
    azure_openai_key: SecretStr | None = None

    # ── Auth / JWT ────────────────────────────────────────────
    jwt_secret_key: SecretStr = SecretStr("change-me-ekko-jwt-secret")
    jwt_expire_minutes: int = 30

    # ── RAG ───────────────────────────────────────────────────
    rag_embedding_model: str = "text-embedding-3-small"
    rag_llm_model: str = ChatModel.GPT_4O

    # ── Database ──────────────────────────────────────────────
    postgresql_user: str = "postgres"
    postgresql_host: str = "127.0.0.1"
    postgresql_port: int = 5432
    postgresql_name: str = "ekko"
    postgresql_password: SecretStr | None = None

    # ── Paths ─────────────────────────────────────────────────
    root_dir_path: Path = Path(__file__).resolve().parents[4]
    src_dir_path: Path = root_dir_path / "src"
    package_dir_path: Path = src_dir_path / "ekko"
    logs_dir_path: Path = Path("./logs")
    prompt_dir_path: Path = package_dir_path / "ai" / "prompts"
    interaction_dir_path: Path = package_dir_path / "interaction"

    # ── Audio / IPC ───────────────────────────────────────────
    audio_streamer_tcp_port: int = 6600
    audio_streamer_tcp_server_module_path: str = "ekko.infrastructure.audio_streamer.audio_streamer_tcp_server"
    audio_format: int = 8  # pyaudiowpatch.paInt16
    audio_frames_per_buffer: int = 1024
    audio_channels: int = 2
    audio_sample_rate: int = 48000
    stt_device: str = "cpu"
    stt_compute_type: str = "default"

    # ── Misc constants ────────────────────────────────────────
    sleep_delay_seconds: float = 0.1
    wait_timeout_seconds: int = 2
    max_read_bytes: int = 100

    # ── Computed ──────────────────────────────────────────────
    @cached_property
    def postgresql_url(self) -> str:
        """Synchronous PostgreSQL DSN."""
        pw = self.postgresql_password.get_secret_value() if self.postgresql_password else ""
        auth = f"{self.postgresql_user}:{pw}" if pw else self.postgresql_user
        return f"postgresql://{auth}@{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_name}"

    @cached_property
    def postgresql_async_url(self) -> str:
        """Asyncpg-compatible DSN for SQLAlchemy async engines."""
        pw = self.postgresql_password.get_secret_value() if self.postgresql_password else ""
        auth = f"{self.postgresql_user}:{pw}" if pw else self.postgresql_user
        return f"postgresql+asyncpg://{auth}@{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_name}"
