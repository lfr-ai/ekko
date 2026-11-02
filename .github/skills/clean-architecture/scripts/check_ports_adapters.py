"""Verify a Core port's Protocol methods stay aligned with every Infrastructure
adapter that nominally implements it (`class XRepository(Base, XPort): ...`,
the pattern the `clean-architecture` skill's `repository_adapter.py.template`
establishes).

For each adapter method that overrides a port method of the same name, checks:

- **Signature**: parameter names, order, kind (positional-only/positional-or-
  keyword/var-positional/keyword-only/var-keyword), annotations, and the
  return annotation must match exactly (`self`/`cls` excluded). Async-ness
  (`def` vs `async def`) must also match.
- **Docstring summary**: the first line of the port's and the adapter's
  docstring must match verbatim. The rest of the docstring (`Args:`,
  `Returns:`, and especially `Raises:` — an adapter legitimately raises
  infrastructure-specific exceptions its port never declares) is intentionally
  out of scope.

A port method the adapter never overrides (inherited from an unrelated mixin,
or satisfied structurally without nominal inheritance) is out of scope — this
check only follows explicit `class Adapter(..., SomePort)` inheritance, never
structural (duck-typed) Protocol conformance.

Run standalone::

    uv run python .agents/skills/clean-architecture/scripts/check_ports_adapters.py \\
        [--src-root src] [--ports-glob "**/core/ports/**/*.py"] \\
        [--adapters-glob "**/infrastructure/**/*.py"]

Exit status is non-zero when any violation is found.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Sequence

_DEFAULT_SRC_ROOT = Path("src")
_DEFAULT_PORTS_GLOB = "**/core/ports/**/*.py"
_DEFAULT_ADAPTERS_GLOB = "**/infrastructure/**/*.py"
_IMPLICIT_PARAM_NAMES = frozenset({"self", "cls"})


@dataclass(frozen=True, kw_only=True, slots=True)
class AlignmentViolation:
    """One drift between a port method and the adapter method overriding it."""

    file: Path
    line: int
    rule: str
    message: str


@dataclass(frozen=True, kw_only=True, slots=True)
class _Param:
    """One method parameter, position/kind-aware (`self`/`cls` excluded)."""

    name: str
    kind: str
    annotation: str | None
    has_default: bool


@dataclass(frozen=True, kw_only=True, slots=True)
class _MethodShape:
    """A method's comparable shape: signature plus docstring summary."""

    name: str
    is_async: bool
    params: tuple[_Param, ...]
    returns: str | None
    summary: str | None
    lineno: int


@dataclass(frozen=True, kw_only=True, slots=True)
class _Port:
    """One discovered Core port (a `Protocol` class) and its method shapes."""

    qualified_name: str
    file: Path
    methods: dict[str, _MethodShape] = field(default_factory=dict)


def _unparse(node: ast.expr | None) -> str | None:
    """Render an annotation expression back to normalized source text.

    Args:
        node (ast.expr | None): Annotation node, or None when absent.

    Returns:
        str | None: Unparsed annotation text, or None when there was none.
    """
    return ast.unparse(node) if node is not None else None


def _params(args: ast.arguments) -> tuple[_Param, ...]:
    """Flatten an `arguments` node into ordered, kind-aware parameters.

    Args:
        args (ast.arguments): Function signature to flatten.

    Returns:
        tuple[_Param, ...]: Parameters excluding an implicit `self`/`cls`.
    """
    params: list[_Param] = []

    positional = [*args.posonlyargs, *args.args]
    defaults_by_index = {
        len(positional) - len(args.defaults) + i: True
        for i in range(len(args.defaults))
    }
    posonly_count = len(args.posonlyargs)
    for index, arg in enumerate(positional):
        if index == 0 and arg.arg in _IMPLICIT_PARAM_NAMES:
            continue
        kind = "POSONLY" if index < posonly_count else "POS_OR_KW"
        params.append(
            _Param(
                name=arg.arg,
                kind=kind,
                annotation=_unparse(arg.annotation),
                has_default=index in defaults_by_index,
            )
        )

    if args.vararg is not None:
        params.append(
            _Param(
                name=args.vararg.arg,
                kind="VAR_POS",
                annotation=_unparse(args.vararg.annotation),
                has_default=False,
            )
        )

    for arg, kw_default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        params.append(
            _Param(
                name=arg.arg,
                kind="KWONLY",
                annotation=_unparse(arg.annotation),
                has_default=kw_default is not None,
            )
        )

    if args.kwarg is not None:
        params.append(
            _Param(
                name=args.kwarg.arg,
                kind="VAR_KW",
                annotation=_unparse(args.kwarg.annotation),
                has_default=False,
            )
        )

    return tuple(params)


