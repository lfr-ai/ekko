"""Root test configuration for repository-level test suites.

Provides deterministic environment setup and shared Testcontainers fixtures
used by integration and end-to-end tests.
"""

from __future__ import annotations

import asyncio
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
from testcontainers.postgres import PostgresContainer

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator


def _ensure_backend_src_on_path() -> None:
    """Ensure backend source directory is importable in test sessions."""
    backend_src = Path(__file__).resolve().parents[1] / "backend" / "src"
    backend_src_str = str(backend_src)
    if backend_src_str not in sys.path:
        sys.path.insert(0, backend_src_str)


_ensure_backend_src_on_path()


@pytest.fixture(scope="session", autouse=True)
def _test_environment() -> Generator[None, None, None]:
    """Force deterministic environment for all root tests."""
    from ekko.config.settings import get_settings

    previous_environment = os.environ.get("EKKO_ENVIRONMENT")
    previous_disable_audio = os.environ.get("EKKO_DISABLE_AUDIO")

    os.environ["EKKO_ENVIRONMENT"] = "test"
    os.environ["EKKO_DISABLE_AUDIO"] = "true"
    get_settings.cache_clear()

    yield

    get_settings.cache_clear()
    if previous_environment is None:
        os.environ.pop("EKKO_ENVIRONMENT", None)
    else:
        os.environ["EKKO_ENVIRONMENT"] = previous_environment

    if previous_disable_audio is None:
        os.environ.pop("EKKO_DISABLE_AUDIO", None)
    else:
        os.environ["EKKO_DISABLE_AUDIO"] = previous_disable_audio


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Run PostgreSQL in Docker for container-backed test flows."""
    try:
        import docker

        docker.from_env().ping()
    except Exception as exc:  # pragma: no cover - depends on local Docker runtime
        pytest.skip(f"Docker not available: {exc}")

    container = PostgresContainer(image="postgres:16", driver=None)

    try:
        container.start()
    except Exception as exc:  # pragma: no cover - depends on local Docker runtime
        pytest.skip(f"Postgres Testcontainer unavailable: {exc}")

    yield container

    container.stop()


@pytest.fixture(scope="session")
def postgres_async_database_url(postgres_container: PostgresContainer) -> str:
    """Build SQLAlchemy async URL from Testcontainers connection details."""
    return postgres_container.get_connection_url(driver="asyncpg")


@pytest.fixture
async def postgres_async_engine(
    postgres_async_database_url: str,
) -> AsyncGenerator[AsyncEngine, None]:
    """Create a PostgreSQL async engine with test schema created."""
    from ekko.infrastructure.db import models as _  # noqa: F401
    from ekko.infrastructure.db.base import Base

    engine = create_async_engine(postgres_async_database_url, future=True, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def postgres_session_factory(
    postgres_async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Provide async SQLAlchemy session factory bound to Testcontainer DB."""
    return async_sessionmaker(postgres_async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def postgres_session(
    postgres_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Provide async SQLAlchemy session for integration tests."""
    async with postgres_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def app_with_postgres(postgres_async_database_url: str):
    """Create FastAPI app with a Testcontainers-backed DB engine injected."""
    from ekko.composition import create_app

    app = create_app()

    db_engine = create_async_engine(postgres_async_database_url, future=True, echo=False)
    app.state.db_engine = db_engine
    app.state.session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    yield app

    asyncio.run(db_engine.dispose())


@pytest.fixture
def containerized_client(app_with_postgres):
    """Provide in-process HTTP client for container-backed API tests."""
    from fastapi.testclient import TestClient

    with TestClient(app_with_postgres, raise_server_exceptions=False) as client:
        yield client
