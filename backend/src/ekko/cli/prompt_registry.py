"""CLI for prompt registry provisioning and inspection."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from ekko.ai.prompts import (
    PROMPT_KEY_CONVERSATIONAL_SYSTEM,
    PROMPT_KEY_SUMMARY_CHUNKS,
    get_active_prompt_version,
    get_active_prompt_versions,
    get_prompt_version_info,
    get_prompt_versions,
    provision_all_prompts,
)

PROMPT_KEYS: tuple[str, str] = (
    PROMPT_KEY_SUMMARY_CHUNKS,
    PROMPT_KEY_CONVERSATIONAL_SYSTEM,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prompt registry management")
    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("provision", help="Provision all known prompts")

    list_parser = subparsers.add_parser("list", help="List provisioned prompt versions")
    list_parser.add_argument(
        "--prompt-key",
        choices=PROMPT_KEYS,
        help="Optional prompt key filter",
    )

    active_parser = subparsers.add_parser("active", help="Show active prompt versions")
    active_parser.add_argument(
        "--prompt-key",
        choices=PROMPT_KEYS,
        help="Optional prompt key filter",
    )

    resolve_parser = subparsers.add_parser(
        "resolve",
        help="Resolve a specific prompt key/version to metadata",
    )
    resolve_parser.add_argument(
        "--prompt-key",
        required=True,
        choices=PROMPT_KEYS,
        help="Prompt key to resolve",
    )
    resolve_parser.add_argument(
        "--version",
        required=True,
        help="Prompt version to resolve (for example: v2)",
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
            else list(PROMPT_KEYS)
        )
        output: dict[str, list[dict[str, object]]] = {}
        for key in prompt_keys:
            output[key] = [asdict(item) for item in get_prompt_versions(key)]
        _emit_json(output)
        return

    if command == "active":
        if args.prompt_key:
            _emit_json(asdict(get_active_prompt_version(args.prompt_key)))
            return

        output = {
            key: asdict(info)
            for key, info in get_active_prompt_versions().items()
        }
        _emit_json(output)
        return

    if command == "resolve":
        resolved = get_prompt_version_info(
            prompt_key=args.prompt_key,
            version=args.version,
        )
        if resolved is None:
            parser.error(
                f"Prompt version '{args.version}' was not found for key '{args.prompt_key}'.",
            )
        _emit_json(asdict(resolved))
        return

    parser.error(f"Unknown command: {command}")


def _emit_json(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
