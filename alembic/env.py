"""Alembic env.py configured for async SQLAlchemy engines.

This file prefers a SQLAlchemy URL from the alembic config (`sqlalchemy.url`) and
falls back to the application's settings via :func:`voice.config.settings.get_settings`.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from voice.config.settings import get_settings
from voice.infrastructure.db import Base

# Alembic config and logging
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate'
target_metadata = Base.metadata


def _get_url() -> str:
    """Resolve the SQLAlchemy URL for migrations.

    Preference order:
    1. `sqlalchemy.url` in alembic.ini (useful for CI/managed runs)
    2. application settings (VOICE_ prefixed env vars)
    """
    url = config.get_main_option("sqlalchemy.url")
    if url:
        return url
    return get_settings().postgresql_async_url


def run_migrations_offline() -> None:
    url = _get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(_get_url(), poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
