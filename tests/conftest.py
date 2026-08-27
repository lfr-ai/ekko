"""Root test configuration for repository-level test suites.

Provides deterministic environment setup and shared SQLite-backed database
fixtures used by integration and end-to-end tests.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

_TEST_DATABASE_URL = "sqlite+aiosqlite://"


def _ensure_backend_src_on_path() -> None:
    """Ensure backend source directory is importable in test sessions."""
    backend_src = Path(__file__).resolve().parents[1] / "backend" / "src"
    backend_src_str = str(backend_src)
    if backend_src_str not in sys.path:
        sys.path.insert(0, backend_src_str)


_ensure_backend_src_on_path()


@pytest.fixture(scope="session", autouse=True)
def _test_environment() -> Generator[None]:
    """Force deterministic environment for all root tests."""
    from ekko.config.runtime import get_config

    previous_environment = os.environ.get("EKKO_ENVIRONMENT")
    previous_disable_audio = os.environ.get("EKKO_DISABLE_AUDIO")

    os.environ["EKKO_ENVIRONMENT"] = "test"
    os.environ["EKKO_DISABLE_AUDIO"] = "true"
    get_config.cache_clear()

    yield

    get_config.cache_clear()
    if previous_environment is None:
        os.environ.pop("EKKO_ENVIRONMENT", None)
    else:
        os.environ["EKKO_ENVIRONMENT"] = previous_environment

    if previous_disable_audio is None:
        os.environ.pop("EKKO_DISABLE_AUDIO", None)
    else:
        os.environ["EKKO_DISABLE_AUDIO"] = previous_disable_audio


@pytest.fixture
async def test_async_engine() -> AsyncGenerator[AsyncEngine]:
    """Create an in-memory SQLite async engine with test schema."""
    from ekko.infrastructure.db import models as _  # noqa: F401
    from ekko.infrastructure.db.base import Base

    engine = create_async_engine(_TEST_DATABASE_URL, future=True, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
def test_session_factory(
    test_async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Provide async SQLAlchemy session factory backed by in-memory SQLite."""
    return async_sessionmaker(test_async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def test_session(
    test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    """Provide async SQLAlchemy session for integration tests."""
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def integration_app(test_async_engine: AsyncEngine):
    """Create FastAPI app with in-memory SQLite DB engine injected."""
    from ekko.application.services import ReadinessService
    from ekko.composition import create_app
    from ekko.infrastructure.db.readiness import SQLAlchemyReadinessProbe

    app = create_app()
    app.state.db_engine = test_async_engine
    app.state.readiness_service = ReadinessService(
        database_probe=SQLAlchemyReadinessProbe(database_url=_TEST_DATABASE_URL),
    )
    app.state.session_factory = async_sessionmaker(
        test_async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return app


@pytest.fixture
def containerized_client(integration_app):
    """Provide in-process HTTP client for integration API tests."""
    from fastapi.testclient import TestClient

    with TestClient(integration_app, raise_server_exceptions=False) as client:
        yield client
