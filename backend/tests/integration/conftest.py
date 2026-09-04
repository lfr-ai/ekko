"""Integration conftest — SQLite-backed test fixtures."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

_TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.fixture(autouse=True)
def _integration_environment() -> Generator[None]:
    """Force deterministic settings for integration test execution."""
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
def integration_settings() -> object:
    """Settings configured for integration testing."""
    from ekko.config.base import BaseAppConfig
    from ekko.config.enums import Environment

    return BaseAppConfig(
        environment=Environment.TEST,
        debug=False,
        disable_audio=True,
        azure_speech_key=None,
    )


@pytest.fixture
async def test_db_engine() -> AsyncGenerator[AsyncEngine]:
    """Create an in-memory SQLite async engine with schema."""
    from sqlalchemy.ext.asyncio import create_async_engine

    from ekko.infrastructure.db import models as _  # noqa: F401
    from ekko.infrastructure.db.base import Base

    engine = create_async_engine(_TEST_DATABASE_URL, future=True, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
def test_db_session_factory(test_db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Provide async SQLAlchemy session factory for integration tests."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    return async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
async def test_db_session(
    test_db_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    """Create a test database session."""
    async with test_db_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def integration_app():
    """Create an app instance configured for integration API tests."""
    from ekko.composition import create_app

    return create_app()


@pytest.fixture
def integration_client(integration_app):
    """Create test client that runs app lifespan handlers."""
    from fastapi.testclient import TestClient

    with TestClient(integration_app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture
def integration_app_with_db(test_db_engine: AsyncEngine):
    """Create an integration app with in-memory SQLite DB engine injected."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from ekko.application.services import ReadinessService
    from ekko.composition import create_app
    from ekko.infrastructure.db.readiness import SQLAlchemyReadinessProbe

    app = create_app()
    app.state.db_engine = test_db_engine
    app.state.readiness_service = ReadinessService(
        database_probe=SQLAlchemyReadinessProbe(database_url=_TEST_DATABASE_URL),
    )
    app.state.session_factory = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return app


@pytest.fixture
def integration_client_with_db(integration_app_with_db):
    """Create test client for integration app with DB context injected."""
    from fastapi.testclient import TestClient

    with TestClient(integration_app_with_db, raise_server_exceptions=False) as client:
        yield client
