"""Property-based tests conftest with Hypothesis strategies."""

import pytest
from hypothesis import strategies as st

from ekko.config.enums import Environment, LLMProvider


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Remove EKKO_ENVIRONMENT so pydantic-settings uses class defaults."""
    monkeypatch.delenv("EKKO_ENVIRONMENT", raising=False)


# Strategies for domain types
environment_strategy = st.sampled_from(list(Environment))
llm_provider_strategy = st.sampled_from(list(LLMProvider))
port_strategy = st.integers(min_value=1024, max_value=65535)
host_strategy = st.from_regex(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", fullmatch=True)
