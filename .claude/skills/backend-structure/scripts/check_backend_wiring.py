"""Static check for backend-structure's presentation-boundary conventions.

`import-linter` (the `clean-architecture` skill) already enforces layer-level
import direction. It does not know about these two finer-grained rules that
operate INSIDE the presentation layer:

1. Presentation modules reach application/domain dependencies through a
   structural `_DependencyProvider`-style Protocol, never by importing the
   concrete DI container class directly (Structural Presentation Boundary,
   Hard Rule 6/18).
2. Route handlers consume a named `Annotated` dependency alias, never an
   inline `Depends(...)` call in the function signature.

Read-only: parses source with `ast`, never imports or executes target files.

Usage:
    uv run python check_backend_wiring.py src/<pkg>/presentation \
        --container-name Container

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

_DEFAULT_CONTAINER_NAME = "Container"


@dataclass(frozen=True, kw_only=True, slots=True)
class Finding:
    """One presentation-boundary observation."""

    path: Path
    line: int
    message: str

    def __str__(self) -> str:
        """Render as a `path:line: message` grep-friendly line."""
        return f"{self.path}:{self.line}: {self.message}"


def _iter_python_files(root: Path) -> Iterator[Path]:
    """Yield every `.py` file under `root`, skipping caches."""
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" not in path.parts:
            yield path


def _check_container_import(
    tree: ast.Module, *, path: Path, container_name: str
) -> Iterator[Finding]:
    """Flag any import of the concrete container class by name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == container_name:
                    yield Finding(
                        path=path,
                        line=node.lineno,
                        message=(
                            f"imports concrete '{container_name}' directly — "
                            "reach it through a structural _DependencyProvider "
                            "Protocol instead (Structural Presentation Boundary)"
                        ),
                    )


def _check_inline_depends(tree: ast.Module, *, path: Path) -> Iterator[Finding]:
    """Flag a route handler parameter with an inline `Depends(...)` default."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if (
                isinstance(default, ast.Call)
                and isinstance(default.func, ast.Name)
                and default.func.id == "Depends"
            ):
                yield Finding(
                    path=path,
                    line=default.lineno,
                    message=(
                        f"'{node.name}' uses an inline Depends(...) default — "
                        "extract a named Annotated dependency alias instead"
                    ),
                )


def check_file(path: Path, *, container_name: str) -> list[Finding]:
    """Run both checks against one presentation-layer source file.

    Args:
        path (Path): Source file to inspect.
        container_name (str): Concrete container class name to flag.

    Returns:
        list[Finding]: Findings for this file, in source order.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [
            Finding(path=path, line=exc.lineno or 0, message=f"unparsable: {exc.msg}")
        ]
    return [
        *_check_container_import(tree, path=path, container_name=container_name),
        *_check_inline_depends(tree, path=path),
    ]


def main(argv: list[str] | None = None) -> int:
    """Scan a presentation directory and report findings.

    Args:
        argv (list[str] | None): Command-line arguments, or None for `sys.argv`.

    Returns:
        int: Exit code — 0 clean, 1 findings, 2 usage error.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("presentation_dir", type=Path)
    parser.add_argument("--container-name", default=_DEFAULT_CONTAINER_NAME)
    args = parser.parse_args(argv)

    if not args.presentation_dir.is_dir():
        sys.stderr.write(f"error: not a directory: {args.presentation_dir}\n")
        return 2

    findings = [
        finding
        for path in _iter_python_files(args.presentation_dir)
        for finding in check_file(path, container_name=args.container_name)
    ]
    for finding in findings:
        sys.stdout.write(f"{finding}\n")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
