"""Async SQLAlchemy engine and session factory."""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from ekko.config.settings import get_settings


def _set_sqlite_pragmas(dbapi_conn, _connection_record) -> None:
    """Enable WAL mode and foreign keys for every SQLite connection."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.close()


def _is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith(("sqlite+", "sqlite://"))


def create_engine() -> AsyncEngine:
    settings = get_settings()
    database_url = settings.database_url
    connect_args: dict[str, bool] = {"check_same_thread": False} if _is_sqlite_url(database_url) else {}

    engine = create_async_engine(
        database_url,
        future=True,
        echo=False,
        connect_args=connect_args,
    )
    if _is_sqlite_url(database_url):
        event.listen(engine.sync_engine, "connect", _set_sqlite_pragmas)
    return engine


def create_session_factory(engine: AsyncEngine | None = None) -> async_sessionmaker[AsyncSession]:
    if engine is None:
        engine = create_engine()
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
