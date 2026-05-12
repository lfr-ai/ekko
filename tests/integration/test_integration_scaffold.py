"""Integration test scaffold.

These placeholders keep the integration task target valid until concrete
integration scenarios are implemented.
"""

from __future__ import annotations

import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="Integration scenarios not implemented yet")
def test_integration_suite_when_not_implemented_is_skipped() -> None:
    """Placeholder integration test to keep task wiring healthy."""
