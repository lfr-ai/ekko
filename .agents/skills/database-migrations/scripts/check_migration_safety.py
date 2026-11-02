"""Static safety review for one Alembic migration file.

Closes a real gap: nothing in the repo's ruff/ty/pre-commit configuration
understands Alembic migration semantics, so risky patterns documented in the
`database-migrations` skill's Guardrails section (never edit an applied
migration, add columns nullable-then-tighten, keep schema/data changes
separate) go unchecked until a human reviewer happens to notice them.

This script is read-only: it never connects to a database and never imports
the target file (avoids executing arbitrary migration code). It parses the
migration's AST and flags patterns that are safe to autogenerate but unsafe to
apply directly against a live table without a follow-up step.

Usage:
    uv run python check_migration_safety.py alembic/versions/2026..._add_x.py
    uv run python check_migration_safety.py alembic/versions/*.py

Exit codes:
    0 - no findings in any file
    1 - at least one finding (printed to stdout, one per line)
    2 - usage error (no files given, or a file could not be parsed)
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

_RISKY_OP_CALLS = frozenset({"drop_column", "drop_table", "rename_table"})


@dataclass(frozen=True, kw_only=True, slots=True)
class Finding:
    """One safety observation about a migration file."""

    path: Path
    line: int
    message: str

    def __str__(self) -> str:
        """Render as a `path:line: message` grep-friendly line."""
        return f"{self.path}:{self.line}: {self.message}"


def _iter_op_calls(tree: ast.Module) -> Iterator[tuple[ast.Call, str]]:
    """Yield every `op.<name>(...)` Alembic operation call in the module."""
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "op"
        ):
            yield node, node.func.attr


def _keyword_value(call: ast.Call, *, name: str) -> ast.expr | None:
    """Find a call's keyword argument value by name, or None if absent."""
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _check_destructive_ops(tree: ast.Module, *, path: Path) -> Iterator[Finding]:
    """Flag drop/rename operations that are irreversible against live data."""
    for call, name in _iter_op_calls(tree):
        if name in _RISKY_OP_CALLS:
            yield Finding(
                path=path,
                line=call.lineno,
                message=(
                    f"op.{name}(...) is destructive/irreversible against a live "
                    "table — confirm downgrade() restores it and that a prior "
                    "release stopped reading the old shape first"
                ),
            )


def _check_tightened_nullable(tree: ast.Module, *, path: Path) -> Iterator[Finding]:
    """Flag alter_column(nullable=False) applied in a single step."""
    for call, name in _iter_op_calls(tree):
        if name != "alter_column":
            continue
        nullable = _keyword_value(call, name="nullable")
        if isinstance(nullable, ast.Constant) and nullable.value is False:
            yield Finding(
                path=path,
                line=call.lineno,
                message=(
                    "op.alter_column(..., nullable=False) tightens an existing "
                    "column directly — add it nullable, backfill in a separate "
                    "migration, then tighten, unless the table is known-empty"
                ),
            )


def _is_docstring_statement(stmt: ast.stmt) -> bool:
    """True for a bare string-literal statement (a docstring, not a call)."""
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and isinstance(stmt.value.value, str)
    )


def _check_empty_downgrade(tree: ast.Module, *, path: Path) -> Iterator[Finding]:
    """Flag a `downgrade()` whose body is only `pass` (or a docstring)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "downgrade":
            body = [stmt for stmt in node.body if not _is_docstring_statement(stmt)]
            if all(isinstance(stmt, ast.Pass) for stmt in body):
                yield Finding(
                    path=path,
                    line=node.lineno,
                    message=(
                        "downgrade() is a no-op — confirm this is intentional "
                        "(e.g. genuinely irreversible data change) rather than "
                        "an incomplete autogenerate"
                    ),
                )


_CHECKS = (_check_destructive_ops, _check_tightened_nullable, _check_empty_downgrade)


def _check_file(path: Path) -> list[Finding] | None:
    """Run every check against one migration file, or None if unparsable."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return None
    findings: list[Finding] = []
    for check in _CHECKS:
        findings.extend(check(tree, path=path))
    return findings


def main(argv: list[str] | None = None) -> int:
    """Run the safety checks over each migration file given on the CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "migration_files",
        nargs="+",
        type=Path,
        help="one or more Alembic migration files (alembic/versions/*.py)",
    )
    args = parser.parse_args(argv)

    all_findings: list[Finding] = []
    for path in args.migration_files:
        if not path.is_file():
            print(f"error: not a file: {path}", file=sys.stderr)
            return 2
        findings = _check_file(path)
        if findings is None:
            print(f"error: could not parse as Python: {path}", file=sys.stderr)
            return 2
        all_findings.extend(findings)

    for finding in all_findings:
        print(finding)

    if all_findings:
        print(f"\n{len(all_findings)} finding(s) — review before merging.")
        return 1
    print("No safety findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
