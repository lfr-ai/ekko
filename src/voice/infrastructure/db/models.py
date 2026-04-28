"""SQLAlchemy declarative models for the voice app (example)."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String
from voice.infrastructure.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), nullable=False, unique=True)
    full_name = Column(String(256), nullable=True)
