"""Property tests for registry constants validation.

Tests uniqueness, format patterns, and collision detection for all
auto-generated registry constants.
"""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path
from typing import Any

import pytest

from ekko.core import registry_constants


@pytest.fixture
def registry_json() -> dict[str, Any]:
    """Load the naming registry JSON for validation."""
    # Navigate from backend/tests/property to project root
    registry_path = Path(__file__).parent.parent.parent.parent / "registry" / "naming_registry.json"
    with registry_path.open() as f:
        return json.load(f)


@pytest.fixture
def all_constants() -> dict[str, str]:
    """Extract all constants from the registry_constants module."""
    constants = {}
    for name in dir(registry_constants):
        if name.isupper() and not name.startswith("_"):
            constants[name] = getattr(registry_constants, name)
    return constants


@pytest.fixture
def constants_by_category(
    all_constants: dict[str, str],
    registry_json: dict[str, Any],
) -> dict[str, dict[str, str]]:
    """Group constants by category prefix using registry categories."""
    by_category: dict[str, dict[str, str]] = {}

    # Use the registry to know what categories exist
    registry_categories = {cat.upper() for cat in registry_json}

    for name, value in all_constants.items():
        # Try to match against known categories
        matched = False
        for reg_cat in registry_categories:
            if name.startswith(f"{reg_cat}_") and name.endswith("_LABEL"):
                if reg_cat not in by_category:
                    by_category[reg_cat] = {}
                by_category[reg_cat][name] = value
                matched = True
                break

        if not matched:
            # Fallback: extract category as everything before the last two underscores
            parts = name.split("_")
            if len(parts) >= 3:
                category = "_".join(parts[:-2]) if name.endswith("_LABEL") else parts[0]
                if category not in by_category:
                    by_category[category] = {}
                by_category[category][name] = value

    return by_category


@pytest.mark.property
class TestRegistryConstantsUniqueness:
    """Property tests for constant uniqueness."""

    def test_all_constant_names_are_unique(
        self,
        all_constants: dict[str, str],
    ) -> None:
        """All constant names must be unique across the entire module."""
        constant_names = list(all_constants.keys())
        assert len(constant_names) == len(set(constant_names)), "Duplicate constant names found"

    def test_values_unique_within_category(
        self,
        constants_by_category: dict[str, dict[str, str]],
    ) -> None:
        """Values must be unique within each category."""
        for category, constants in constants_by_category.items():
            values = list(constants.values())
            unique_values = set(values)
            assert len(values) == len(unique_values), (
                f"Duplicate values in category {category}: {[v for v in values if values.count(v) > 1]}"
            )

    def test_no_empty_values(
        self,
        all_constants: dict[str, str],
    ) -> None:
        """No constant should have an empty string value."""
        empty_constants = [name for name, value in all_constants.items() if not value]
        assert not empty_constants, f"Empty values found in constants: {empty_constants}"


@pytest.mark.property
class TestRegistryConstantsFormatPatterns:
    """Property tests for constant naming and format patterns."""

    def test_constant_names_are_upper_snake_case(
        self,
        all_constants: dict[str, str],
    ) -> None:
        """All constant names must be UPPER_SNAKE_CASE."""
        pattern = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$")
        for name in all_constants:
            assert pattern.match(name), f"Constant {name} is not UPPER_SNAKE_CASE"

    def test_constant_names_follow_category_key_field_pattern(
        self,
        all_constants: dict[str, str],
    ) -> None:
        """Constant names must have at least category + key components."""
        for name in all_constants:
            parts = name.split("_")
            assert len(parts) >= 2, f"Constant {name} doesn't have at least 2 parts (CATEGORY_KEY)"

    def test_all_constants_end_with_label(
        self,
        all_constants: dict[str, str],
    ) -> None:
        """Constants should use one of the supported naming suffix/prefix conventions."""
        for name in all_constants:
            assert name.endswith("_LABEL") or name.startswith(("FIELD_", "ROUTE_", "ERROR_", "STATUS_")), (
                f"Constant {name} does not match expected naming convention"
            )

    def test_labels_are_non_empty_strings(
        self,
        all_constants: dict[str, str],
    ) -> None:
        """All label values must be non-empty strings."""
        for name, value in all_constants.items():
            assert isinstance(value, str), f"Constant {name} is not a string: {type(value)}"
            assert value.strip(), f"Constant {name} has empty or whitespace-only value"

    def test_labels_are_human_readable(
        self,
        all_constants: dict[str, str],
    ) -> None:
        """Label constants should be human-readable (no underscores, start with capital)."""
        for name, value in all_constants.items():
            if not name.endswith("_LABEL"):
                continue
            # Labels should start with an uppercase letter
            assert value[0].isupper(), f"Label {name} doesn't start with uppercase: {value}"
            # Labels shouldn't contain underscores (they're for human display)
            # Allow exceptions for technical terms like "16-bit"
            if "_" in value:
                pytest.fail(f"Label {name} contains underscore: {value}")


