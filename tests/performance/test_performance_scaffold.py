"""Performance test scaffold.

These placeholders keep the performance task target valid until concrete
benchmark scenarios are implemented.
"""

from __future__ import annotations

import pytest


@pytest.mark.performance
@pytest.mark.skip(reason="Performance benchmarks not implemented yet")
def test_performance_benchmark_when_not_implemented_is_skipped(benchmark) -> None:
    """Placeholder benchmark test to keep task wiring healthy."""

    benchmark(lambda: None)
