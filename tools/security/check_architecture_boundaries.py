"""Validate Clean Architecture import boundaries for the ekko package.

Enforces dependency rules:
  - config/ must not import from core/, application/, presentation/
  - core/ must not import from application/, infrastructure/, presentation/
  - ai/ must not import from infrastructure/, application/, presentation/
  - infrastructure/ must not import from application/, presentation/
  - application/ must not import from presentation/
  - presentation/ is the top layer (no restrictions on ekko.* imports)

Run locally or in CI to catch dependency violations early.
"""

from __future__ import annotations

import argparse
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
    """A dependency boundary violation.

    Attributes:
        file_path: Path to the file containing the violation.
        line_number: Line number where the violation occurs.
        line_text: The import statement text.
        layer: The layer containing the violating file.
        imported_layer: The layer being imported (causing the violation).
        reason: Human-readable explanation of why this is a violation.
    """

    file_path: Path
    line_number: int
    line_text: str
    layer: str
    imported_layer: str
    reason: str


def _collect_python_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if p.is_file())


def _check_config(files: list[Path]) -> list[Violation]:
    """Check that config/ does not import from core/, application/, or presentation/.

    Args:
        files: List of Python source files to check.

    Returns:
        List of violations found.
    """
    violations: list[Violation] = []
    forbidden = {"core", "application", "presentation"}
    for fp in files:
        if "/config/" not in fp.as_posix() and "\\config\\" not in str(fp):
            continue
        for idx, line in enumerate(
            fp.read_text(encoding="utf-8").splitlines(), start=1
        ):
            m = _IMPORT_PATTERN.search(line)
            if m and m.group("layer") in forbidden:
                imported_layer = m.group("layer")
                violations.append(
                    Violation(
                        fp,
                        idx,
                        line.strip(),
                        "config",
                        imported_layer,
                        "config/ must not import from core/, application/, or presentation/",
                    )
                )
    return violations


def _check_core(files: list[Path]) -> list[Violation]:
    """Check that core/ does not import from outer layers.

    Args:
        files: List of Python source files to check.

    Returns:
        List of violations found.
    """
    violations: list[Violation] = []
    for fp in files:
        if "/core/" not in fp.as_posix() and "\\core\\" not in str(fp):
            continue
        for idx, line in enumerate(
            fp.read_text(encoding="utf-8").splitlines(), start=1
        ):
            m = _IMPORT_PATTERN.search(line)
            if m and m.group("layer") in OUTER_LAYERS:
                imported_layer = m.group("layer")
                violations.append(
                    Violation(
                        fp,
                        idx,
                        line.strip(),
                        "core",
                        imported_layer,
                        "core/ must not depend on outer layers",
                    )
                )
    return violations


def _check_infrastructure(files: list[Path]) -> list[Violation]:
    """Check that infrastructure/ does not import from application/ or presentation/.

    Args:
        files: List of Python source files to check.

    Returns:
        List of violations found.
    """
    violations: list[Violation] = []
    forbidden = {"application", "presentation"}
    for fp in files:
        if "/infrastructure/" not in fp.as_posix() and "\\infrastructure\\" not in str(
            fp
        ):
            continue
        for idx, line in enumerate(
            fp.read_text(encoding="utf-8").splitlines(), start=1
        ):
            m = _IMPORT_PATTERN.search(line)
            if m and m.group("layer") in forbidden:
                imported_layer = m.group("layer")
                violations.append(
                    Violation(
                        fp,
                        idx,
                        line.strip(),
                        "infrastructure",
                        imported_layer,
                        "infrastructure/ must not import from application/ or presentation/",
                    )
                )
    return violations


def _check_application(files: list[Path]) -> list[Violation]:
    """Check that application/ does not import from presentation/.

    Args:
        files: List of Python source files to check.

    Returns:
        List of violations found.
    """
    violations: list[Violation] = []
    for fp in files:
        if "/application/" not in fp.as_posix() and "\\application\\" not in str(fp):
            continue
        for idx, line in enumerate(
            fp.read_text(encoding="utf-8").splitlines(), start=1
        ):
            m = _IMPORT_PATTERN.search(line)
            if m and m.group("layer") == "presentation":
                violations.append(
                    Violation(
                        fp,
                        idx,
                        line.strip(),
                        "application",
                        "presentation",
                        "application/ must not import from presentation/",
                    )
                )
    return violations


def _check_ai(files: list[Path]) -> list[Violation]:
    """Check that ai/ does not import from infrastructure/, application/, or presentation/.

    Args:
        files: List of Python source files to check.

    Returns:
        List of violations found.
    """
    violations: list[Violation] = []
    forbidden = {"infrastructure", "application", "presentation"}
    for fp in files:
        posix = fp.as_posix()
        if "/ai/" not in posix and "\\ai\\" not in str(fp):
            continue
        for idx, line in enumerate(
            fp.read_text(encoding="utf-8").splitlines(), start=1
        ):
            m = _IMPORT_PATTERN.search(line)
            if m and m.group("layer") in forbidden:
                imported_layer = m.group("layer")
                violations.append(
                    Violation(
                        fp,
                        idx,
                        line.strip(),
                        "ai",
                        imported_layer,
                        "ai/ must not import from infrastructure/, application/, or presentation/",
                    )
                )
    return violations


def main() -> int:
    """Run all architecture boundary checks.

    Returns:
        Process exit code (0 for success, 1 for violations or errors).
    """
    parser = argparse.ArgumentParser(
        description="Validate Clean Architecture import boundaries for the ekko package."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output including file paths, line numbers, and violation reasons",
    )
    args = parser.parse_args()

    if not SRC.exists():
        print(f"Source directory not found: {SRC}")
        return 1

    files = _collect_python_files(SRC)
    violations = [
        *_check_config(files),
        *_check_core(files),
        *_check_infrastructure(files),
        *_check_application(files),
        *_check_ai(files),
    ]

    if not violations:
        print("Clean Architecture boundaries OK")
        return 0

    print(f"Architecture violations ({len(violations)}):")
    if args.verbose:
        print()
        for v in violations:
            rel = v.file_path.relative_to(ROOT)
            print(f"  {rel}:{v.line_number}")
            print(f"    Layer: {v.layer} -> {v.imported_layer}")
            print(f"    Reason: {v.reason}")
            print(f"    Import: {v.line_text}")
            print()
    else:
        print()
        for v in violations:
            rel = v.file_path.relative_to(ROOT)
            print(f"  {rel}:{v.line_number}: {v.reason}")
            print(f"    -> {v.line_text}")

    if not args.verbose:
        print("\nRun with --verbose for detailed output")

    return 1


if __name__ == "__main__":
    sys.exit(main())
