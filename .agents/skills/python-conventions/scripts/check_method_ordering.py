"""Flag single-use private helpers placed away from their caller.

Neither PEP 8 nor the Google Python Style Guide prescribes member order, but
this project's convention (`python-conventions.instructions.md` "Method
Ordering", `references/method-ordering.md`'s "Module layout") is the stepdown
rule from *Clean Code*: a private helper used by exactly one caller must sit
immediately after that caller, never banished to a separate "private members"
block at the bottom (the class/module's own chronological-addition order).
A helper called by more than one caller is a shared helper and is exempt (it
anchors near `__init__`/its first caller instead, which this script does not
attempt to verify mechanically).

The same rule applies at two scopes, checked independently:

- **Class scope**: a private method used by exactly one sibling method.
- **Module scope**: a private (`_`-prefixed) top-level function used by
  exactly one sibling top-level function — the module-level equivalent for
  function-only modules and files that mix top-level functions with a class
  (e.g. a small supporting dataclass plus the functions that build it).

Run standalone::

    uv run python .agents/skills/python-conventions/scripts/check_method_ordering.py <path> [<path> ...]

Exit status is non-zero when any violation is found.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence

_EXEMPT_DECORATORS = frozenset({"property", "staticmethod", "classmethod", "override"})
_MODULE_EXEMPT_DECORATORS = _EXEMPT_DECORATORS | frozenset({"fixture", "overload"})
_SELF_LIKE_NAMES = frozenset({"self", "cls"})
_MIN_ITEMS_TO_CHECK = 3
_MAX_DIRECT_HELPERS_BEFORE_DISPATCH = 3


@dataclass(frozen=True, kw_only=True, slots=True)
class OrderingViolation:
    """One misplaced single-caller private helper found in a class."""

    file: Path
    line: int
    rule: str
    message: str


def _iter_python_files(paths: Sequence[Path]) -> Iterator[Path]:
    """Expand a mix of files and directories into concrete `.py` files.

    Args:
        paths (Sequence[Path]): Files or directories to scan.

    Yields:
        Path: Each `.py` file found.
    """
    for path in paths:
        if path.is_dir():
            yield from path.rglob("*.py")
        elif path.suffix == ".py":
            yield path


def _class_methods(
    node: ast.ClassDef,
) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Direct method defs of a class, in source order."""
    return [
        stmt
        for stmt in node.body
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef)
    ]


def _is_dunder(name: str) -> bool:
    """Whether a name is a `__dunder__` method name."""
    return name.startswith("__") and name.endswith("__")


def _decorator_names(method: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Simple names of a method's decorators (ignoring call arguments)."""
    names: set[str] = set()
    for decorator in method.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, ast.Attribute):
            names.add(target.attr)
    return names


