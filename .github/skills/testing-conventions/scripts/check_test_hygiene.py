"""Guard fast-tier test speed hygiene that ruff's `PT` rules do not cover.

The fast tier (`pytest -m "not slow"` — every `tests/unit` and `tests/property`
module) runs on every commit and in the agentic dev loop, so its collection and
execution cost must stay low. Ruff polices pytest *API* usage, never *import
weight* or *wall-clock blocking*. This script adds two static, false-positive-free
checks against the two ways a fast test silently gets slow:

- ``heavy-top-level-import``: a fast-tier module importing a multi-second import
  chain (``langsmith``, ``langchain``, ``matplotlib``, ``seaborn``, ``plotly``)
  at module top level. Such libraries load during *collection* — before a single
  assertion runs, and even when the test is deselected — and belong to
  `slow`/`integration`-scoped tests or scripts, never a fast unit test. Defer the
  import into the test body if one genuinely needs it.
- ``real-sleep``: a fast-tier module calling ``time.sleep()`` (a real wall-clock
  block). Fast tests must mock time or patch the sleeping call (e.g.
  ``tenacity``'s ``nap`` hook) instead of blocking — a handful of 5-second sleeps
  is enough to dominate the whole tier.

Run standalone::

    uv run python .agents/skills/testing-conventions/scripts/check_test_hygiene.py [dir ...]

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

# The always-run tiers. Docker-backed `integration` tests are auto-marked `slow`
# and excluded from the fast tier, so their heavier imports are out of scope.
_DEFAULT_FAST_TIER_ROOTS = (Path("tests/unit"), Path("tests/property"))

# Top-level packages whose import pulls a multi-second dependency graph a fast
# unit/property test never needs. `litellm`, `polars`, and `duckdb` are
# deliberately absent: specific unit tests exercise code that requires them, so
# banning them outright would be a false positive.
_HEAVY_TOP_LEVEL_IMPORTS = frozenset(
    {"langchain", "langsmith", "matplotlib", "plotly", "seaborn"}
)


@dataclass(frozen=True, kw_only=True, slots=True)
class HygieneViolation:
    """One fast-tier speed-hygiene breach found in a test module."""

    file: Path
    line: int
    rule: str
    message: str


def _iter_test_modules(root: Path) -> Iterator[Path]:
    """Yield every collectable test module under a fast-tier directory.

    Args:
        root (Path): Fast-tier directory to scan.

    Yields:
        Path: Each ``.py`` file except packaging/fixture modules.
    """
    for path in root.rglob("*.py"):
        if path.name not in {"__init__.py", "conftest.py"}:
            yield path


def _top_level_module(node: ast.Import | ast.ImportFrom) -> Iterator[tuple[str, int]]:
    """Yield the root package name and line for each name an import introduces.

    Args:
        node (ast.Import | ast.ImportFrom): Import statement node.

    Yields:
        tuple[str, int]: The top-level package name and its source line.
    """
    if isinstance(node, ast.ImportFrom):
        if node.level == 0 and node.module is not None:
            yield node.module.split(".", 1)[0], node.lineno
        return
    for alias in node.names:
        yield alias.name.split(".", 1)[0], node.lineno


def _heavy_import_violations(
    file: Path, tree: ast.Module
) -> Iterator[HygieneViolation]:
    """Flag top-level imports of a banned heavy package in a fast-tier module.

    Only module-level imports count: an import nested inside a function body is
    already deferred and does not cost collection time.

    Args:
        file (Path): Module being checked.
        tree (ast.Module): Parsed module AST.

    Yields:
        HygieneViolation: One per banned top-level import.
    """
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        for package, line in _top_level_module(node):
            if package in _HEAVY_TOP_LEVEL_IMPORTS:
                yield HygieneViolation(
                    file=file,
                    line=line,
                    rule="heavy-top-level-import",
                    message=(
                        f"fast-tier test imports heavy package '{package}' at module "
                        "top level (loads during collection) — defer it into the test "
                        "body or move the test to the `slow` tier"
                    ),
                )


def _imports_bare_sleep_from_time(tree: ast.Module) -> bool:
    """Detect a ``from time import sleep`` binding in a module.

    Args:
        tree (ast.Module): Parsed module AST.

    Returns:
        bool: 'True' when the bare name ``sleep`` refers to ``time.sleep``.
    """
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "time"
            and any(alias.name == "sleep" for alias in node.names)
        ):
            return True
    return False


def _is_real_sleep_call(node: ast.Call, *, bare_sleep_is_time: bool) -> bool:
    """Decide whether a call node is a real ``time.sleep`` wall-clock block.

    ``asyncio.sleep`` is intentionally excluded — it yields to the event loop
    rather than blocking a worker.

    Args:
        node (ast.Call): Call expression to classify.
        bare_sleep_is_time (bool): Whether a bare ``sleep`` name is ``time.sleep``.

    Returns:
        bool: 'True' when the call blocks on real time.
    """
    func = node.func
    if isinstance(func, ast.Attribute):
        return (
            func.attr == "sleep"
            and isinstance(func.value, ast.Name)
            and func.value.id == "time"
        )
    if isinstance(func, ast.Name):
        return func.id == "sleep" and bare_sleep_is_time
    return False


def _real_sleep_violations(file: Path, tree: ast.Module) -> Iterator[HygieneViolation]:
    """Flag real ``time.sleep()`` calls anywhere in a fast-tier module.

    Args:
        file (Path): Module being checked.
        tree (ast.Module): Parsed module AST.

    Yields:
        HygieneViolation: One per real-sleep call site.
    """
    bare_sleep_is_time = _imports_bare_sleep_from_time(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_real_sleep_call(
            node, bare_sleep_is_time=bare_sleep_is_time
        ):
            yield HygieneViolation(
                file=file,
                line=node.lineno,
                rule="real-sleep",
                message=(
                    "fast-tier test calls real time.sleep() — patch the sleeping "
                    "call (e.g. tenacity's nap hook) or mock time instead of blocking"
                ),
            )


def check_test_hygiene(roots: Sequence[Path]) -> list[HygieneViolation]:
    """Run every hygiene check against every fast-tier module under the roots.

    Args:
        roots (Sequence[Path]): Fast-tier directories to scan.

    Returns:
        list[HygieneViolation]: All violations found, unsorted.
    """
    violations: list[HygieneViolation] = []
    for root in roots:
        if not root.is_dir():
            continue
        for file in _iter_test_modules(root):
            tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
            violations.extend(_heavy_import_violations(file, tree))
            violations.extend(_real_sleep_violations(file, tree))
    return violations


def _report(violations: list[HygieneViolation]) -> int:
    """Write a human-readable report and compute the process exit code.

    Args:
        violations (list[HygieneViolation]): Violations to report.

    Returns:
        int: ``0`` when there are no violations, otherwise ``1``.
    """
    if not violations:
        sys.stdout.write(
            "testing-conventions: no fast-tier speed-hygiene violations found.\n"
        )
        return 0
    sys.stderr.write("testing-conventions: fast-tier speed-hygiene violations found:\n")
    for violation in sorted(violations, key=lambda v: (str(v.file), v.line)):
        sys.stderr.write(
            f"  - {violation.file}:{violation.line} [{violation.rule}] {violation.message}\n"
        )
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the fast-tier hygiene checks and return a process exit code.

    Args:
        argv (Sequence[str] | None): Optional CLI arguments; positional arguments
            override the default fast-tier roots.

    Returns:
        int: ``0`` on success, ``1`` when violations are found.
    """
    args = list(argv if argv is not None else sys.argv[1:])
    roots = tuple(Path(arg) for arg in args) if args else _DEFAULT_FAST_TIER_ROOTS
    return _report(check_test_hygiene(roots))


if __name__ == "__main__":
    raise SystemExit(main())
