"""CLI for prompt registry provisioning and inspection."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from ekko.ai.prompts import (
    PROMPT_KEY_CONVERSATIONAL_SYSTEM,
    PROMPT_KEY_SUMMARY_CHUNKS,
    get_prompt_versions,
    provision_all_prompts,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prompt registry management")
    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("provision", help="Provision all known prompts")

    list_parser = subparsers.add_parser("list", help="List provisioned prompt versions")
    list_parser.add_argument(
        "--prompt-key",
        choices=[PROMPT_KEY_SUMMARY_CHUNKS, PROMPT_KEY_CONVERSATIONAL_SYSTEM],
        help="Optional prompt key filter",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    command = args.command or "provision"
    if command == "provision":
        records = [asdict(record) for record in provision_all_prompts()]
        _emit_json(records)
        return

    if command == "list":
        prompt_keys = (
            [args.prompt_key]
            if args.prompt_key
            else [PROMPT_KEY_SUMMARY_CHUNKS, PROMPT_KEY_CONVERSATIONAL_SYSTEM]
        )
        output: dict[str, list[dict[str, object]]] = {}
        for key in prompt_keys:
            output[key] = [asdict(item) for item in get_prompt_versions(key)]
        _emit_json(output)
        return

    parser.error(f"Unknown command: {command}")


def _emit_json(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
