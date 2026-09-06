"""Integration tests for database and API boundaries."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select, text

from ekko.infrastructure.db.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_db_engine_when_started_then_select_one_succeeds(test_async_engine) -> None:
    """SQLite async engine accepts simple connectivity probes."""
    async with test_async_engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))

    assert result.scalar_one() == 1


@pytest.mark.asyncio
async def test_user_create_when_valid_payload_then_row_is_persisted(
    test_session: AsyncSession,
) -> None:
    """User rows persist through the async ORM session."""
    user = User(username="integration_user", full_name="Integration User")

    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    assert user.id is not None
    assert user.username == "integration_user"


@pytest.mark.asyncio
async def test_user_read_when_row_exists_then_query_returns_it(
    test_session: AsyncSession,
) -> None:
    """Inserted rows are queryable with SQLAlchemy select statements."""
    seeded_user = User(username="reader", full_name="Read Model")
    test_session.add(seeded_user)
    await test_session.commit()

    result = await test_session.execute(select(User).where(User.username == "reader"))
    loaded_user = result.scalar_one()

    assert loaded_user.full_name == "Read Model"


def test_health_endpoint_reports_sqlite_state(containerized_client) -> None:
    """REST health endpoint is reachable and reports SQLite state."""
    response = containerized_client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["ok"], bool)
    assert "sqlite_database_present" in payload["details"]


def test_prompt_catalog_graphql_returns_version_set(containerized_client) -> None:
    """Prompt catalog GraphQL query returns the active version set and prompts."""
    response = containerized_client.post(
        "/graphql",
        json={"query": "query { promptCatalog { versionSet prompts { key } } }"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload
    catalog = payload["data"]["promptCatalog"]
    assert isinstance(catalog["versionSet"], str)
    assert catalog["versionSet"]
    assert isinstance(catalog["prompts"], list)
