from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from voice.config.settings import SETTINGS


_engine = create_engine(SETTINGS.get_database_url(), future=True)

SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def get_engine():
    """Return the SQLAlchemy Engine used by the application.

    Alembic env.py can import this to run migrations.
    """
    return _engine


def get_session() -> Generator:
    """Yield a SQLAlchemy session. Use as a context manager or dependency.

    Example (FastAPI dependency):
        def get_db():
            with get_session() as session:
                yield session
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