@pytest.mark.property
class TestRegistryConstantsConsistency:
    """Property tests for consistency with naming_registry.json."""

    @staticmethod
    def _expected_constant_name(*, category: str, key: str) -> str:
        category_upper = category.upper()
        key_upper = key.upper()

        if category == "field_names":
            return f"FIELD_{key_upper}"
        if category == "api_routes":
            return f"ROUTE_{key_upper}"
        if category == "error_codes":
            return f"ERROR_{key_upper}"
        if category == "status_values":
            return f"STATUS_{key_upper}"
        return f"{category_upper}_{key_upper}_LABEL"

    def test_all_registry_entries_have_constants(
        self,
        registry_json: dict[str, Any],
        all_constants: dict[str, str],
    ) -> None:
        """Each entry in the JSON registry should have a corresponding constant."""
        for category, entries in registry_json.items():
            for key, properties in entries.items():
                expected_constant = self._expected_constant_name(category=category, key=key)
                assert expected_constant in all_constants, f"Missing constant {expected_constant} for {category}.{key}"
                # Verify the value matches
                expected_value = properties["label"] if "label" in properties else properties["value"]
                assert all_constants[expected_constant] == expected_value, (
                    f"Constant {expected_constant} value mismatch: "
                    f"expected '{expected_value}', got '{all_constants[expected_constant]}'"
                )

    def test_no_extra_constants_not_in_registry(
        self,
        registry_json: dict[str, Any],
        all_constants: dict[str, str],
    ) -> None:
        """All constants should correspond to entries in the registry JSON."""
        expected_constants = set()
        for category, entries in registry_json.items():
            for key in entries:
                expected_constants.add(self._expected_constant_name(category=category, key=key))

        actual_constants = set(all_constants.keys())
        extra_constants = actual_constants - expected_constants

        assert not extra_constants, f"Found constants not in registry.json: {extra_constants}"

    def test_category_names_match_registry_keys(
        self,
        registry_json: dict[str, Any],
        all_constants: dict[str, str],
    ) -> None:
        """Every registry category should have at least one generated constant."""
        for category, entries in registry_json.items():
            assert entries, f"Registry category {category} should not be empty"
            first_key = next(iter(entries))
            expected_constant = self._expected_constant_name(category=category, key=first_key)
            assert expected_constant in all_constants, f"No generated constants found for registry category {category}"


@pytest.mark.property
class TestRegistryConstantsCollisions:
    """Property tests for collision detection between categories."""

    def test_no_value_collisions_across_categories(
        self,
        constants_by_category: dict[str, dict[str, str]],
    ) -> None:
        """Same label value shouldn't appear in different categories unless intentional."""
        all_values: dict[str, list[str]] = {}
        for constants in constants_by_category.values():
            for name, value in constants.items():
                if value not in all_values:
                    all_values[value] = []
                all_values[value].append(name)

        # Check for collisions (same value in multiple constants)
        collisions = {value: names for value, names in all_values.items() if len(names) > 1}

        # Some collisions might be intentional (e.g., "Other" appearing in multiple categories)
        # Flag them but allow specific known cases
        known_acceptable_collisions = {"Other"}

        problematic_collisions = {
            value: names for value, names in collisions.items() if value not in known_acceptable_collisions
        }

        assert not problematic_collisions, f"Value collisions across categories: {problematic_collisions}"

    def test_category_prefixes_dont_overlap(
        self,
        constants_by_category: dict[str, dict[str, str]],
    ) -> None:
        """Category prefixes should be distinct with no substring relationships."""
        categories = list(constants_by_category.keys())
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i + 1 :]:
                # Check cat1 is not a prefix of cat2 or vice versa
                assert not cat2.startswith(cat1), f"Category {cat1} is a prefix of {cat2}"
                assert not cat1.startswith(cat2), f"Category {cat2} is a prefix of {cat1}"


@pytest.mark.property
class TestRegistryModuleIntegrity:
    """Property tests for module-level integrity checks."""

    def test_module_can_be_imported(self) -> None:
        """Registry constants module must be importable without errors."""
        try:
            importlib.reload(registry_constants)
        except Exception as e:
            pytest.fail(f"Failed to import registry_constants: {e}")

    def test_module_has_docstring(self) -> None:
        """Module should have a docstring explaining it's auto-generated."""
        assert registry_constants.__doc__ is not None, "Module missing docstring"
        assert "auto-generated" in registry_constants.__doc__.lower(), (
            "Docstring should warn that module is auto-generated"
        )

    def test_no_mutable_objects_as_constants(
        self,
        all_constants: dict[str, str],
    ) -> None:
        """All constants should be immutable types (strings)."""
        for name, value in all_constants.items():
            assert isinstance(value, (str, int, float, bool, type(None))), (
                f"Constant {name} is mutable type {type(value)}"
            )
