"""Validate Clean Architecture import boundaries for the voice package."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Violation:
    """Represents a dependency boundary violation."""

    file_path: Path
    line_number: int
    line_text: str
    reason: str


_IMPORT_PATTERN = re.compile(r"^\s*(?:from|import)\s+voice\.(?P<layer>\w+)")


def _collect_python_files(*, root: Path) -> list[Path]:
    return [path for path in root.rglob("*.py") if path.is_file()]


def _check_core_boundaries(*, files: list[Path]) -> list[Violation]:
    violations: list[Violation] = []
    disallowed_layers = {"application", "infrastructure", "presentation", "interaction", "models", "managers"}

    for file_path in files:
        relative = file_path.as_posix()
        if "/core/" not in relative:
            continue
        for idx, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
            match = _IMPORT_PATTERN.search(line)
            if not match:
                continue
            layer = match.group("layer")
            if layer in disallowed_layers:
                violations.append(
                    Violation(
                        file_path=file_path,
                        line_number=idx,
                        line_text=line.strip(),
                        reason="core must not depend on outer layers",
                    )
                )

    return violations


def _check_application_boundaries(*, files: list[Path]) -> list[Violation]:
    violations: list[Violation] = []

    for file_path in files:
        relative = file_path.as_posix()
        if "/application/" not in relative:
            continue
        for idx, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
            match = _IMPORT_PATTERN.search(line)
            if not match:
                continue
            if match.group("layer") == "infrastructure":
                violations.append(
                    Violation(
                        file_path=file_path,
                        line_number=idx,
                        line_text=line.strip(),
                        reason="application must depend on abstractions, not infrastructure",
                    )
                )

    return violations


def main() -> int:
    """Run architecture boundary checks.

    Returns:
        Process exit code.
    """

    root = Path("src") / "voice"
    if not root.exists():
        print("No src/voice directory found; skipping architecture checks.")
        return 0

    files = _collect_python_files(root=root)
    violations = [
        *_check_core_boundaries(files=files),
        *_check_application_boundaries(files=files),
    ]

    if not violations:
        print("Clean Architecture boundaries OK")
        return 0

    print("Clean Architecture boundary violations detected:")
    for violation in violations:
        rel_path = violation.file_path.as_posix()
        print(f"- {rel_path}:{violation.line_number}: {violation.reason}")
        print(f"  -> {violation.line_text}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
