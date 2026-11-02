"""Database backend and derived connection URL settings."""

from __future__ import annotations

import sys
from functools import cached_property
from pathlib import Path

from ekko.config.enums import DatabaseBackend
from ekko.config.settings._shared import ConfiguredSettings


class DatabaseSettings(ConfiguredSettings):
    """Database backend selection and derived SQLite connection URLs."""

    database_backend: DatabaseBackend = DatabaseBackend.SQLITE
    database_path: str = "./ekko.db"

    @cached_property
    def resolved_db_path(self) -> Path:
        """Filesystem path to the SQLite database, with parent directories ensured."""
        if getattr(sys, "frozen", False):
            import os

            base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            db_path = base / "ekko" / "ekko.db"
        else:
            db_path = Path(self.database_path).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path

    @cached_property
    def database_url(self) -> str:
        """Async SQLite DSN for SQLAlchemy async engines."""
        return f"sqlite+aiosqlite:///{self.resolved_db_path}"

    @cached_property
    def database_sync_url(self) -> str:
        """Synchronous SQLite DSN for Alembic migrations."""
        return f"sqlite:///{self.resolved_db_path}"
