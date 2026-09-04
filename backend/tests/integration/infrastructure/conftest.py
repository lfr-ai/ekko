"""Integration test fixtures for infrastructure tests."""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module", autouse=True)
def ensure_logs_dir():
    """Ensure logs directory exists for STT tests."""

    from ekko.config.runtime import get_config

    settings = get_config()
    settings.logs_dir_path.mkdir(parents=True, exist_ok=True)
