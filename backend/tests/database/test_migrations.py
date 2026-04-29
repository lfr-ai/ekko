"""Database tests — migration and ORM model validation."""

from __future__ import annotations

import pytest


@pytest.mark.integration
class TestAlembicConfig:
    """Validate alembic configuration is consistent."""

    def test_alembic_ini_exists(self):
        from pathlib import Path

        ini = Path(__file__).resolve().parents[2] / "alembic.ini"
        assert ini.exists()

    def test_alembic_env_imports(self):
        """Verify alembic/env.py exists and contains expected setup."""
        from pathlib import Path

        env_py = Path(__file__).resolve().parents[2] / "alembic" / "env.py"
        assert env_py.exists(), f"alembic/env.py not found at {env_py}"
        content = env_py.read_text()
        assert "target_metadata" in content


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
