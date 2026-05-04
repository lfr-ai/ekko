"""Integration conftest."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.fixture
def integration_settings():
    """Settings configured for integration testing."""
    from ekko.config.settings import BaseAppConfig
    from ekko.core.enums import Environment

    return BaseAppConfig(environment=Environment.TEST, debug=False)


@pytest.fixture
async def test_db_engine():
    """Create a temporary SQLite engine for integration testing."""
    from sqlalchemy.ext.asyncio import create_async_engine

    # Import models to ensure they're registered with Base.metadata
    from ekko.infrastructure.db import models as _  # noqa: F401
    from ekko.infrastructure.db.base import Base

    # Create temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        future=True,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()
    db_path.unlink(missing_ok=True)


@pytest.fixture
async def test_db_session(test_db_engine: AsyncEngine):
    """Create a test database session."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    session_factory = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()