def _summary(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """Extract a docstring's first line (the part `Raises:` never reaches).

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): Method to inspect.

    Returns:
        str | None: The stripped summary line, or None without a docstring.
    """
    docstring = ast.get_docstring(node, clean=True)
    if not docstring:
        return None
    first_paragraph = docstring.split("\n\n", 1)[0]
    return " ".join(first_paragraph.split())


def _method_shape(node: ast.FunctionDef | ast.AsyncFunctionDef) -> _MethodShape:
    """Build one method's comparable shape.

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): Method to inspect.

    Returns:
        _MethodShape: Signature and docstring-summary shape for comparison.
    """
    return _MethodShape(
        name=node.name,
        is_async=isinstance(node, ast.AsyncFunctionDef),
        params=_params(node.args),
        returns=_unparse(node.returns),
        summary=_summary(node),
        lineno=node.lineno,
    )


def _is_protocol_base(base: ast.expr) -> bool:
    """Check whether a class base expression is `Protocol` (bare or aliased)."""
    if isinstance(base, ast.Name):
        return base.id == "Protocol"
    return isinstance(base, ast.Attribute) and base.attr == "Protocol"


def _module_name(file: Path, *, src_root: Path) -> str | None:
    """Derive a file's dotted module name relative to the source root.

    Args:
        file (Path): Python source file.
        src_root (Path): Import root the project's packages resolve against.

    Returns:
        str | None: Dotted module name, or None when `file` is outside
            `src_root`.
    """
    try:
        relative = file.relative_to(src_root)
    except ValueError:
        return None
    return ".".join(relative.with_suffix("").parts)


def _iter_public_methods(
    class_node: ast.ClassDef,
) -> Iterator[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Yield a class's directly-defined public method/property definitions."""
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and (
            not node.name.startswith("_") or node.name == "__init__"
        ):
            yield node


def _find_ports(files: Iterable[Path], *, src_root: Path) -> dict[str, _Port]:
    """Discover every `Protocol` class under the ports root.

    Args:
        files (Iterable[Path]): Candidate port module files.
        src_root (Path): Import root used to compute qualified names.

    Returns:
        dict[str, _Port]: Ports keyed by qualified name (`module.ClassName`).
    """
    ports: dict[str, _Port] = {}
    for file in files:
        module = _module_name(file, src_root=src_root)
        if module is None:
            continue
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if not any(_is_protocol_base(base) for base in node.bases):
                continue
            qualified_name = f"{module}.{node.name}"
            ports[qualified_name] = _Port(
                qualified_name=qualified_name,
                file=file,
                methods={m.name: _method_shape(m) for m in _iter_public_methods(node)},
            )
    return ports


def _import_map(tree: ast.Module) -> dict[str, str]:
    """Map a module's locally-bound names to their `module.Name` origin.

    Only plain `from module import Name [as alias]` imports are resolved
    (matching this project's port-import convention); star imports and
    aliased submodule imports are out of scope.

    Args:
        tree (ast.Module): Parsed adapter module AST.

    Returns:
        dict[str, str]: Local name -> `"module.Name"` it was imported from.
    """
    imports: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module is None or node.level:
            continue
        for alias in node.names:
            local_name = alias.asname or alias.name
            imports[local_name] = f"{node.module}.{alias.name}"
    return imports


def _implemented_ports(
    class_node: ast.ClassDef, *, imports: dict[str, str], ports: dict[str, _Port]
) -> list[_Port]:
    """Resolve which discovered ports a class nominally inherits from."""
    implemented: list[_Port] = []
    for base in class_node.bases:
        if not isinstance(base, ast.Name):
            continue
        qualified_name = imports.get(base.id)
        if qualified_name is not None and (port := ports.get(qualified_name)):
            implemented.append(port)
    return implemented


def _signature_violations(
    *, file: Path, port_method: _MethodShape, adapter_method: _MethodShape
) -> Iterator[AlignmentViolation]:
    """Compare one adapter method's signature against its port method."""
    label = f"{adapter_method.name}()"
    if port_method.is_async != adapter_method.is_async:
        yield AlignmentViolation(
            file=file,
            line=adapter_method.lineno,
            rule="port-adapter-async-mismatch",
            message=(
                f"{label}: async-ness differs from port "
                f"(port async={port_method.is_async}, "
                f"adapter async={adapter_method.is_async})"
            ),
        )
    if port_method.params != adapter_method.params:
        yield AlignmentViolation(
            file=file,
            line=adapter_method.lineno,
            rule="port-adapter-signature-drift",
            message=(
                f"{label}: parameters drift from port "
                f"(port={port_method.params}, adapter={adapter_method.params})"
            ),
        )
    if port_method.returns != adapter_method.returns:
        yield AlignmentViolation(
            file=file,
            line=adapter_method.lineno,
            rule="port-adapter-return-type-drift",
            message=(
                f"{label}: return type drifts from port "
                f"(port={port_method.returns!r}, adapter={adapter_method.returns!r})"
            ),
        )


def _docstring_violations(
    *, file: Path, port_method: _MethodShape, adapter_method: _MethodShape
) -> Iterator[AlignmentViolation]:
    """Compare one adapter method's docstring summary against its port method."""
    if (
        port_method.summary is not None
        and adapter_method.summary is not None
        and port_method.summary != adapter_method.summary
    ):
        yield AlignmentViolation(
            file=file,
            line=adapter_method.lineno,
            rule="port-adapter-docstring-drift",
            message=(
                f"{adapter_method.name}(): docstring summary drifts from port "
                f"(port={port_method.summary!r}, adapter={adapter_method.summary!r})"
            ),
        )


def _adapter_violations(
    class_node: ast.ClassDef,
    *,
    file: Path,
    imports: dict[str, str],
    ports: dict[str, _Port],
) -> Iterator[AlignmentViolation]:
    """Check every port method an adapter class overrides."""
    for port in _implemented_ports(class_node, imports=imports, ports=ports):
        adapter_methods = {
            m.name: _method_shape(m) for m in _iter_public_methods(class_node)
        }
        for name, port_method in port.methods.items():
            adapter_method = adapter_methods.get(name)
            if adapter_method is None:
                continue
            yield from _signature_violations(
                file=file, port_method=port_method, adapter_method=adapter_method
            )
            yield from _docstring_violations(
                file=file, port_method=port_method, adapter_method=adapter_method
            )


def _check_adapters(
    files: Iterable[Path], *, ports: dict[str, _Port]
) -> list[AlignmentViolation]:
    """Check every adapter file against the discovered ports.

    Args:
        files (Iterable[Path]): Candidate adapter module files.
        ports (dict[str, _Port]): Ports keyed by qualified name.

    Returns:
        list[AlignmentViolation]: Violations found, if any.
    """
    violations: list[AlignmentViolation] = []
    for file in files:
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        imports = _import_map(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                violations.extend(
                    _adapter_violations(node, file=file, imports=imports, ports=ports)
                )
    return violations


def check_ports_adapters(
    *, src_root: Path, ports_glob: str, adapters_glob: str
) -> list[AlignmentViolation]:
    """Run the full ports/adapters alignment check.

    Args:
        src_root (Path): Import root the project's packages resolve against.
        ports_glob (str): Glob (relative to `src_root`) selecting port modules.
        adapters_glob (str): Glob (relative to `src_root`) selecting adapter
            modules.

    Returns:
        list[AlignmentViolation]: Violations found, if any.
    """
    ports = _find_ports(src_root.glob(ports_glob), src_root=src_root)
    return _check_adapters(src_root.glob(adapters_glob), ports=ports)


def _report(violations: list[AlignmentViolation]) -> int:
    """Write a human-readable report and compute the process exit code.

    Args:
        violations (list[AlignmentViolation]): Violations to report.

    Returns:
        int: `0` when there are no violations, otherwise `1`.
    """
    if not violations:
        sys.stdout.write("ports-adapters: no violations found.\n")
        return 0
    sys.stderr.write("ports-adapters: violations found:\n")
    for violation in sorted(violations, key=lambda v: (str(v.file), v.line)):
        sys.stderr.write(
            f"  - {violation.file}:{violation.line} [{violation.rule}] "
            f"{violation.message}\n"
        )
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ports/adapters alignment check and return a process exit code.

    Args:
        argv (Sequence[str] | None): Optional CLI arguments; defaults to
            `sys.argv[1:]`.

    Returns:
        int: `0` on success, `1` when violations are found.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src-root", type=Path, default=_DEFAULT_SRC_ROOT)
    parser.add_argument("--ports-glob", default=_DEFAULT_PORTS_GLOB)
    parser.add_argument("--adapters-glob", default=_DEFAULT_ADAPTERS_GLOB)
    args = parser.parse_args(argv)
    violations = check_ports_adapters(
        src_root=args.src_root,
        ports_glob=args.ports_glob,
        adapters_glob=args.adapters_glob,
    )
    return _report(violations)


if __name__ == "__main__":
    raise SystemExit(main())
