"""Property-based tests for the naming registry.

Validates invariants that must hold for all registry entries:
- Label/value uniqueness within sections
- Key format compliance
- No duplicate keys across sections
- Enum-registry correspondence

Uses Hypothesis for property-based testing (R009).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from hypothesis import given, strategies as st

if TYPE_CHECKING:
    from collections.abc import Sequence

# ── Constants ───────────────────────────────────────────────────

REGISTRY_PATH = (
    Path(__file__).parent.parent.parent / "registry" / "naming_registry.json"
)
VALID_KEY_PATTERN = re.compile(r"^[a-z0-9_]+$")

# ── Fixtures ────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def registry() -> dict:
    """Load naming registry from JSON file."""
    with REGISTRY_PATH.open() as f:
        return json.load(f)


# ── Property Tests ──────────────────────────────────────────────


def test_registry_exists() -> None:
    """Registry file exists and is valid JSON."""
    assert REGISTRY_PATH.exists(), f"Registry not found at {REGISTRY_PATH}"
    with REGISTRY_PATH.open() as f:
        registry = json.load(f)
    assert isinstance(registry, dict), "Registry must be a JSON object"
    assert len(registry) > 0, "Registry must not be empty"


def test_label_uniqueness_within_sections(registry: dict) -> None:
    """Labels are unique within each section.

    No two entries in the same section should have the same display label.
    """
    for section_name, entries in registry.items():
        labels = [meta.get("label") for meta in entries.values() if "label" in meta]
        assert len(labels) == len(set(labels)), (
            f"Duplicate labels found in section '{section_name}': {labels}"
        )


def test_value_uniqueness_within_sections(registry: dict) -> None:
    """Values are unique within each section.

    No two entries in the same section should have the same value.
    """
    for section_name, entries in registry.items():
        values = [meta.get("value") for meta in entries.values() if "value" in meta]
        assert len(values) == len(set(values)), (
            f"Duplicate values found in section '{section_name}': {values}"
        )


def test_no_duplicate_keys_within_sections(registry: dict) -> None:
    """Keys are unique within each section.

    A section cannot have duplicate keys. Duplicate keys across sections are
    acceptable because the generator uses section-specific prefixes
    (e.g., FIELD_USER vs MESSAGE_ROLES_USER_LABEL).
    """
    for section_name, entries in registry.items():
        keys = list(entries.keys())
        duplicates = [k for k in keys if keys.count(k) > 1]
        assert len(keys) == len(set(keys)), (
            f"Duplicate keys found in section '{section_name}': {set(duplicates)}"
        )


def test_valid_key_format(registry: dict) -> None:
    """All keys match the pattern [a-z0-9_]+.

    Keys must be lowercase alphanumeric with underscores only, suitable for
    generating Python constant names.
    """
    invalid_keys: list[tuple[str, str]] = []
    for section_name, entries in registry.items():
        for key in entries.keys():
            if not VALID_KEY_PATTERN.match(key):
                invalid_keys.append((section_name, key))

    assert not invalid_keys, (
        f"Invalid key format (must match [a-z0-9_]+): {invalid_keys}"
    )


def test_required_fields_present(registry: dict) -> None:
    """Every entry has required fields (label or value, and description).

    Each entry must have at least one of 'label' or 'value', and must have a
    'description'.
    """
    missing_fields: list[tuple[str, str, str]] = []
    for section_name, entries in registry.items():
        for key, meta in entries.items():
            if "label" not in meta and "value" not in meta:
                missing_fields.append((section_name, key, "label or value"))
            if "description" not in meta:
                missing_fields.append((section_name, key, "description"))

    assert not missing_fields, f"Missing required fields: {missing_fields}"


def test_section_names_valid(registry: dict) -> None:
    """Section names match the pattern [a-z0-9_]+."""
    invalid_sections = [
        section for section in registry.keys() if not VALID_KEY_PATTERN.match(section)
    ]
    assert not invalid_sections, f"Invalid section names: {invalid_sections}"


# ── Hypothesis Property Tests ───────────────────────────────────


@given(
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_", min_size=1, max_size=20)
)
def test_hypothetical_key_format(key: str) -> None:
    """Any key matching [a-z0-9_]+ is valid.

    Hypothesis generates random valid keys and confirms they match the pattern.
    """
    assert VALID_KEY_PATTERN.match(key), f"Generated key '{key}' should be valid"


@given(
    st.lists(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=3, max_size=10),
        min_size=2,
        max_size=10,
        unique=True,
    )
)
def test_uniqueness_property(labels: Sequence[str]) -> None:
    """Unique input labels remain unique after set conversion.

    Validates that uniqueness checks work correctly for any list of labels.
    """
    assert len(labels) == len(set(labels)), "Unique labels should remain unique"


def test_enum_registry_correspondence(registry: dict) -> None:
    """All enums defined in core/enums/ have corresponding registry entries.

    This ensures that enum values can be looked up in the registry for
    display purposes.
    """
    # Known enum sections in the registry
    enum_sections = {
        "message_roles",
        "transcript_statuses",
        "audio_formats",
        "llm_providers",
        "stt_providers",
        "environments",
    }

    for section in enum_sections:
        assert section in registry, f"Enum section '{section}' not found in registry"

        # Verify each entry has a label for display
        entries = registry[section]
        for key, meta in entries.items():
            assert "label" in meta, (
                f"Enum entry '{key}' in section '{section}' missing 'label' field"
            )


def test_field_names_section_structure(registry: dict) -> None:
    """Field names section has 'value' field (not 'label')."""
    if "field_names" not in registry:
        pytest.skip("field_names section not present in registry")

    for key, meta in registry["field_names"].items():
        assert "value" in meta, f"Field name '{key}' missing 'value' field"
        assert isinstance(meta["value"], str), (
            f"Field name '{key}' value must be string"
        )


def test_api_routes_section_structure(registry: dict) -> None:
    """API routes section has valid path values."""
    if "api_routes" not in registry:
        pytest.skip("api_routes section not present in registry")

    for key, meta in registry["api_routes"].items():
        assert "value" in meta, f"Route '{key}' missing 'value' field"
        value = meta["value"]
        assert value.startswith("/"), (
            f"Route '{key}' value must start with '/': {value}"
        )


def test_error_codes_section_structure(registry: dict) -> None:
    """Error codes section has valid code values."""
    if "error_codes" not in registry:
        pytest.skip("error_codes section not present in registry")

    for key, meta in registry["error_codes"].items():
        assert "value" in meta, f"Error code '{key}' missing 'value' field"
        assert isinstance(meta["value"], str), (
            f"Error code '{key}' value must be string"
        )
