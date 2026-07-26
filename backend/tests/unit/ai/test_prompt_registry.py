"""Tests for prompt registry versioning and provisioning."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

import ekko.ai.prompts.registry as prompt_registry
from ekko.ai.prompts.registry import (
    EXPERIMENTAL_VERSION_SET,
    PROMPT_SOURCES,
    PromptRegistryError,
    get_active_prompt_versions,
    get_prompt_text,
    get_prompt_version_info,
    get_prompt_versions,
    provision_prompt,
)
from ekko.core.registry_constants import (
    PROMPT_KEY_CONVERSATIONAL_SYSTEM,
    PROMPT_KEY_HMAS_AGENT_POLICY,
    PROMPT_KEY_HMAS_AGGREGATION_POLICY,
    PROMPT_KEY_HMAS_DELEGATION_BRIEF,
    PROMPT_KEY_HMAS_FAILURE_POLICY,
    PROMPT_KEY_HMAS_PLANNING_POLICY,
    PROMPT_KEY_HMAS_PROFILE_ANALYST,
    PROMPT_KEY_HMAS_PROFILE_PLANNER,
    PROMPT_KEY_HMAS_PROFILE_RESEARCHER,
    PROMPT_KEY_HMAS_PROFILE_REVIEWER,
    PROMPT_KEY_HMAS_PROFILE_WRITER,
    PROMPT_KEY_HMAS_SUPERVISOR_SYSTEM,
    PROMPT_KEY_HMAS_TASK_POLICY,
    PROMPT_KEY_SUMMARY_CHUNKS,
)


@dataclass(slots=True)
class PromptSettingsStub:
    prompt_dir_path: Path
    prompt_version: str | None = None
    prompt_version_set: str = "production"
    prompt_auto_provision: bool = True


def _seed_file_backed_hmas_prompts(prompt_dir: Path) -> None:
    for source in PROMPT_SOURCES.values():
        if source.source_kind != "file":
            continue
        file_path = prompt_dir / source.source_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not file_path.exists():
            file_path.write_text(f"seeded {source.key}", encoding="utf-8")


@pytest.mark.unit
def test_provision_prompt_creates_first_version(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    settings = PromptSettingsStub(prompt_dir_path=prompt_dir)
    info = provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    assert info.version == "v1.0"
    assert info.is_new is True
    assert info.file_path.exists()
    assert info.file_path.read_text(encoding="utf-8") == "Prompt V1: {content}"


@pytest.mark.unit
def test_provision_prompt_creates_new_version_on_source_change(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    settings = PromptSettingsStub(prompt_dir_path=prompt_dir)
    first = provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    source_file.write_text("Prompt V2: {content}", encoding="utf-8")
    second = provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    assert first.version == "v1.0"
    assert second.version == "v1.1"

    versions = get_prompt_versions(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)
    assert [version.version for version in versions] == ["v1.0", "v1.1"]


@pytest.mark.unit
def test_get_prompt_text_respects_selected_version(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    settings = PromptSettingsStub(prompt_dir_path=prompt_dir)
    provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    source_file.write_text("Prompt V2: {content}", encoding="utf-8")
    provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    selected = PromptSettingsStub(
        prompt_dir_path=prompt_dir,
        prompt_version="v1.0",
        prompt_auto_provision=True,
    )
    text = get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=selected)
    assert text == "Prompt V1: {content}"


@pytest.mark.unit
def test_get_prompt_text_raises_for_unknown_version(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    settings = PromptSettingsStub(
        prompt_dir_path=prompt_dir,
        prompt_version="v9",
        prompt_auto_provision=True,
    )

    with pytest.raises(PromptRegistryError):
        get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)


@pytest.mark.unit
def test_get_active_prompt_versions_with_auto_provision_returns_versions(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")
    _seed_file_backed_hmas_prompts(prompt_dir)

    settings = PromptSettingsStub(prompt_dir_path=prompt_dir)
    provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)
    provision_prompt(prompt_key=PROMPT_KEY_CONVERSATIONAL_SYSTEM, settings=settings)

    active_versions = get_active_prompt_versions(settings=settings)

    assert active_versions[PROMPT_KEY_SUMMARY_CHUNKS].version == "v1.0"
    assert active_versions[PROMPT_KEY_CONVERSATIONAL_SYSTEM].version == "v1.0"


@pytest.mark.unit
def test_get_prompt_version_info_with_existing_version_returns_metadata(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    settings = PromptSettingsStub(prompt_dir_path=prompt_dir)
    provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    version_info = get_prompt_version_info(
        prompt_key=PROMPT_KEY_SUMMARY_CHUNKS,
        version="v1.0",
        settings=settings,
    )

    assert version_info is not None
    assert version_info.version == "v1.0"


@pytest.mark.unit
def test_provision_prompt_with_stale_lock_raises_registry_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    versions_dir = prompt_dir / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    lock_path = versions_dir / ".registry.lock"
    lock_path.write_text("stale-lock", encoding="utf-8")

    monkeypatch.setattr(prompt_registry, "REGISTRY_LOCK_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(prompt_registry, "REGISTRY_LOCK_POLL_INTERVAL_SECONDS", 0.005)

    settings = PromptSettingsStub(prompt_dir_path=prompt_dir)
    with pytest.raises(PromptRegistryError, match="Timed out waiting for prompt registry lock"):
        provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)


@pytest.mark.unit
def test_experimental_version_set_reads_from_source_directly(tmp_path: Path) -> None:
    """Experimental mode always reads from template source, no versioning."""
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("experimental content", encoding="utf-8")

    settings = PromptSettingsStub(
        prompt_dir_path=prompt_dir,
        prompt_version_set=EXPERIMENTAL_VERSION_SET,
    )

    text = get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)
    assert text == "experimental content"

    # No version file should have been created.
    versions_dir = prompt_dir / "versions"
    assert not versions_dir.exists() or not list(versions_dir.rglob("*.prompt.md"))


@pytest.mark.unit
def test_named_version_set_pins_prompt_version_after_source_changes(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    pinned_settings = PromptSettingsStub(
        prompt_dir_path=prompt_dir,
        prompt_version_set="production",
        prompt_auto_provision=True,
    )

    first_text = get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=pinned_settings)
    assert first_text == "Prompt V1: {content}"

    source_file.write_text("Prompt V2: {content}", encoding="utf-8")
    second_text = get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=pinned_settings)

    assert second_text == "Prompt V1: {content}"


@pytest.mark.unit
def test_named_version_set_without_entry_and_auto_provision_disabled_raises(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    strict_settings = PromptSettingsStub(
        prompt_dir_path=prompt_dir,
        prompt_version_set="production",
        prompt_auto_provision=False,
    )

    with pytest.raises(PromptRegistryError, match="version set"):
        get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=strict_settings)


@pytest.mark.unit
def test_hmas_prompt_registry_keys_are_present_and_non_empty(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    summary_file = prompt_dir / "templates" / "summary_chunks.prompt.md"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text("summary", encoding="utf-8")
    _seed_file_backed_hmas_prompts(prompt_dir)

    settings = PromptSettingsStub(prompt_dir_path=prompt_dir)
    hmas_keys = [
        PROMPT_KEY_HMAS_AGENT_POLICY,
        PROMPT_KEY_HMAS_TASK_POLICY,
        PROMPT_KEY_HMAS_PROFILE_PLANNER,
        PROMPT_KEY_HMAS_PROFILE_RESEARCHER,
        PROMPT_KEY_HMAS_PROFILE_ANALYST,
        PROMPT_KEY_HMAS_PROFILE_WRITER,
        PROMPT_KEY_HMAS_PROFILE_REVIEWER,
        PROMPT_KEY_HMAS_SUPERVISOR_SYSTEM,
        PROMPT_KEY_HMAS_PLANNING_POLICY,
        PROMPT_KEY_HMAS_DELEGATION_BRIEF,
        PROMPT_KEY_HMAS_AGGREGATION_POLICY,
        PROMPT_KEY_HMAS_FAILURE_POLICY,
    ]

    for key in hmas_keys:
        assert key in PROMPT_SOURCES
        assert get_prompt_text(key, settings=settings).strip()


@pytest.mark.unit
def test_hmas_prompt_registry_sources_use_file_backed_subfolders() -> None:
    file_backed_hmas_keys = [
        PROMPT_KEY_HMAS_AGENT_POLICY,
        PROMPT_KEY_HMAS_TASK_POLICY,
        PROMPT_KEY_HMAS_PROFILE_PLANNER,
        PROMPT_KEY_HMAS_PROFILE_RESEARCHER,
        PROMPT_KEY_HMAS_PROFILE_ANALYST,
        PROMPT_KEY_HMAS_PROFILE_WRITER,
        PROMPT_KEY_HMAS_PROFILE_REVIEWER,
        PROMPT_KEY_HMAS_SUPERVISOR_SYSTEM,
        PROMPT_KEY_HMAS_PLANNING_POLICY,
        PROMPT_KEY_HMAS_DELEGATION_BRIEF,
        PROMPT_KEY_HMAS_AGGREGATION_POLICY,
        PROMPT_KEY_HMAS_FAILURE_POLICY,
    ]

    for key in file_backed_hmas_keys:
        source = PROMPT_SOURCES[key]
        assert source.source_kind == "file"
        assert source.source_name.startswith("templates/hmas/")
        assert source.inline_text is None


@pytest.mark.unit
def test_hmas_prompt_registry_files_exist_in_prompt_directory() -> None:
    prompt_directory = Path(prompt_registry.__file__).parent
    hmas_source_files = [
        "templates/hmas/agent_policy.prompt.md",
        "templates/hmas/task_policy.prompt.md",
        "templates/hmas/profiles/planner.prompt.md",
        "templates/hmas/profiles/researcher.prompt.md",
        "templates/hmas/profiles/analyst.prompt.md",
        "templates/hmas/profiles/writer.prompt.md",
        "templates/hmas/profiles/reviewer.prompt.md",
        "templates/hmas/supervisor/system.prompt.md",
        "templates/hmas/supervisor/planning_policy.prompt.md",
        "templates/hmas/supervisor/delegation_brief.prompt.md",
        "templates/hmas/supervisor/aggregation_policy.prompt.md",
        "templates/hmas/supervisor/failure_policy.prompt.md",
    ]

    for relative_path in hmas_source_files:
        file_path = prompt_directory / relative_path
        assert file_path.exists(), f"Missing HMAS prompt file: {relative_path}"
