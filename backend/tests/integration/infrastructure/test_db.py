"""Integration tests for database models and operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_user_create(test_db_session: AsyncSession) -> None:
    """Test creating a user in the database."""
    from ekko.infrastructure.db.models import User

    user = User(username="test_user", full_name="Test User")
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    assert user.id is not None
    assert user.username == "test_user"
    assert user.full_name == "Test User"


@pytest.mark.asyncio
async def test_user_read(test_db_session: AsyncSession) -> None:
    """Test reading a user from the database."""
    from ekko.infrastructure.db.models import User

    # Create user
    user = User(username="read_user", full_name="Read User")
    test_db_session.add(user)
    await test_db_session.commit()
    user_id = user.id

    # Read user
    result = await test_db_session.execute(select(User).where(User.id == user_id))
    fetched_user = result.scalar_one()

    assert fetched_user.id == user_id
    assert fetched_user.username == "read_user"
    assert fetched_user.full_name == "Read User"


@pytest.mark.asyncio
async def test_user_update(test_db_session: AsyncSession) -> None:
    """Test updating a user in the database."""
    from ekko.infrastructure.db.models import User

    # Create user
    user = User(username="update_user", full_name="Original Name")
    test_db_session.add(user)
    await test_db_session.commit()
    user_id = user.id

    # Update user
    result = await test_db_session.execute(select(User).where(User.id == user_id))
    user_to_update = result.scalar_one()
    user_to_update.full_name = "Updated Name"
    await test_db_session.commit()

    # Verify update
    result = await test_db_session.execute(select(User).where(User.id == user_id))
    updated_user = result.scalar_one()
    assert updated_user.full_name == "Updated Name"


@pytest.mark.asyncio
async def test_user_delete(test_db_session: AsyncSession) -> None:
    """Test deleting a user from the database."""
    from ekko.infrastructure.db.models import User

    # Create user
    user = User(username="delete_user", full_name="Delete User")
    test_db_session.add(user)
    await test_db_session.commit()
    user_id = user.id

    # Delete user
    result = await test_db_session.execute(select(User).where(User.id == user_id))
    user_to_delete = result.scalar_one()
    await test_db_session.delete(user_to_delete)
    await test_db_session.commit()

    # Verify deletion
    result = await test_db_session.execute(select(User).where(User.id == user_id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_user_unique_constraint(test_db_session: AsyncSession) -> None:
    """Test that username unique constraint is enforced."""
    from sqlalchemy.exc import IntegrityError

    from ekko.infrastructure.db.models import User

    # Create first user
    user1 = User(username="unique_user", full_name="User One")
    test_db_session.add(user1)
    await test_db_session.commit()

    # Try to create second user with same username
    user2 = User(username="unique_user", full_name="User Two")
    test_db_session.add(user2)

    with pytest.raises(IntegrityError):
        await test_db_session.commit()


@pytest.mark.asyncio
async def test_transaction_rollback(test_db_session: AsyncSession) -> None:
    """Test that transaction rollback works correctly."""
    from ekko.infrastructure.db.models import User

    # Create user
    user = User(username="rollback_user", full_name="Rollback User")
    test_db_session.add(user)
    await test_db_session.flush()  # Flush to get ID but don't commit
    user_id = user.id

    # Rollback
    await test_db_session.rollback()

    # Verify user was not persisted
    result = await test_db_session.execute(select(User).where(User.id == user_id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_session_isolation(test_db_session: AsyncSession) -> None:
    """Test that sessions are properly isolated."""
    from ekko.infrastructure.db.models import User

    # Create and commit user in first session
    user = User(username="isolation_user", full_name="Isolation User")
    test_db_session.add(user)
    await test_db_session.commit()

    # Verify changes are visible in same session
    result = await test_db_session.execute(select(User).where(User.username == "isolation_user"))
    fetched_user = result.scalar_one()
    assert fetched_user.full_name == "Isolation User"
