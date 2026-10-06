"""Flag destructive/replace actions in a `terraform show -json <plan>` file.

Closes a real gap: static validation (`fmt`, `validate`, TFLint) never inspects
what a plan actually intends to DO to existing infrastructure. This script
reads the JSON plan Terraform already produces and prints every resource whose
planned action includes "delete" (destroy or destroy-then-create/replace),
grouped by resource address, so a reviewer sees the blast radius before
anyone applies it.

This script never runs `terraform` itself and never touches credentials or
state — it only parses a plan file already saved to disk:

    terraform plan -out=tfplan.binary
    terraform show -json tfplan.binary > plan.json
    uv run python check_terraform_plan.py plan.json

Exit codes:
    0 - no destroy/replace actions found
    1 - at least one destroy/replace action found (printed, one per resource)
    2 - usage error (file missing or not valid JSON with the expected shape)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_DESTRUCTIVE_ACTIONS = frozenset({"delete"})


def _as_dict(value: object) -> dict[str, object]:
    """Normalize an arbitrary JSON value into a plain `dict[str, object]`."""
    if not isinstance(value, dict):
        return {}
    normalized: dict[str, object] = {str(key): item for key, item in value.items()}
    return normalized


def _as_list(value: object) -> list[object]:
    """Normalize an arbitrary JSON value into a plain `list[object]`."""
    if not isinstance(value, list):
        return []
    normalized: list[object] = list(value)
    return normalized


def _resource_changes(plan: object) -> list[object]:
    if not isinstance(plan, dict):
        message = "plan root is not a JSON object"
        raise TypeError(message)
    return _as_list(_as_dict(plan).get("resource_changes"))


def _actions_of(change: object) -> list[object]:
    change_field = _as_dict(_as_dict(change).get("change"))
    return _as_list(change_field.get("actions"))


def _address_of(change: object) -> str:
    address = _as_dict(change).get("address")
    return address if isinstance(address, str) else "<unknown address>"


def _destructive_addresses(plan: object) -> list[str]:
    findings: list[str] = []
    for change in _resource_changes(plan):
        actions = _actions_of(change)
        if _DESTRUCTIVE_ACTIONS.intersection(actions):
            joined = "+".join(str(action) for action in actions)
            findings.append(f"{_address_of(change)}: {joined}")
    return findings


def main(argv: list[str] | None = None) -> int:
    """Parse the plan JSON file given on the CLI and report destructive actions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "plan_json",
        type=Path,
        help="path to a `terraform show -json <plan>` output file",
    )
    args = parser.parse_args(argv)

    if not args.plan_json.is_file():
        print(f"error: not a file: {args.plan_json}", file=sys.stderr)
        return 2

    try:
        plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
        findings = _destructive_addresses(plan)
    except (json.JSONDecodeError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not findings:
        print("No destroy/replace actions in this plan.")
        return 0

    print("Destructive actions in this plan:")
    for finding in findings:
        print(f"  {finding}")
    print(
        f"\n{len(findings)} resource(s) will be destroyed or replaced — "
        "confirm this is expected before applying."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
