"""Tests for prompt registry versioning and provisioning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from ekko.ai.prompts.registry import (
    PROMPT_KEY_SUMMARY_CHUNKS,
    PromptRegistryError,
    get_prompt_text,
    get_prompt_versions,
    provision_prompt,
)

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(slots=True)
class PromptSettingsStub:
    prompt_dir_path: Path
    prompt_version: str | None = None
    prompt_auto_provision: bool = True


@pytest.mark.unit
def test_provision_prompt_creates_first_version(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "summary_prompt_chunks.txt"
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    settings = PromptSettingsStub(prompt_dir_path=prompt_dir)
    info = provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    assert info.version == "v1"
    assert info.is_new is True
    assert info.file_path.exists()
    assert info.file_path.read_text(encoding="utf-8") == "Prompt V1: {content}"


@pytest.mark.unit
def test_provision_prompt_creates_new_version_on_source_change(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "summary_prompt_chunks.txt"
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    settings = PromptSettingsStub(prompt_dir_path=prompt_dir)
    first = provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    source_file.write_text("Prompt V2: {content}", encoding="utf-8")
    second = provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    assert first.version == "v1"
    assert second.version == "v2"

    versions = get_prompt_versions(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)
    assert [version.version for version in versions] == ["v1", "v2"]


@pytest.mark.unit
def test_get_prompt_text_respects_selected_version(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "summary_prompt_chunks.txt"
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    settings = PromptSettingsStub(prompt_dir_path=prompt_dir)
    provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    source_file.write_text("Prompt V2: {content}", encoding="utf-8")
    provision_prompt(prompt_key=PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)

    selected = PromptSettingsStub(
        prompt_dir_path=prompt_dir,
        prompt_version="v1",
        prompt_auto_provision=True,
    )
    text = get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=selected)
    assert text == "Prompt V1: {content}"


@pytest.mark.unit
def test_get_prompt_text_raises_for_unknown_version(tmp_path: Path) -> None:
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    source_file = prompt_dir / "summary_prompt_chunks.txt"
    source_file.write_text("Prompt V1: {content}", encoding="utf-8")

    settings = PromptSettingsStub(
        prompt_dir_path=prompt_dir,
        prompt_version="v9",
        prompt_auto_provision=True,
    )

    with pytest.raises(PromptRegistryError):
        get_prompt_text(PROMPT_KEY_SUMMARY_CHUNKS, settings=settings)
