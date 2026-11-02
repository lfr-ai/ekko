"""Static check for the `from_config` structural-Protocol convention.

Hard Rule 20 / the `configuration` skill require that a component built from
application configuration exposes `from_config(cls, config: _XConfig)`, where
`_XConfig` is a PRIVATE structural `typing.Protocol` declared in the same
module — never the concrete aggregate config type. This keeps the component
decoupled from the config layer (PEP 544 structural typing) instead of
importing `AppConfig`/`BaseAppConfig` directly.

Neither ruff nor ty know about this project-specific convention; both accept
a `from_config(cls, config: AppConfig)` signature as perfectly valid typing.

Read-only: parses source with `ast`, never imports or executes target files.

Usage:
    uv run python check_from_config_pattern.py src/<pkg>

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


@dataclass(frozen=True, kw_only=True, slots=True)
class Finding:
    """One `from_config` convention observation."""

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


def _is_classmethod(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a function is decorated with `@classmethod`."""
    return any(
        isinstance(deco, ast.Name) and deco.id == "classmethod"
        for deco in node.decorator_list
    )


def _is_abstractmethod(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a function is decorated with `@abstractmethod`."""
    return any(
        isinstance(deco, ast.Name) and deco.id == "abstractmethod"
        for deco in node.decorator_list
    )


def _annotation_name(annotation: ast.expr | None) -> str | None:
    """Extract a simple name from a type annotation, when possible."""
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        return annotation.value
    return None


def _config_param(node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.arg | None:
    """Return the config parameter of a `from_config` classmethod, if any."""
    params = [*node.args.posonlyargs, *node.args.args]
    return params[1] if len(params) > 1 else None


def _local_protocol_names(tree: ast.Module) -> set[str]:
    """Collect names of module-level classes that inherit from `Protocol`."""
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
        and any(
            isinstance(base, ast.Name) and base.id == "Protocol" for base in node.bases
        )
    }


def _check_config_parameter(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    path: Path,
    protocol_names: set[str],
) -> Finding | None:
    """Validate one `from_config` method's config-parameter annotation."""
    param = _config_param(node)
    if param is None or param.annotation is None:
        return Finding(
            path=path,
            line=node.lineno,
            message=(
                "'from_config' has no typed config parameter — annotate "
                "it with a private structural _XConfig Protocol"
            ),
        )

    name = _annotation_name(param.annotation)
    if name is None:
        return None

    if not name.startswith("_"):
        return Finding(
            path=path,
            line=param.lineno,
            message=(
                f"'from_config' parameter typed as public '{name}' — use "
                "a private structural _XConfig Protocol instead of the "
                "concrete aggregate config (Hard Rule 20)"
            ),
        )
    if name not in protocol_names:
        return Finding(
            path=path,
            line=param.lineno,
            message=(
                f"'from_config' parameter type '{name}' is not a "
                "Protocol defined in this module — keep the structural "
                "view local"
            ),
        )
    return None


def _check_from_config_methods(tree: ast.Module, *, path: Path) -> Iterator[Finding]:
    """Flag `from_config` classmethods whose config parameter is not a
    private, locally-defined structural Protocol.
    """
    protocol_names = _local_protocol_names(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if node.name != "from_config" or not _is_classmethod(node):
            continue
        if _is_abstractmethod(node):
            # An abstract stub (e.g. FromConfigMixin.from_config) declares the
            # contract generically - it has no config type to validate here;
            # the check applies to each concrete override instead.
            continue
        finding = _check_config_parameter(
            node, path=path, protocol_names=protocol_names
        )
        if finding is not None:
            yield finding


def check_file(path: Path) -> list[Finding]:
    """Run the from_config check against one source file.

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
    return list(_check_from_config_methods(tree, path=path))


def main(argv: list[str] | None = None) -> int:
    """Scan a source directory and report `from_config` convention findings.

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
