"""Database tests — migration and ORM model validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from ekko.infrastructure.db.models import User


@pytest.mark.integration
class TestAlembicConfig:
    """Validate alembic configuration is consistent."""

    def test_alembic_ini_exists(self):
        ini = Path(__file__).resolve().parents[2] / "alembic.ini"
        assert ini.exists()

    def test_alembic_env_imports(self):
        """Verify alembic/env.py exists and contains expected setup."""
        env_py = Path(__file__).resolve().parents[2] / "alembic" / "env.py"
        assert env_py.exists(), f"alembic/env.py not found at {env_py}"
        content = env_py.read_text()
        assert "target_metadata = User.metadata" in content

    def test_migration_history_contains_current_users_schema(self) -> None:
        """Migration head should create the table represented by ORM metadata."""
        versions = Path(__file__).resolve().parents[2] / "alembic" / "versions"
        migration_text = "\n".join(path.read_text() for path in sorted(versions.glob("*.py")))

        assert '"users"' in migration_text
        assert User.__table__.name == "users"


@pytest.mark.integration
class TestORMModels:
    """Validate ORM model definitions."""

    def test_models_import(self):
        """Ensure ORM models module can be imported."""
        from ekko.infrastructure.db import models

        assert models is not None

    def test_base_import(self):
        """Ensure the declarative base can be imported."""
        from ekko.infrastructure.db.base import Base

        assert Base is not None
