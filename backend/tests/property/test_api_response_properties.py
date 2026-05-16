"""Property-based invariants for API response schemas."""

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from ekko.presentation.api.schemas.responses import HealthResponse, StreamResponse

pytestmark = pytest.mark.property


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    ok=st.booleans(),
    details=st.dictionaries(
        keys=st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=10),
        values=st.one_of(st.booleans(), st.integers(min_value=-10_000, max_value=10_000), st.text(max_size=20)),
        max_size=5,
    ),
)
def test_health_response_when_constructed_then_roundtrip_is_lossless(ok: bool, details: dict[str, object]) -> None:
    """HealthResponse should preserve arbitrary JSON-like detail payloads."""
    response = HealthResponse(ok=ok, details=details)

    assert response.ok is ok
    assert response.details == details


@settings(max_examples=50)
@given(status=st.text(min_size=1, max_size=20))
def test_stream_response_when_constructed_then_status_matches_input(status: str) -> None:
    """StreamResponse should retain non-empty status values."""
    response = StreamResponse(status=status)

    assert response.status == status
