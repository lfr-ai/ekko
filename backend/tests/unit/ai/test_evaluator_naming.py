"""Tests for evaluator backtest naming and metadata."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ekko.ai.prompts.registry import PromptVersionInfo
from ekko.cli.evaluator import build_backtest_metadata, build_backtest_run_name


@pytest.mark.unit
def test_build_backtest_run_name_with_prompt_versions_includes_version_tokens() -> None:
    prompt_versions = {
        "summary_chunks": PromptVersionInfo(
            prompt_key="summary_chunks",
            version="v2",
            checksum="abc123",
            source_name="summary_prompt_chunks.txt",
            file_path=__file__,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            is_new=False,
        ),
        "conversational_system": PromptVersionInfo(
            prompt_key="conversational_system",
            version="v1",
            checksum="def456",
            source_name="templates.CONVERSATIONAL_SYSTEM",
            file_path=__file__,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            is_new=False,
        ),
    }

    run_name = build_backtest_run_name(
        dataset_label="customer-support-regression",
        model_label="gpt-4o-2024-08-06",
        prompt_versions=prompt_versions,
        now_utc=datetime(2026, 2, 3, 4, 5, 6, tzinfo=UTC),
    )

    assert "sumv2" in run_name
    assert "convv1" in run_name
    assert run_name.endswith("20260203-040506")


@pytest.mark.unit
def test_build_backtest_metadata_with_active_prompt_versions_returns_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompt_versions = {
        "summary_chunks": PromptVersionInfo(
            prompt_key="summary_chunks",
            version="v3",
            checksum="sum-check",
            source_name="summary_prompt_chunks.txt",
            file_path=__file__,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            is_new=True,
        ),
    }

    monkeypatch.setattr(
        "ekko.cli.evaluator.get_active_prompt_versions",
        lambda: prompt_versions,
    )

    metadata = build_backtest_metadata(
        dataset_label="eval-dataset",
        model_label="gpt-4o-mini",
        now_utc=datetime(2026, 2, 3, 4, 5, 6, tzinfo=UTC),
    )

    assert metadata["run_name"]
    assert metadata["dataset_label"] == "eval-dataset"
    assert metadata["model_label"] == "gpt-4o-mini"
    assert metadata["prompt_versions"]["summary_chunks"]["version"] == "v3"
