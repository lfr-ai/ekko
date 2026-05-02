"""Database helpers and session factory for async SQLAlchemy (2.x).

This module exposes utilities to create an async engine, the async session
factory and a declarative base for models.
"""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .base import Base


def _set_sqlite_pragmas(dbapi_conn, _connection_record) -> None:
    """Enable WAL mode and foreign keys for every SQLite connection."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.close()


def create_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    engine = create_async_engine(
        database_url,
        echo=echo,
        future=True,
        connect_args={"check_same_thread": False},
    )
    event.listen(engine.sync_engine, "connect", _set_sqlite_pragmas)
    return engine


def create_session_factory(
    engine: AsyncEngine,
    expire_on_commit: bool = False,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=expire_on_commit)


__all__ = ["AsyncEngine", "AsyncSession", "Base", "create_engine", "create_session_factory"]
