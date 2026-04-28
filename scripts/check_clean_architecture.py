"""Lightweight Clean Architecture import checker.

Scans Python files under src/voice and ensures dependency direction follows:
  presentation/infrastructure -> application -> core

This is a heuristic tool to catch obvious violations; run locally and in CI.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "voice"

LAYER_ORDER = {
    "core": 0,
    "application": 1,
    "infrastructure": 2,
    "presentation": 2,
}


def detect_layer(path: Path) -> Optional[str]:
    parts = [p for p in path.parts]
    # look for one of the known layer names in the path
    for name in LAYER_ORDER.keys():
        if name in parts:
            return name
    return None


def module_layer(module_name: str) -> Optional[str]:
    # module_name like 'voice.application.services.chat'
    parts = module_name.split(".")
    for p in parts:
        if p in LAYER_ORDER:
            return p
    return None


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    src = path.read_text(encoding="utf8")
    try:
        tree = ast.parse(src)
    except Exception as e:
        errors.append(f"Failed to parse {path}: {e}")
        return errors

    origin_layer = detect_layer(path)
    if origin_layer is None:
        # file not in recognized layer; skip
        return errors

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("voice"):
                    target = module_layer(name)
                    if target and LAYER_ORDER[origin_layer] < LAYER_ORDER[target]:
                        errors.append(
                            f"Layer violation: {path} ({origin_layer}) -> imports {name} ({target})"
                        )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module
            if mod and mod.startswith("voice"):
                target = module_layer(mod)
                if target and LAYER_ORDER[origin_layer] < LAYER_ORDER[target]:
                    errors.append(
                        f"Layer violation: {path} ({origin_layer}) -> from {mod} import ... ({target})"
                    )

    return errors


def main() -> int:
    python_files = list(SRC.rglob("*.py"))
    violations: list[str] = []
    for f in python_files:
        # ignore tests and __init__.py stubs
        if "tests" in f.parts or f.name.startswith("test_"):
            continue
        errors = check_file(f)
        violations.extend(errors)

    if violations:
        print("Clean Architecture violations found:\n")
        for v in violations:
            print(v)
        return 1

    print("No obvious Clean Architecture violations detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
