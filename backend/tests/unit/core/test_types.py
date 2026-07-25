"""Unit tests for core type aliases and scalar wrappers."""

from __future__ import annotations

import pytest

from ekko.core.types import Confidence, MaxTokens, Temperature


@pytest.mark.unit
class TestMaxTokens:
    """Test MaxTokens scalar wrapper validation."""

    def test_valid_value(self) -> None:
        """Accept positive integer within bounds."""
        assert MaxTokens(1024) == 1024

    def test_zero_raises(self) -> None:
        """Reject zero value."""
        with pytest.raises(ValueError, match="must be positive"):
            MaxTokens(0)

    def test_negative_raises(self) -> None:
        """Reject negative value."""
        with pytest.raises(ValueError, match="must be positive"):
            MaxTokens(-1)

    def test_exceeds_limit_raises(self) -> None:
        """Reject value exceeding upper limit."""
        with pytest.raises(ValueError, match="must not exceed"):
            MaxTokens(2_000_000)

    def test_bool_raises(self) -> None:
        """Reject boolean input."""
        with pytest.raises(TypeError, match="must be an integer"):
            MaxTokens(True)  # type: ignore[arg-type]

    def test_float_raises(self) -> None:
        """Reject float input."""
        with pytest.raises(TypeError, match="must be an integer"):
            MaxTokens(1.5)  # type: ignore[arg-type]

    def test_boundary_one(self) -> None:
        """Accept minimum valid value."""
        assert MaxTokens(1) == 1

    def test_boundary_max(self) -> None:
        """Accept maximum valid value."""
        assert MaxTokens(1_000_000) == 1_000_000

    def test_is_int_subclass(self) -> None:
        """Return value that is int-compatible."""
        val = MaxTokens(512)
        assert isinstance(val, int)
        assert val + 1 == 513


@pytest.mark.unit
class TestTemperature:
    """Test Temperature scalar wrapper validation."""

    def test_valid_float(self) -> None:
        """Accept float within range."""
        assert Temperature(0.7) == pytest.approx(0.7)

    def test_zero_valid(self) -> None:
        """Accept zero (lower bound)."""
        assert Temperature(0.0) == 0.0

    def test_max_valid(self) -> None:
        """Accept 2.0 (upper bound)."""
        assert Temperature(2.0) == 2.0

    def test_int_accepted(self) -> None:
        """Accept integer input (coerced to float)."""
        assert Temperature(1) == 1.0

    def test_below_range_raises(self) -> None:
        """Reject value below 0.0."""
        with pytest.raises(ValueError, match="must be between"):
            Temperature(-0.1)

    def test_above_range_raises(self) -> None:
        """Reject value above 2.0."""
        with pytest.raises(ValueError, match="must be between"):
            Temperature(2.1)

    def test_bool_raises(self) -> None:
        """Reject boolean input."""
        with pytest.raises(TypeError, match="must be a numeric value"):
            Temperature(True)  # type: ignore[arg-type]

    def test_string_raises(self) -> None:
        """Reject string input."""
        with pytest.raises(TypeError, match="must be a numeric value"):
            Temperature("0.5")  # type: ignore[arg-type]

    def test_is_float_subclass(self) -> None:
        """Return value that is float-compatible."""
        val = Temperature(1.0)
        assert isinstance(val, float)


@pytest.mark.unit
class TestConfidence:
    """Test Confidence scalar wrapper validation."""

    def test_valid_value(self) -> None:
        """Accept float within [0.0, 1.0]."""
        assert Confidence(0.95) == pytest.approx(0.95)

    def test_zero_valid(self) -> None:
        """Accept zero (lower bound)."""
        assert Confidence(0.0) == 0.0

    def test_one_valid(self) -> None:
        """Accept 1.0 (upper bound)."""
        assert Confidence(1.0) == 1.0

    def test_below_range_raises(self) -> None:
        """Reject value below 0.0."""
        with pytest.raises(ValueError, match="must be between"):
            Confidence(-0.01)

    def test_above_range_raises(self) -> None:
        """Reject value above 1.0."""
        with pytest.raises(ValueError, match="must be between"):
            Confidence(1.01)

    def test_bool_raises(self) -> None:
        """Reject boolean input."""
        with pytest.raises(TypeError, match="must be a numeric value"):
            Confidence(True)  # type: ignore[arg-type]

    def test_int_accepted(self) -> None:
        """Accept integer 0 or 1."""
        assert Confidence(0) == 0.0
        assert Confidence(1) == 1.0

    def test_is_float_subclass(self) -> None:
        """Return value that is float-compatible."""
        val = Confidence(0.5)
        assert isinstance(val, float)
