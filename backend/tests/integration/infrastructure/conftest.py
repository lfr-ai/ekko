"""Integration test fixtures for infrastructure tests."""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module", autouse=True)
def ensure_logs_dir():
    """Ensure logs directory exists for STT tests."""

    from ekko.config.settings import get_settings

    settings = get_settings()
    settings.logs_dir_path.mkdir(parents=True, exist_ok=True)
