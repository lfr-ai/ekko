"""Flag a redundant `response_model=` kwarg on a FastAPI route decorator: one
that repeats the handler's own return-type annotation verbatim.

Per FastAPI's documented `response_model` priority rule, declaring both makes
`response_model` silently override the return-type annotation for validation
purposes — so a `response_model=X` next to `-> X` is not "belt and suspenders",
it is two declarations of the same shape that can drift out of sync with each
other (see the `api-contracts` skill's "FastAPI and Swagger" section). A
`response_model` that legitimately differs from the return type (narrowing a
broader internal type to a public schema, or a deliberate response-validation
test fixture) is unaffected — this check only flags an *identical* pair.

Run standalone::

    uv run python .agents/skills/api-contracts/scripts/check_response_model_redundancy.py \\
        [path ...]

Defaults to `src` when no paths are given. Exit status is non-zero when any
violation is found.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, TypeGuard

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

_DEFAULT_PATHS = (Path("src"),)
_ROUTE_DECORATOR_METHODS = frozenset({"get", "post", "put", "patch", "delete"})


@dataclass(frozen=True, kw_only=True, slots=True)
class RedundancyViolation:
    """One route decorator whose `response_model=` repeats the return type."""

    file: Path
    line: int
    shape: str


def _iter_python_files(paths: Sequence[Path]) -> Iterator[Path]:
    """Expand a mix of files and directories into concrete `.py` files."""
    for path in paths:
        if path.is_dir():
            yield from path.rglob("*.py")
        elif path.suffix == ".py":
            yield path


def _is_route_decorator_call(node: ast.expr) -> TypeGuard[ast.Call]:
    """Check whether a decorator expression is `<router>.<http-verb>(...)`."""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in _ROUTE_DECORATOR_METHODS
    )


def _response_model_keyword(call: ast.Call) -> ast.expr | None:
    """Extract a route decorator call's `response_model=` value, if present."""
    for keyword in call.keywords:
        if keyword.arg == "response_model":
            return keyword.value
    return None


def _redundant_decorator_violations(
    node: ast.FunctionDef | ast.AsyncFunctionDef, *, file: Path
) -> Iterator[RedundancyViolation]:
    """Flag a route decorator whose `response_model=` repeats the return type."""
    if node.returns is None:
        return
    return_shape = ast.unparse(node.returns)
    for decorator in node.decorator_list:
        if not _is_route_decorator_call(decorator):
            continue
        response_model = _response_model_keyword(decorator)
        if response_model is not None and ast.unparse(response_model) == return_shape:
            yield RedundancyViolation(
                file=file, line=decorator.lineno, shape=return_shape
            )


def check_file(file: Path) -> list[RedundancyViolation]:
    """Run the check against a single file.

    Args:
        file (Path): Python file to inspect.

    Returns:
        list[RedundancyViolation]: Violations found, if any.
    """
    tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
    return [
        violation
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        for violation in _redundant_decorator_violations(node, file=file)
    ]


def check_response_model_redundancy(paths: Sequence[Path]) -> list[RedundancyViolation]:
    """Run the check against a set of files or directories.

    Args:
        paths (Sequence[Path]): Files or directories to scan.

    Returns:
        list[RedundancyViolation]: All violations found, unsorted.
    """
    violations: list[RedundancyViolation] = []
    for file in _iter_python_files(paths):
        violations.extend(check_file(file))
    return violations


def _report(violations: list[RedundancyViolation]) -> int:
    """Write a human-readable report and compute the process exit code."""
    if not violations:
        sys.stdout.write("response-model-redundancy: no violations found.\n")
        return 0
    sys.stderr.write("response-model-redundancy: violations found:\n")
    for violation in sorted(violations, key=lambda v: (str(v.file), v.line)):
        sys.stderr.write(
            f"  - {violation.file}:{violation.line} response_model={violation.shape} "
            f"duplicates the return-type annotation; drop the kwarg\n"
        )
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the check and return a process exit code.

    Args:
        argv (Sequence[str] | None): Optional CLI arguments naming files or
            directories to scan; defaults to `src`.

    Returns:
        int: `0` on success, `1` when violations are found.
    """
    args = list(argv if argv is not None else sys.argv[1:])
    paths = [Path(arg) for arg in args] if args else list(_DEFAULT_PATHS)
    return _report(check_response_model_redundancy(paths))


if __name__ == "__main__":
    raise SystemExit(main())
