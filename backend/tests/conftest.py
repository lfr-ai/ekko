"""Root test configuration.

Sets up environment for all test sessions and provides shared fixtures.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


def _ensure_src_on_path() -> None:
    """Ensure local source directory is importable in test sessions."""
    src_path = Path(__file__).resolve().parents[1] / "src"
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


_ensure_src_on_path()

# Force test environment
os.environ.setdefault("EKKO_ENVIRONMENT", "test")


@pytest.fixture
def settings():
    """Provide a fresh test settings instance."""
    from ekko.config.settings import BaseAppConfig
    from ekko.core.enums import Environment

    return BaseAppConfig(environment=Environment.TEST, debug=False)


@pytest.fixture
def app(settings):
    """Create a FastAPI test app with dependency overrides."""
    from ekko.composition import create_app

    return create_app()


@pytest.fixture
def client(app):
    """Create a test client for the FastAPI app."""
    from fastapi.testclient import TestClient

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
