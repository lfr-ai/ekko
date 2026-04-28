"""Async SQLAlchemy engine and session factory."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from voice.config.settings import get_settings


def create_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(settings.postgresql_async_url, future=True, echo=False)


def create_session_factory(engine: AsyncEngine | None = None) -> sessionmaker:
    if engine is None:
        engine = create_engine()
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
