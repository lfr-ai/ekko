"""Tests for immutable prompt-registry resolution and repository integrity."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from ekko.ai.prompts.registry import (
    EXPERIMENTAL_VERSION_SET,
    PROMPT_SOURCES,
    PromptRegistryError,
    get_active_prompt_versions,
    get_prompt_text,
    get_prompt_version_info,
    get_prompt_versions,
)
from ekko.core.registry_constants import PROMPT_KEY_SUMMARY_CHUNKS

_PROMPT_ROOT = Path(__file__).resolve().parents[3] / "src" / "ekko" / "ai" / "prompts"


@dataclass(frozen=True, slots=True)
class PromptSettingsStub:
    """Prompt settings required by the registry."""

    prompt_dir_path: Path
    prompt_version: str | None = None
    prompt_version_set: str = "production"
    prompt_auto_provision: bool = False


def _write_registry(*, prompt_dir: Path, version_sets: object) -> None:
    """Write a temporary registry manifest."""
    registry_dir = prompt_dir / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    (registry_dir / "prompt_registry.json").write_text(
        json.dumps({"version_sets": version_sets}),
        encoding="utf-8",
    )


@pytest.mark.unit
def test_checked_in_registry_has_no_runtime_active_set() -> None:
    """Manifest describes available sets without selecting one."""
    registry_path = _PROMPT_ROOT / "registry" / "prompt_registry.json"

    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    assert "active_version_set" not in registry
    assert EXPERIMENTAL_VERSION_SET not in registry["version_sets"]


@pytest.mark.unit
def test_checked_in_schema_requires_complete_closed_version_sets() -> None:
    """Schema rejects selection fields, experimental, partial sets, and unknown prompts."""
    schema_path = _PROMPT_ROOT / "registry" / "prompt_registry_schema.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    version_sets = schema["properties"]["version_sets"]
    prompts = schema["$defs"]["version_set"]["properties"]["prompts"]

    assert schema["required"] == ["version_sets"]
    assert schema["additionalProperties"] is False
    assert version_sets["propertyNames"] == {"not": {"const": EXPERIMENTAL_VERSION_SET}}
    assert set(prompts["required"]) == set(PROMPT_SOURCES)
    assert prompts["additionalProperties"] is False


@pytest.mark.unit
def test_checked_in_version_sets_resolve_complete_immutable_snapshots() -> None:
    """Every checked-in set pins every known prompt to an existing snapshot."""
    registry_path = _PROMPT_ROOT / "registry" / "prompt_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    missing_snapshots: list[Path] = []
    for version_set in registry["version_sets"].values():
        pins = version_set["prompts"]
        assert set(pins) == set(PROMPT_SOURCES)
        for prompt_key, version in pins.items():
            snapshot = _PROMPT_ROOT / "versions" / prompt_key / version / f"{prompt_key}.prompt.md"
            if not snapshot.is_file():
                missing_snapshots.append(snapshot)

    assert missing_snapshots == []


@pytest.mark.unit
@pytest.mark.parametrize("version_set", ["development", "production"])
def test_get_prompt_text_with_checked_in_named_set_returns_pinned_snapshot(version_set: str) -> None:
    """Named sets load their checked-in immutable prompt snapshots."""
    settings = PromptSettingsStub(
        prompt_dir_path=_PROMPT_ROOT,
        prompt_version_set=version_set,
    )
    expected_path = _PROMPT_ROOT / "versions" / "summary_chunks" / "v1.0" / "summary_chunks.prompt.md"

    text = get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    assert text == expected_path.read_text(encoding="utf-8")


@pytest.mark.unit
def test_get_prompt_text_with_experimental_set_reads_editable_template(tmp_path: Path) -> None:
    """Reserved experimental mode reads templates without a manifest entry."""
    template = tmp_path / "templates" / "summary_chunks.prompt.md"
    template.parent.mkdir(parents=True)
    template.write_text("editable template", encoding="utf-8")
    settings = PromptSettingsStub(
        prompt_dir_path=tmp_path,
        prompt_version_set=EXPERIMENTAL_VERSION_SET,
    )

    text = get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    assert text == "editable template"
    assert not (tmp_path / "versions").exists()


@pytest.mark.unit
def test_get_prompt_text_with_unknown_set_raises_without_mutating_files(tmp_path: Path) -> None:
    """A misspelled set fails instead of creating registry state."""
    _write_registry(prompt_dir=tmp_path, version_sets={"production": {"prompts": {}}})
    settings = PromptSettingsStub(prompt_dir_path=tmp_path, prompt_version_set="prodution")

    with pytest.raises(PromptRegistryError, match="prodution"):
        get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    assert not (tmp_path / "versions").exists()


@pytest.mark.unit
def test_get_prompt_text_with_incomplete_set_raises_actionable_error(tmp_path: Path) -> None:
    """A partial immutable set is rejected before prompt resolution."""
    _write_registry(
        prompt_dir=tmp_path,
        version_sets={
            "production": {
                "prompts": {PROMPT_KEY_SUMMARY_CHUNKS: "v1.0"},
            },
        },
    )
    settings = PromptSettingsStub(prompt_dir_path=tmp_path)

    with pytest.raises(PromptRegistryError, match="exactly these prompts"):
        get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)


@pytest.mark.unit
def test_get_prompt_text_with_active_set_field_raises_manifest_error(tmp_path: Path) -> None:
    """Legacy manifest-owned runtime selection is rejected."""
    registry_dir = tmp_path / "registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "prompt_registry.json").write_text(
        json.dumps({"version_sets": {}, "active_version_set": "production"}),
        encoding="utf-8",
    )
    settings = PromptSettingsStub(prompt_dir_path=tmp_path)

    with pytest.raises(PromptRegistryError, match="unsupported fields"):
        get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)


@pytest.mark.unit
def test_prompt_version_inspection_derives_metadata_from_snapshots() -> None:
    """Version inspection discovers immutable files without a mutable metadata ledger."""
    settings = PromptSettingsStub(prompt_dir_path=_PROMPT_ROOT)

    versions = get_prompt_versions(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)
    version_info = get_prompt_version_info(
        prompt_key=PROMPT_KEY_SUMMARY_CHUNKS,
        version="v1.0",
        settings=settings,
    )

    assert [item.version for item in versions] == ["v1.0"]
    assert version_info is not None
    assert version_info.file_path.is_file()
    assert len(version_info.checksum) == 64


@pytest.mark.unit
def test_get_active_prompt_versions_with_production_returns_all_pins() -> None:
    """Active metadata reflects the environment-selected immutable set."""
    settings = PromptSettingsStub(prompt_dir_path=_PROMPT_ROOT)

    active_versions = get_active_prompt_versions(settings=settings)

    assert set(active_versions) == set(PROMPT_SOURCES)
    assert {info.version for info in active_versions.values()} == {"v1.0"}
