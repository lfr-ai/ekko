"""Validate Clean Architecture import boundaries for the ekko package.

Enforces dependency rules:
  - core must not import from application, infrastructure, or presentation
  - application must not import from infrastructure or presentation
  - presentation must not import from infrastructure (except via composition/)
  - ai must not import from infrastructure

Run locally or in CI to catch dependency violations early.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "backend" / "src" / "ekko"

_IMPORT_PATTERN = re.compile(r"^\s*(?:from|import)\s+ekko\.(?P<layer>\w+)")

OUTER_LAYERS = {"application", "infrastructure", "presentation", "managers"}


@dataclass(frozen=True, slots=True)
class Violation:
    """A dependency boundary violation."""

    file_path: Path
    line_number: int
    line_text: str
    reason: str


def _collect_python_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if p.is_file())


def _check_core(files: list[Path]) -> list[Violation]:
    violations: list[Violation] = []
    for fp in files:
        if "/core/" not in fp.as_posix() and "\\core\\" not in str(fp):
            continue
        for idx, line in enumerate(fp.read_text(encoding="utf-8").splitlines(), start=1):
            m = _IMPORT_PATTERN.search(line)
            if m and m.group("layer") in OUTER_LAYERS:
                violations.append(Violation(fp, idx, line.strip(), "core must not depend on outer layers"))
    return violations


def _check_application(files: list[Path]) -> list[Violation]:
    violations: list[Violation] = []
    for fp in files:
        if "/application/" not in fp.as_posix() and "\\application\\" not in str(fp):
            continue
        for idx, line in enumerate(fp.read_text(encoding="utf-8").splitlines(), start=1):
            m = _IMPORT_PATTERN.search(line)
            if m and m.group("layer") in {"infrastructure", "presentation"}:
                violations.append(Violation(fp, idx, line.strip(), "application must not import infrastructure/presentation"))
    return violations


def _check_ai(files: list[Path]) -> list[Violation]:
    violations: list[Violation] = []
    for fp in files:
        posix = fp.as_posix()
        if "/ai/" not in posix and "\\ai\\" not in str(fp):
            continue
        for idx, line in enumerate(fp.read_text(encoding="utf-8").splitlines(), start=1):
            m = _IMPORT_PATTERN.search(line)
            if m and m.group("layer") == "infrastructure":
                violations.append(Violation(fp, idx, line.strip(), "ai must not import from infrastructure"))
    return violations


def _check_presentation(files: list[Path]) -> list[Violation]:
    violations: list[Violation] = []
    for fp in files:
        posix = fp.as_posix()
        if "/presentation/" not in posix and "\\presentation\\" not in str(fp):
            continue
        for idx, line in enumerate(fp.read_text(encoding="utf-8").splitlines(), start=1):
            m = _IMPORT_PATTERN.search(line)
            if m and m.group("layer") == "infrastructure":
                violations.append(Violation(fp, idx, line.strip(), "presentation must not import from infrastructure"))
    return violations


def main() -> int:
    """Run all architecture boundary checks.

    Returns:
        Process exit code.
    """
    if not SRC.exists():
        print(f"Source directory not found: {SRC}")
        return 1

    files = _collect_python_files(SRC)
    violations = [
        *_check_core(files),
        *_check_application(files),
        *_check_ai(files),
        *_check_presentation(files),
    ]

    if not violations:
        print("Clean Architecture boundaries OK")
        return 0

    print(f"Architecture violations ({len(violations)}):\n")
    for v in violations:
        rel = v.file_path.relative_to(ROOT)
        print(f"  {rel}:{v.line_number}: {v.reason}")
        print(f"    -> {v.line_text}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
