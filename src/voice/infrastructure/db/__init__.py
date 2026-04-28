"""Database helpers and session factory for async SQLAlchemy (2.x).

This module exposes utilities to create an async engine, the async session
factory and a declarative base for models.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def create_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    return create_async_engine(database_url, echo=echo, future=True)


def create_session_factory(engine: AsyncEngine, expire_on_commit: bool = False) -> sessionmaker:
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=expire_on_commit)


__all__ = ["Base", "create_engine", "create_session_factory", "AsyncSession", "AsyncEngine"]
