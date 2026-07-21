"""Alembic env.py configured for SQLite via synchronous engine.

This file resolves the database URL from the application's settings
via :func:`ekko.config.settings.get_settings`.
"""

from __future__ import annotations

from logging.config import fileConfig
from typing import TYPE_CHECKING

from sqlalchemy import create_engine, pool

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection

# isort: off
from alembic import context
from ekko.config.settings import get_settings
from ekko.infrastructure.db import Base
# isort: on

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
    2. application settings (EKKO_ prefixed env vars)
    """
    url = config.get_main_option("sqlalchemy.url")
    if url:
        return url
    return get_settings().database_sync_url


def run_migrations_offline() -> None:
    url = _get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(_get_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
