"""Static check for this skill's port/adapter inheritance contract.

Two read-only AST checks, neither reimplementing ty or ruff:

1. Any class whose name ends in `Port` must list `Protocol` among its bases —
   Core ports declare shape only, never behavior (Framework Independence).
2. Any class that subclasses a `*Port` base (an adapter) must decorate every
   public, non-factory method with `@override` — the project's Hard Rule
   that every port/adapter implementation carries `@override`. ty already
   type-checks `@override` when present; it has no rule requiring the
   decorator to be present at all, which is the gap this closes.

Usage:
    uv run python check_port_adapter_binding.py src/<pkg>

Exit codes:
    0 - no findings
    1 - at least one finding (printed to stdout, one per line)
    2 - usage error (path does not exist)
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

_PORT_SUFFIX = "Port"
_EXEMPT_METHOD_NAMES = frozenset({"__init__", "from_config"})


@dataclass(frozen=True, kw_only=True, slots=True)
class Finding:
    """One port/adapter contract observation."""

    path: Path
    line: int
    message: str

    def __str__(self) -> str:
        """Render as a `path:line: message` grep-friendly line."""
        return f"{self.path}:{self.line}: {self.message}"


def _base_names(node: ast.ClassDef) -> list[str]:
    """Collect the simple names of a class's direct base expressions."""
    names: list[str] = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


def _is_classmethod_or_staticmethod(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    """Whether a method is decorated `@classmethod` or `@staticmethod`."""
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id in {
            "classmethod",
            "staticmethod",
        }:
            return True
    return False


def _has_override_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Whether a method already carries `@override`."""
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "override":
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr == "override":
            return True
    return False


def _check_port_is_protocol(node: ast.ClassDef, *, path: Path) -> Iterator[Finding]:
    """Flag a `*Port`-named class that does not list `Protocol` as a base."""
    if node.name.endswith(_PORT_SUFFIX) and "Protocol" not in _base_names(node):
        yield Finding(
            path=path,
            line=node.lineno,
            message=(
                f"'{node.name}' ends in 'Port' but does not subclass Protocol — "
                "ports declare shape only, never behavior"
            ),
        )


def _check_adapter_overrides(node: ast.ClassDef, *, path: Path) -> Iterator[Finding]:
    """Flag an adapter (subclasses a `*Port` base) missing `@override` on a method."""
    if not any(base.endswith(_PORT_SUFFIX) for base in _base_names(node)):
        return
    for member in node.body:
        if not isinstance(member, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if member.name in _EXEMPT_METHOD_NAMES or member.name.startswith("_"):
            continue
        if _is_classmethod_or_staticmethod(member):
            continue
        if not _has_override_decorator(member):
            yield Finding(
                path=path,
                line=member.lineno,
                message=(
                    f"'{node.name}.{member.name}' implements a Port but is "
                    "missing @override"
                ),
            )


def check_file(path: Path) -> list[Finding]:
    """Run both checks against every class defined in one source file.

    Args:
        path (Path): Source file to inspect.

    Returns:
        list[Finding]: Findings for this file, in source order.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [
            Finding(path=path, line=exc.lineno or 0, message=f"unparsable: {exc.msg}")
        ]
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            findings.extend(_check_port_is_protocol(node, path=path))
            findings.extend(_check_adapter_overrides(node, path=path))
    return findings


def _iter_python_files(root: Path) -> Iterator[Path]:
    """Yield every `.py` file under `root`, skipping caches."""
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" not in path.parts:
            yield path


def main(argv: list[str] | None = None) -> int:
    """Scan a source tree and report port/adapter contract findings.

    Args:
        argv (list[str] | None): Command-line arguments, or None for `sys.argv`.

    Returns:
        int: Exit code — 0 clean, 1 findings, 2 usage error.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    args = parser.parse_args(argv)

    if not args.source_dir.is_dir():
        sys.stderr.write(f"error: not a directory: {args.source_dir}\n")
        return 2

    findings = [
        finding
        for path in _iter_python_files(args.source_dir)
        for finding in check_file(path)
    ]
    for finding in findings:
        sys.stdout.write(f"{finding}\n")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
