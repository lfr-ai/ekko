"""Check pytest naming conventions ruff's pytest-style rules (PT) don't cover.

Ruff's `PT` rules police pytest API usage (fixture scope, `raises` style, etc.)
but not filename/class naming. This script checks the two naming conventions
`testing-conventions` documents:

- Every test file matches ``test_*.py``.
- Every class defined in a test file starts with ``Test``.

Run standalone::

    uv run python .agents/skills/testing-conventions/scripts/check_test_naming.py [dir]

Exit status is non-zero when any violation is found.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

_DEFAULT_TESTS_DIR = Path("tests")


@dataclass(frozen=True, kw_only=True, slots=True)
class NamingViolation:
    """One test-naming convention breach found in a test tree."""

    file: Path
    line: int
    rule: str
    message: str


def _iter_python_files(root: Path) -> Iterator[Path]:
    """Yield every `.py` file under a directory, skipping `conftest.py`.

    Args:
        root (Path): Directory to scan.

    Yields:
        Path: Each candidate test file.
    """
    for path in root.rglob("*.py"):
        if path.name not in {"conftest.py", "__init__.py"}:
            yield path


def _file_name_violations(file: Path) -> Iterator[NamingViolation]:
    """Flag test files whose name does not start with `test_`.

    Args:
        file (Path): File to check.

    Yields:
        NamingViolation: At most one, for a non-compliant filename.
    """
    if not file.name.startswith("test_"):
        yield NamingViolation(
            file=file,
            line=1,
            rule="test-file-name",
            message=f"test file '{file.name}' does not match 'test_{{module}}.py'",
        )


def _class_name_violations(file: Path) -> Iterator[NamingViolation]:
    """Flag public classes defined in a test file that do not start with `Test`.

    Private test-double helpers (``_FakeRepo``, ``_DummyModel``, ...) are
    exempt: pytest never collects them, and the `consistency` skill requires
    marking such helpers with a leading underscore instead of naming them
    like a collected test class.

    Args:
        file (Path): File to check.

    Yields:
        NamingViolation: One per non-compliant public class definition.
    """
    tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        is_uncollected_helper = node.name.startswith(("_", "Test"))
        if not is_uncollected_helper:
            yield NamingViolation(
                file=file,
                line=node.lineno,
                rule="test-class-name",
                message=f"class '{node.name}' does not match 'Test{{ClassName}}'",
            )


def check_test_naming(root: Path) -> list[NamingViolation]:
    """Run every naming check against every test file under a directory.

    Args:
        root (Path): Test directory to scan (e.g. ``tests``).

    Returns:
        list[NamingViolation]: All violations found, unsorted.
    """
    violations: list[NamingViolation] = []
    for file in _iter_python_files(root):
        violations.extend(_file_name_violations(file))
        violations.extend(_class_name_violations(file))
    return violations


def _report(violations: list[NamingViolation]) -> int:
    """Write a human-readable report and compute the process exit code.

    Args:
        violations (list[NamingViolation]): Violations to report.

    Returns:
        int: ``0`` when there are no violations, otherwise ``1``.
    """
    if not violations:
        sys.stdout.write("testing-conventions: no naming violations found.\n")
        return 0
    sys.stderr.write("testing-conventions: naming violations found:\n")
    for violation in sorted(violations, key=lambda v: (str(v.file), v.line)):
        sys.stderr.write(
            f"  - {violation.file}:{violation.line} [{violation.rule}] "
            f"{violation.message}\n"
        )
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the test-naming checks and return a process exit code.

    Args:
        argv (Sequence[str] | None): Optional CLI arguments; the first
            positional argument overrides the default ``tests`` directory.

    Returns:
        int: ``0`` on success, ``1`` when violations are found.
    """
    args = list(argv if argv is not None else sys.argv[1:])
    root = Path(args[0]) if args else _DEFAULT_TESTS_DIR
    return _report(check_test_naming(root))


if __name__ == "__main__":
    raise SystemExit(main())
