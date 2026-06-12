"""Base application configuration.

All environment-specific settings classes inherit from :class:`BaseAppConfig`.
"""

from __future__ import annotations

import logging
import sys
from functools import cached_property
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from ekko.config.enums import ChatModel, DatabaseBackend, Environment, LLMProvider
from ekko.config.runtime import ROOT_DIR


class BaseAppConfig(BaseSettings):
    """Typed application settings read from environment variables.

    Uses the ``EKKO_`` env prefix (e.g. ``EKKO_OPENAI_API_KEY``).
    """

    model_config = SettingsConfigDict(
        env_prefix="EKKO_",
        env_file_encoding="utf-8",
        frozen=True,
        extra="ignore",
    )

    # ── General ───────────────────────────────────────────────
    environment: Environment = Environment.LOCAL
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
    log_level: str = str(logging.INFO)
    sentry_dsn: str | None = None

    # ── LLM / OpenAI ─────────────────────────────────────────
    llm_provider: LLMProvider = LLMProvider.OPENAI
    llm_default_deployment: str | None = None
    openai_api_key: SecretStr | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_version: str = "2025-02-01-preview"
    azure_openai_key: SecretStr | None = None

    # ── RAG ───────────────────────────────────────────────────
    rag_embedding_model: str = "text-embedding-3-small"
    rag_llm_model: str = ChatModel.GPT_4O

    # ── Database ───────────────────────────────────────────────
    database_backend: DatabaseBackend = DatabaseBackend.SQLITE
    database_path: str = "./ekko.db"
    postgresql_host: str = "127.0.0.1"
    postgresql_port: int = 5432
    postgresql_name: str = "ekko"
    postgresql_user: str = "postgres"
    postgresql_password: SecretStr | None = None
    postgresql_sslmode: str = "prefer"
    postgresql_async_database_url_override: str | None = None
    postgresql_sync_database_url_override: str | None = None

    # ── Database (DuckDB analytics over SQLite) ───────────────
    duckdb_enabled: bool = False
    duckdb_database_path: str = "./ekko_analytics.duckdb"

    # ── Paths ─────────────────────────────────────────────────
    root_dir_path: Path = ROOT_DIR
    src_dir_path: Path = root_dir_path / "src"
    package_dir_path: Path = src_dir_path / "ekko"
    logs_dir_path: Path = Path("./logs")
    prompt_dir_path: Path = package_dir_path / "ai" / "prompts"
    prompt_version: str | None = None
    prompt_auto_provision: bool = True
    interaction_dir_path: Path = package_dir_path / "interaction"

    # ── Audio / IPC ───────────────────────────────────────────
    disable_audio: bool = False
    audio_streamer_tcp_port: int = 6600
    audio_streamer_tcp_server_module_path: str = "ekko.infrastructure.audio_streamer.audio_streamer_tcp_server"
    audio_format: int = 8  # pyaudiowpatch.paInt16
    audio_frames_per_buffer: int = 1024
    audio_channels: int = 2
    audio_sample_rate: int = 48000

    # ── Azure Speech Services (STT) ───────────────────────────
    azure_speech_key: SecretStr | None = None
    azure_speech_region: str = "northeurope"
    azure_speech_language: str = "da-DK"
    azure_speech_recognition_mode: str = "continuous"

    # ── Legacy STT Config (deprecated, kept for backward compat)
    stt_device: str = "cpu"
    stt_compute_type: str = "default"

    # ── Misc constants ────────────────────────────────────────
    sleep_delay_seconds: float = 0.1
    wait_timeout_seconds: int = 2
    max_read_bytes: int = 100

    # ── Computed ──────────────────────────────────────────────
    @cached_property
    def _resolved_db_path(self) -> Path:
        """Resolve the database file path, creating parent dirs as needed."""
        if getattr(sys, "frozen", False):
            import os

            base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            db_path = base / "ekko" / "ekko.db"
        else:
            db_path = Path(self.database_path).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path

    @cached_property
    def _resolved_duckdb_path(self) -> Path:
        """Resolve the DuckDB file path, creating parent dirs as needed."""
        duckdb_path = Path(self.duckdb_database_path).resolve()
        duckdb_path.parent.mkdir(parents=True, exist_ok=True)
        return duckdb_path

    @property
    def resolved_db_path(self) -> Path:
        """Public accessor for the resolved SQLite path."""
        return self._resolved_db_path

    @property
    def resolved_duckdb_path(self) -> Path:
        """Public accessor for the resolved DuckDB path."""
        return self._resolved_duckdb_path

    @cached_property
    def database_url(self) -> str:
        """Async DSN for SQLAlchemy async engines based on configured backend."""
        if self.database_backend == DatabaseBackend.SQLITE:
            return f"sqlite+aiosqlite:///{self._resolved_db_path}"

        return self.postgresql_async_database_url

    @cached_property
    def database_sync_url(self) -> str:
        """Synchronous DSN for Alembic migrations based on configured backend."""
        if self.database_backend == DatabaseBackend.SQLITE:
            return f"sqlite:///{self._resolved_db_path}"

        return self.postgresql_sync_database_url

    @cached_property
    def postgresql_async_database_url(self) -> str:
        """Async PostgreSQL DSN used by SQLAlchemy async engines."""
        if self.postgresql_async_database_url_override:
            return self.postgresql_async_database_url_override
        return self._build_postgresql_url(async_mode=True)

    @cached_property
    def postgresql_sync_database_url(self) -> str:
        """Sync PostgreSQL DSN used by Alembic migration engines."""
        if self.postgresql_sync_database_url_override:
            return self.postgresql_sync_database_url_override
        return self._build_postgresql_url(async_mode=False)

    def _build_postgresql_url(self, *, async_mode: bool) -> str:
        """Build PostgreSQL SQLAlchemy URL from structured settings values."""
        driver = "postgresql+asyncpg" if async_mode else "postgresql+psycopg"
        user = quote_plus(self.postgresql_user)
        password = self.postgresql_password.get_secret_value() if self.postgresql_password else ""
        password_segment = f":{quote_plus(password)}" if password else ""

        return (
            f"{driver}://{user}{password_segment}@"
            f"{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_name}"
            f"?sslmode={self.postgresql_sslmode}"
        )
