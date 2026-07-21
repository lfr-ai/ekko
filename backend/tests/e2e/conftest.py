"""E2E test configuration — disables audio to allow headless execution."""

import os

import pytest


@pytest.fixture(autouse=True)
def _disable_audio_for_e2e():
    """Disable audio subsystem for e2e tests (CI/headless-friendly)."""
    previous = os.environ.get("EKKO_DISABLE_AUDIO")
    os.environ["EKKO_DISABLE_AUDIO"] = "true"
    yield
    if previous is None:
        os.environ.pop("EKKO_DISABLE_AUDIO", None)
    else:
        os.environ["EKKO_DISABLE_AUDIO"] = previous
