"""Container-backed integration tests for database and API boundaries."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select, text

from ekko.infrastructure.db.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_postgres_engine_when_container_running_then_select_one_succeeds(
    postgres_async_engine,
) -> None:
    """Testcontainer PostgreSQL should accept simple connectivity probes."""
    # Arrange / Act
    async with postgres_async_engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))

    # Assert
    assert result.scalar_one() == 1


@pytest.mark.asyncio
async def test_user_create_when_valid_payload_then_row_is_persisted(
    postgres_session: AsyncSession,
) -> None:
    """User rows should persist through async ORM session with PostgreSQL."""
    # Arrange
    user = User(username="integration_user", full_name="Integration User")

    # Act
    postgres_session.add(user)
    await postgres_session.commit()
    await postgres_session.refresh(user)

    # Assert
    assert user.id is not None
    assert user.username == "integration_user"


@pytest.mark.asyncio
async def test_user_read_when_row_exists_then_query_returns_it(
    postgres_session: AsyncSession,
) -> None:
    """Inserted rows should be queryable with SQLAlchemy select statements."""
    # Arrange
    seeded_user = User(username="reader", full_name="Read Model")
    postgres_session.add(seeded_user)
    await postgres_session.commit()

    # Act
    result = await postgres_session.execute(
        select(User).where(User.username == "reader")
    )
    loaded_user = result.scalar_one()

    # Assert
    assert loaded_user.full_name == "Read Model"


def test_health_when_containerized_app_running_then_returns_queue_details(
    containerized_client,
) -> None:
    """REST health endpoint should be reachable in integration flow."""
    # Arrange / Act
    response = containerized_client.get("/health")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["ok"], bool)
    assert "transcripts_queue_present" in payload["details"]


def test_graphql_health_ready_when_db_injected_then_dependency_reports_healthy(
    containerized_client,
) -> None:
    """GraphQL health_ready should report database as healthy with Testcontainer DB."""
    # Arrange
    query = {
        "query": "query { healthReady { status dependencies { name healthy detail } } }",
    }

    # Act
    response = containerized_client.post("/graphql/graphql", json=query)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "errors" not in payload

    dependencies = payload["data"]["healthReady"]["dependencies"]
    database_dependency = next(dep for dep in dependencies if dep["name"] == "database")
    assert database_dependency["healthy"] is True
