"""Integration conftest."""

from __future__ import annotations

import os
from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest
from testcontainers.postgres import PostgresContainer

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine
    from sqlalchemy.ext.asyncio import async_sessionmaker


@pytest.fixture(autouse=True)
def _integration_environment() -> Generator[None, None, None]:
    """Force deterministic settings for integration test execution."""
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


@pytest.fixture
def integration_settings() -> object:
    """Settings configured for integration testing."""
    from ekko.config.settings import BaseAppConfig
    from ekko.core.enums import Environment

    return BaseAppConfig(environment=Environment.TEST, debug=False, disable_audio=True)


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Run PostgreSQL in Docker for integration tests."""
    container = PostgresContainer(image="postgres:16", driver=None)

    try:
        container.start()
    except Exception as exc:  # pragma: no cover - depends on local Docker runtime
        pytest.skip(f"Postgres Testcontainer unavailable: {exc}")

    yield container

    container.stop()


@pytest.fixture(scope="session")
def postgres_async_database_url(postgres_container: PostgresContainer) -> str:
    """Build SQLAlchemy async database URL from container connection details."""
    return postgres_container.get_connection_url(driver="asyncpg")


@pytest.fixture
async def test_db_engine(postgres_async_database_url: str) -> AsyncEngine:
    """Create a PostgreSQL async engine backed by Testcontainers."""
    from sqlalchemy.ext.asyncio import create_async_engine

    # Import models to ensure they're registered with Base.metadata
    from ekko.infrastructure.db import models as _  # noqa: F401
    from ekko.infrastructure.db.base import Base

    engine = create_async_engine(
        postgres_async_database_url,
        future=True,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture
def test_db_session_factory(test_db_engine: AsyncEngine) -> async_sessionmaker[object]:
    """Provide async SQLAlchemy session factory for integration app/tests."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    return async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
async def test_db_session(test_db_session_factory: async_sessionmaker[object]):
    """Create a test database session."""
    async with test_db_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def integration_app(test_db_engine: AsyncEngine, test_db_session_factory: async_sessionmaker[object]):
    """Create an app instance configured for integration API tests."""
    from ekko.composition import create_app

    app = create_app()
    app.state.db_engine = test_db_engine
    app.state.session_factory = test_db_session_factory
    return app


@pytest.fixture
def integration_client(integration_app):
    """Create test client that runs app lifespan handlers."""
    from fastapi.testclient import TestClient

    with TestClient(integration_app, raise_server_exceptions=False) as client:
        yield client
