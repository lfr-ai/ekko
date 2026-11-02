"""Check file/folder naming conventions the `consistency` skill documents.

Ruff/Biome catch symbol-level naming (classes, functions) but not filesystem
naming. This script checks the two conventions `consistency` documents:

- Python files and folders under `src`/`tests` use ``snake_case``.
- TypeScript/TSX files under a frontend `src` use ``kebab-case``.

Run standalone::

    uv run python .agents/skills/consistency/scripts/check_naming.py [path ...]

Exit status is non-zero when any violation is found.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

_DEFAULT_PYTHON_ROOTS = (
    Path("src"),
    Path("tests"),
    Path("backend/src"),
    Path("backend/tests"),
    Path("backend/alembic"),
    Path("scripts"),
    Path("tools"),
    Path("registry"),
)
_DEFAULT_FRONTEND_ROOTS = (Path("frontend/src"),)
_SNAKE_CASE = re.compile(r"^[a-z0-9_]+$")
_KEBAB_CASE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_PYTHON_IGNORED_NAMES = frozenset({"__pycache__"})


@dataclass(frozen=True, kw_only=True, slots=True)
class NamingViolation:
    """One filesystem-naming convention breach."""

    path: Path
    rule: str
    message: str


def _python_naming_violations(root: Path) -> Iterator[NamingViolation]:
    """Flag Python files/folders under a root that are not snake_case.

    Only directories that directly contain a `.py` file are checked — this
    keeps resource-only folders (e.g. `prompts/versions/*/v1.0/*.prompt.md`)
    out of scope, since the convention targets Python packages, not data.

    Args:
        root (Path): Directory to scan (e.g. ``src`` or ``tests``).

    Yields:
        NamingViolation: One per non-compliant file or package-folder name.
    """
    if not root.is_dir():
        return
    package_dirs = {path.parent for path in root.rglob("*.py")}
    for path in root.rglob("*"):
        if path.name in _PYTHON_IGNORED_NAMES or path.name.startswith("."):
            continue
        if path.is_dir():
            if path not in package_dirs:
                continue
            stem, kind = path.name, "folder"
        elif path.suffix == ".py":
            stem, kind = path.stem, "file"
        else:
            continue
        if not _SNAKE_CASE.match(stem):
            yield NamingViolation(
                path=path,
                rule="python-snake-case",
                message=f"{kind} name '{path.name}' is not snake_case",
            )


def _frontend_naming_violations(root: Path) -> Iterator[NamingViolation]:
    """Flag TypeScript files under a frontend root that are not kebab-case.

    Args:
        root (Path): Frontend source directory (e.g. ``frontend/src``).

    Yields:
        NamingViolation: One per non-compliant file name.
    """
    if not root.is_dir():
        return
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx"}:
            continue
        if path.stem in {"vite-env.d", "vite.config", "vitest.config"}:
            continue
        stem = path.stem
        stem = stem.removesuffix(".d")
        if not _KEBAB_CASE.match(stem):
            yield NamingViolation(
                path=path,
                rule="frontend-kebab-case",
                message=f"file name '{path.name}' is not kebab-case",
            )


def check_naming(*, python_roots: Sequence[Path], frontend_roots: Sequence[Path]) -> list[NamingViolation]:
    """Run every naming check against the given Python and frontend roots.

    Args:
        python_roots (Sequence[Path]): Python directories to scan.
        frontend_roots (Sequence[Path]): Frontend source directories to scan.

    Returns:
        list[NamingViolation]: All violations found, unsorted.
    """
    violations: list[NamingViolation] = []
    for root in python_roots:
        violations.extend(_python_naming_violations(root))
    for root in frontend_roots:
        violations.extend(_frontend_naming_violations(root))
    return violations


def _report(violations: list[NamingViolation]) -> int:
    """Write a human-readable report and compute the process exit code.

    Args:
        violations (list[NamingViolation]): Violations to report.

    Returns:
        int: ``0`` when there are no violations, otherwise ``1``.
    """
    if not violations:
        sys.stdout.write("consistency: no naming violations found.\n")
        return 0
    sys.stderr.write("consistency: naming violations found:\n")
    for violation in sorted(violations, key=lambda v: str(v.path)):
        sys.stderr.write(f"  - {violation.path} [{violation.rule}] {violation.message}\n")
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the naming checks and return a process exit code.

    Args:
        argv (Sequence[str] | None): Optional CLI arguments naming
            directories to scan; defaults to the repository's `src`/`tests`
            and `frontend/src` (when present).

    Returns:
        int: ``0`` on success, ``1`` when violations are found.
    """
    args = list(argv if argv is not None else sys.argv[1:])
    if args:
        return _report(check_naming(python_roots=[Path(arg) for arg in args], frontend_roots=[]))
    return _report(check_naming(python_roots=_DEFAULT_PYTHON_ROOTS, frontend_roots=_DEFAULT_FRONTEND_ROOTS))


if __name__ == "__main__":
    raise SystemExit(main())