def _self_attr_references(method: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Names referenced as `self.<name>`/`cls.<name>` anywhere in a method body.

    Deliberately broader than "directly called" — a helper passed as a bare
    callback (for example `asyncio.to_thread(self._helper, ...)`) is still a
    real usage and must count as a caller, not be missed as dead code.
    """
    referenced: set[str] = set()
    for node in ast.walk(method):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in _SELF_LIKE_NAMES
        ):
            referenced.add(node.attr)
    return referenced


def _callers_by_method_name(
    methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
) -> dict[str, set[str]]:
    """Map each method name to the set of sibling methods that reference it."""
    callers: dict[str, set[str]] = {method.name: set() for method in methods}
    for caller in methods:
        for referenced_name in _self_attr_references(caller):
            if referenced_name in callers and referenced_name != caller.name:
                callers[referenced_name].add(caller.name)
    return callers


def _is_single_caller_helper_candidate(
    method: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    """Whether a method is eligible to be checked as a private helper."""
    if not method.name.startswith("_") or _is_dunder(method.name):
        return False
    return not (_decorator_names(method) & _EXEMPT_DECORATORS)


def _immediate_caller_by_name(
    callers_by_name: dict[str, set[str]],
) -> dict[str, str | None]:
    """Map each method name to its sole caller, or `None` if not single-caller."""
    return {
        name: next(iter(callers)) if len(callers) == 1 else None
        for name, callers in callers_by_name.items()
    }


def _cluster_root(
    name: str,
    *,
    immediate_caller: dict[str, str | None],
    cache: dict[str, str],
) -> str:
    """Walk a single-caller chain up to its owning public method/shared helper.

    A method with zero or multiple callers is its own cluster root (a public
    entry point, or a shared helper deliberately exempt from adjacency).
    """
    if name in cache:
        return cache[name]
    caller = immediate_caller.get(name)
    root = (
        name
        if caller is None or caller == name
        else _cluster_root(caller, immediate_caller=immediate_caller, cache=cache)
    )
    cache[name] = root
    return root


def _is_misplaced(
    *,
    helper_index: int,
    root_index: int,
    root_name: str,
    context: _ClusterContext,
) -> bool:
    """Whether a helper sits outside its cluster's contiguous span.

    The cluster root (the public method/top-level function that ultimately
    owns this single-caller chain) must be on the expected side of the whole
    chain (before it for class-method stepdown, after it for module-level
    definition-before-use), and every item sandwiched between the root and
    the helper must itself belong to the same cluster (nested helper-of-a-
    helper chains are valid; an unrelated item sitting in between is not).
    """
    near_index, far_index = (
        (root_index, helper_index)
        if context.root_before_helper
        else (helper_index, root_index)
    )
    if far_index <= near_index:
        return True
    return any(
        context.cluster_root_by_name[context.items[between].name] != root_name
        for between in range(near_index + 1, far_index)
    )


def _direct_helper_counts(immediate_caller: dict[str, str | None]) -> dict[str, int]:
    """Count each name's directly-attributed single-caller helpers."""
    counts: dict[str, int] = {}
    for caller in immediate_caller.values():
        if caller is not None:
            counts[caller] = counts.get(caller, 0) + 1
    return counts


@dataclass(frozen=True, kw_only=True, slots=True)
class _ScopeConfig:
    """Static configuration for one ordering scope (class body or module body)."""

    label: str
    rule: str
    root_before_helper: bool
    is_candidate: Callable[[ast.FunctionDef | ast.AsyncFunctionDef], bool]


@dataclass(frozen=True, kw_only=True, slots=True)
class _ClusterContext:
    """Resolved single-caller cluster data for one scope's items."""

    items: list[ast.FunctionDef | ast.AsyncFunctionDef]
    cluster_root_by_name: dict[str, str]
    root_before_helper: bool


def _ordering_violations(
    items: list[ast.FunctionDef | ast.AsyncFunctionDef],
    *,
    callers_by_name: dict[str, set[str]],
    scope: _ScopeConfig,
    file: Path,
) -> Iterator[OrderingViolation]:
    """Flag single-caller items in one scope that sit away from their caller.

    Shared by the class-method and module-function checks; "scope" is either
    a class body or a module body.

    Args:
        items (list[ast.FunctionDef | ast.AsyncFunctionDef]): Methods or
            top-level functions, in source order.
        callers_by_name (dict[str, set[str]]): Sibling callers per item name.
        scope (_ScopeConfig): Scope-specific labeling, direction, and candidacy rule.
        file (Path): File the items were parsed from, for reporting.

    Yields:
        OrderingViolation: One per misplaced single-caller helper.
    """
    if len(items) < _MIN_ITEMS_TO_CHECK:
        return
    index_by_name = {item.name: i for i, item in enumerate(items)}
    immediate_caller = _immediate_caller_by_name(callers_by_name)
    direct_helper_counts = _direct_helper_counts(immediate_caller)
    root_cache: dict[str, str] = {}
    cluster_root_by_name = {
        item.name: _cluster_root(
            item.name, immediate_caller=immediate_caller, cache=root_cache
        )
        for item in items
    }
    context = _ClusterContext(
        items=items,
        cluster_root_by_name=cluster_root_by_name,
        root_before_helper=scope.root_before_helper,
    )
    for i, helper in enumerate(items):
        if not scope.is_candidate(helper):
            continue
        caller_name = immediate_caller[helper.name]
        if caller_name is None:
            continue
        root_name = cluster_root_by_name[helper.name]
        # A caller with many independent single-caller helpers is a dispatch
        # table/registry (e.g. `main()` fanning out to a dozen `_check_*`
        # handlers), not a 1:1 stepdown extraction — exempt from adjacency.
        if direct_helper_counts.get(root_name, 0) > _MAX_DIRECT_HELPERS_BEFORE_DISPATCH:
            continue
        root_index = index_by_name[root_name]
        if not _is_misplaced(
            helper_index=i,
            root_index=root_index,
            root_name=root_name,
            context=context,
        ):
            continue
        yield OrderingViolation(
            file=file,
            line=helper.lineno,
            rule=scope.rule,
            message=(
                f"{scope.label}: '{helper.name}' is used only by "
                f"'{caller_name}' but sits outside its call chain's "
                f"contiguous block (owned by '{root_name}'); see "
                "python-conventions.instructions.md's Method Ordering section"
            ),
        )


def _class_ordering_violations(
    node: ast.ClassDef, *, file: Path
) -> Iterator[OrderingViolation]:
    """Flag single-caller helpers in one class that sit away from their caller.

    Args:
        node (ast.ClassDef): Class to inspect.
        file (Path): File the class was parsed from, for reporting.

    Yields:
        OrderingViolation: One per misplaced single-caller helper.
    """
    methods = _class_methods(node)
    yield from _ordering_violations(
        methods,
        callers_by_name=_callers_by_method_name(methods),
        scope=_ScopeConfig(
            label=f"class '{node.name}'",
            rule="method-ordering-stepdown",
            root_before_helper=True,
            is_candidate=_is_single_caller_helper_candidate,
        ),
        file=file,
    )


def _module_level_functions(
    tree: ast.Module,
) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Top-level function defs of a module, in source order."""
    return [
        stmt
        for stmt in tree.body
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef)
    ]


def _name_references(func: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Bare names referenced (loaded) anywhere in a function body.

    Deliberately broader than "directly called" — a helper passed as a bare
    callback (for example `asyncio.to_thread(_helper, ...)`) is still a real
    usage and must count as a caller, not be missed as dead code.
    """
    return {
        node.id
        for node in ast.walk(func)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }


def _callers_by_function_name(
    functions: list[ast.FunctionDef | ast.AsyncFunctionDef],
) -> dict[str, set[str]]:
    """Map each top-level function name to sibling functions that reference it."""
    callers: dict[str, set[str]] = {function.name: set() for function in functions}
    for caller in functions:
        for referenced_name in _name_references(caller):
            if referenced_name in callers and referenced_name != caller.name:
                callers[referenced_name].add(caller.name)
    return callers


def _is_single_caller_function_candidate(
    func: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    """Whether a top-level function is eligible to be checked as a private helper."""
    if not func.name.startswith("_") or _is_dunder(func.name):
        return False
    return not (_decorator_names(func) & _MODULE_EXEMPT_DECORATORS)


def _module_ordering_violations(
    tree: ast.Module, *, file: Path
) -> Iterator[OrderingViolation]:
    """Flag single-caller top-level functions that sit away from their caller.

    Args:
        tree (ast.Module): Parsed module to inspect.
        file (Path): File the module was parsed from, for reporting.

    Yields:
        OrderingViolation: One per misplaced single-caller top-level function.
    """
    functions = _module_level_functions(tree)
    yield from _ordering_violations(
        functions,
        callers_by_name=_callers_by_function_name(functions),
        scope=_ScopeConfig(
            label="module-level function",
            rule="module-ordering-definition-before-use",
            root_before_helper=False,
            is_candidate=_is_single_caller_function_candidate,
        ),
        file=file,
    )


def _is_test_module(file: Path) -> bool:
    """Whether a file is a pytest test module exempt from the module-level check.

    Test suites conventionally group shared builder/stub helpers in a
    top-of-file utilities section regardless of how many `test_*` functions
    currently use them (see the `testing` skill) — a distinct, equally valid
    layout from a production module's single-orchestrator convention that
    this check would otherwise misflag as misplaced.
    """
    return file.name == "conftest.py" or file.name.startswith("test_")


def check_file(file: Path) -> list[OrderingViolation]:
    """Run the method-ordering check against every class in one file.

    Args:
        file (Path): Python file to inspect.

    Returns:
        list[OrderingViolation]: Violations found, if any.
    """
    tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
    violations: list[OrderingViolation] = (
        []
        if _is_test_module(file)
        else list(_module_ordering_violations(tree, file=file))
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            violations.extend(_class_ordering_violations(node, file=file))
    return violations


def check_method_ordering(paths: Sequence[Path]) -> list[OrderingViolation]:
    """Run the method-ordering check against a set of files or directories.

    Args:
        paths (Sequence[Path]): Files or directories to scan.

    Returns:
        list[OrderingViolation]: All violations found, unsorted.
    """
    violations: list[OrderingViolation] = []
    for file in _iter_python_files(paths):
        violations.extend(check_file(file))
    return violations


def _report(violations: list[OrderingViolation]) -> int:
    """Write a human-readable report and compute the process exit code.

    Args:
        violations (list[OrderingViolation]): Violations to report.

    Returns:
        int: ``0`` when there are no violations, otherwise ``1``.
    """
    if not violations:
        sys.stdout.write("method-ordering: no violations found.\n")
        return 0
    sys.stderr.write("method-ordering: violations found:\n")
    for violation in sorted(violations, key=lambda v: (str(v.file), v.line)):
        sys.stderr.write(
            f"  - {violation.file}:{violation.line} [{violation.rule}] "
            f"{violation.message}\n"
        )
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the method-ordering check and return a process exit code.

    Args:
        argv (Sequence[str] | None): Optional CLI arguments naming files or
            directories to scan; defaults to ``src``.

    Returns:
        int: ``0`` on success, ``1`` when violations are found.
    """
    args = list(argv if argv is not None else sys.argv[1:])
    paths = [Path(arg) for arg in args] if args else [Path("src")]
    return _report(check_method_ordering(paths))


if __name__ == "__main__":
    raise SystemExit(main())
