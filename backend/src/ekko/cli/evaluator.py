"""Evaluator utilities for reproducible backtest naming and metadata."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from typing import Final

from ekko.ai.prompts import PromptVersionInfo, get_active_prompt_versions

DEFAULT_BACKTEST_PREFIX: Final[str] = "backtest"
_MAX_SEGMENT_LENGTH: Final[int] = 48
_MAX_RUN_NAME_LENGTH: Final[int] = 180
_INVALID_SLUG_PATTERN: Final[re.Pattern[str]] = re.compile(r"[^a-z0-9]+")

PROMPT_KEY_ALIASES: Final[dict[str, str]] = {
    "summary_chunks": "sum",
    "conversational_system": "conv",
}
NO_PROMPTS_SEGMENT: Final[str] = "noprompts"


def build_backtest_run_name(
    *,
    dataset_label: str,
    model_label: str,
    prefix: str = DEFAULT_BACKTEST_PREFIX,
    prompt_versions: dict[str, PromptVersionInfo] | None = None,
    now_utc: datetime | None = None,
) -> str:
    """Build a deterministic, prompt-version-aware backtest run name."""
    active_prompt_versions = get_active_prompt_versions() if prompt_versions is None else prompt_versions
    timestamp = (now_utc or datetime.now(tz=UTC)).strftime("%Y%m%d-%H%M%S")

    segments = [
        _slugify(value=prefix, fallback=DEFAULT_BACKTEST_PREFIX),
        _slugify(value=dataset_label, fallback="dataset"),
        _slugify(value=model_label, fallback="model"),
        _build_prompt_version_segment(prompt_versions=active_prompt_versions),
        timestamp,
    ]
    run_name = "-".join(segments)
    return run_name[:_MAX_RUN_NAME_LENGTH]


def build_backtest_metadata(
    *,
    dataset_label: str,
    model_label: str,
    prefix: str = DEFAULT_BACKTEST_PREFIX,
    now_utc: datetime | None = None,
) -> dict[str, object]:
    """Build structured backtest metadata with prompt version traceability."""
    active_prompt_versions = get_active_prompt_versions()
    effective_now = now_utc or datetime.now(tz=UTC)

    run_name = build_backtest_run_name(
        dataset_label=dataset_label,
        model_label=model_label,
        prefix=prefix,
        prompt_versions=active_prompt_versions,
        now_utc=effective_now,
    )
    prompt_metadata = {
        prompt_key: {
            "version": info.version,
            "checksum": info.checksum,
            "source_name": info.source_name,
            "created_at": info.created_at.isoformat(),
        }
        for prompt_key, info in sorted(active_prompt_versions.items())
    }

    return {
        "run_name": run_name,
        "dataset_label": dataset_label,
        "model_label": model_label,
        "generated_at": effective_now.isoformat(),
        "prompt_versions": prompt_metadata,
    }


def _build_prompt_version_segment(*, prompt_versions: dict[str, PromptVersionInfo]) -> str:
    if not prompt_versions:
        return NO_PROMPTS_SEGMENT

    segments = []
    for prompt_key, info in sorted(prompt_versions.items()):
        alias = PROMPT_KEY_ALIASES.get(prompt_key, prompt_key)
        alias_slug = _slugify(value=alias, fallback="prompt")
        version_slug = _slugify(value=info.version, fallback="source")
        segments.append(f"{alias_slug}{version_slug}")

    return ".".join(segments)


def _slugify(*, value: str, fallback: str) -> str:
    lowered = value.strip().lower()
    normalized = _INVALID_SLUG_PATTERN.sub("-", lowered).strip("-")
    if not normalized:
        normalized = fallback
    return normalized[:_MAX_SEGMENT_LENGTH]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluator utilities for backtest naming and metadata",
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    run_name_parser = subparsers.add_parser(
        "run-name",
        help="Generate a backtest run name that includes prompt versions",
    )
    run_name_parser.add_argument("--dataset-label", required=True, help="Dataset identifier")
    run_name_parser.add_argument("--model-label", required=True, help="Model identifier")
    run_name_parser.add_argument(
        "--prefix",
        default=DEFAULT_BACKTEST_PREFIX,
        help="Optional run name prefix",
    )

    metadata_parser = subparsers.add_parser(
        "metadata",
        help="Generate backtest metadata payload including prompt versions",
    )
    metadata_parser.add_argument("--dataset-label", required=True, help="Dataset identifier")
    metadata_parser.add_argument("--model-label", required=True, help="Model identifier")
    metadata_parser.add_argument(
        "--prefix",
        default=DEFAULT_BACKTEST_PREFIX,
        help="Optional run name prefix",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    command = args.command or "run-name"

    if command == "run-name":
        _emit_json(
            {
                "run_name": build_backtest_run_name(
                    dataset_label=args.dataset_label,
                    model_label=args.model_label,
                    prefix=args.prefix,
                ),
            },
        )
        return

    if command == "metadata":
        _emit_json(
            build_backtest_metadata(
                dataset_label=args.dataset_label,
                model_label=args.model_label,
                prefix=args.prefix,
            ),
        )
        return

    parser.error(f"Unknown command: {command}")


def _emit_json(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
