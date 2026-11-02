"""Catch project Python conventions that ruff cannot detect.

Ruff already enforces most of the `python-conventions` skill (no `Any`
(ANN401), no `cast` (TID251/banned-api), docstring presence and format (D),
import style (ICN)). This script covers the remaining ruff-blind spots that
are project convention rather than a lint rule:

- Quoted forward-reference annotations (project requires
  ``from __future__ import annotations`` instead).
- ``@dataclass`` decorators missing ``kw_only=True``.
- Explicit ``-> None`` return annotation on ``__init__``/``__post_init__``.
- Docstring summaries opening with a banned word (Return, Returns, Response,
  Request, Payload, Raised).
- An ``Args:``/``Returns:``/``Yields:``/``Raises:`` field entry opening with
  the same banned words, or with a leading article (A, An, The).
- ``__init__`` docstrings that break the two-shape rule: zero parameters must
  omit the docstring entirely; one or more parameters must use a full
  ``Args:`` section, never a bare one-line summary.
- Any other docstring that uses a structured section (``Args:``/``Returns:``/
  ``Yields:``/``Raises:``) but omits another section that applies given the
  signature and body (real parameters, a non-``None`` return, a `yield`
  with a value, or an explicit ``raise``) — sections are all-or-nothing.
  A pytest ``test_*`` function is exempt from ``Args:`` (fixtures are
  dependency-injected, not documented per-argument).
- Internal (underscore-prefixed) module-level constants that carry a type
  annotation — project convention leaves these untyped (public constants may
  use ``Final[...]``).
- A Direct-import-bucket stdlib module (``functools``, ``datetime``,
  ``pathlib``, etc.) imported as ``import x`` and used qualified
  (``x.symbol``) instead of ``from x import symbol``. Ruff's ``ICN``
  ``banned-from`` only catches the opposite direction (a Qualified-bucket
  module imported directly), so this direction has no ruff rule.

Run standalone::

    uv run python .agents/skills/python-conventions/scripts/check_conventions.py <path> [<path> ...]

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

_BANNED_DOCSTRING_OPENERS = (
    "Return",
    "Returns",
    "Response",
    "Request",
    "Payload",
    "Raised",
)
_DOCSTRING_SECTION_HEADERS = ("Args:", "Returns:", "Yields:", "Raises:")
_BANNED_LEADING_ARTICLES = ("A", "An", "The")
# Mirrors the python-conventions skill's "Direct — from x import Y" bucket.
_DIRECT_IMPORT_MODULES = frozenset(
    {
        "typing",
        "collections.abc",
        "typing_extensions",
        "dataclasses",
        "enum",
        "pathlib",
        "datetime",
        "uuid",
        "contextlib",
        "functools",
    }
)


@dataclass(frozen=True, kw_only=True, slots=True)
class ConventionViolation:
    """One convention breach found in a source file."""

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


def _quoted_forward_ref_violations(tree: ast.Module, *, file: Path) -> Iterator[ConventionViolation]:
    """Flag string-literal annotations used as forward references.

    Args:
        tree (ast.Module): Parsed module AST.
        file (Path): File the AST was parsed from, for reporting.

    Yields:
        ConventionViolation: One per quoted forward-reference annotation.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign | ast.arg):
            annotation = node.annotation
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            annotation = node.returns
        else:
            continue
        if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            yield ConventionViolation(
                file=file,
                line=node.lineno,
                rule="quoted-forward-ref",
                message=(
                    f"quoted forward-reference annotation {annotation.value!r}; "
                    "use `from __future__ import annotations` instead"
                ),
            )


def _dataclass_kw_only_violations(tree: ast.Module, *, file: Path) -> Iterator[ConventionViolation]:
    """Flag `@dataclass` decorators that omit `kw_only=True`.

    Args:
        tree (ast.Module): Parsed module AST.
        file (Path): File the AST was parsed from, for reporting.

    Yields:
        ConventionViolation: One per non-compliant dataclass decorator.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for decorator in node.decorator_list:
            if not _is_noncompliant_dataclass_decorator(decorator):
                continue
            yield ConventionViolation(
                file=file,
                line=node.lineno,
                rule="dataclass-kw-only",
                message=f"class '{node.name}': @dataclass missing (kw_only=True)",
            )


def _is_noncompliant_dataclass_decorator(decorator: ast.expr) -> bool:
    """Detect a `@dataclass` decorator (bare or called) missing `kw_only=True`.

    Args:
        decorator (ast.expr): One decorator expression from a class definition.

    Returns:
        bool: True when the decorator targets `dataclass` without `kw_only=True`.
    """
    if _targets_dataclass(decorator):
        return True
    if not isinstance(decorator, ast.Call) or not _targets_dataclass(decorator.func):
        return False
    return not any(
        kw.arg == "kw_only" and isinstance(kw.value, ast.Constant) and kw.value.value is True
        for kw in decorator.keywords
    )


def _targets_dataclass(node: ast.expr) -> bool:
    """Detect whether a decorator expression names `dataclass` (bare form).

    Args:
        node (ast.expr): Decorator expression, e.g. a `Name` or `Attribute`.

    Returns:
        bool: True when the expression is `dataclass` or `<module>.dataclass`.
    """
    return (isinstance(node, ast.Name) and node.id == "dataclass") or (
        isinstance(node, ast.Attribute) and node.attr == "dataclass"
    )


def _import_style_violations(tree: ast.Module, *, file: Path) -> Iterator[ConventionViolation]:
    """Flag a Direct-bucket module imported qualified instead of directly.

    An explicit ``as`` alias (e.g. ``import myapp.main as main_module`` for
    monkeypatching) signals a deliberate module-object reference, not the
    qualified-access style this check targets, and is exempt.

    Args:
        tree (ast.Module): Parsed module AST.
        file (Path): File the AST was parsed from, for reporting.

    Yields:
        ConventionViolation: One per qualified import of a Direct-bucket module.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Import):
            continue
        for alias in node.names:
            if alias.asname is not None or alias.name not in _DIRECT_IMPORT_MODULES:
                continue
            yield ConventionViolation(
                file=file,
                line=node.lineno,
                rule="qualified-direct-import-module",
                message=(
                    f"'import {alias.name}' targets a Direct-import-bucket "
                    f"module; use 'from {alias.name} import <name>' instead"
                ),
            )


def _init_return_annotation_violations(tree: ast.Module, *, file: Path) -> Iterator[ConventionViolation]:
    """Flag an explicit `-> None` return annotation on `__init__`/`__post_init__`.

    Args:
        tree (ast.Module): Parsed module AST.
        file (Path): File the AST was parsed from, for reporting.

    Yields:
        ConventionViolation: One per `__init__`/`__post_init__` with a
            redundant annotation.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if node.name not in ("__init__", "__post_init__"):
            continue
        returns = node.returns
        is_none_annotation = isinstance(returns, ast.Constant) and returns.value is None
        if is_none_annotation:
            yield ConventionViolation(
                file=file,
                line=node.lineno,
                rule="init-return-none",
                message=f"`{node.name}` has redundant `-> None` return annotation",
            )


def _docstring_opener_violations(tree: ast.Module, *, file: Path) -> Iterator[ConventionViolation]:
    """Flag docstrings whose summary opens with a banned word.

    Args:
        tree (ast.Module): Parsed module AST.
        file (Path): File the AST was parsed from, for reporting.

    Yields:
        ConventionViolation: One per non-compliant docstring.
    """
    scoped_types = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            docstring, line = ast.get_docstring(node, clean=True), 1
        elif isinstance(node, scoped_types):
            docstring, line = ast.get_docstring(node, clean=True), node.lineno
        else:
            continue
        if not docstring:
            continue
        first_word = docstring.split(maxsplit=1)[0].rstrip(".,:")
        if first_word in _BANNED_DOCSTRING_OPENERS:
            yield ConventionViolation(
                file=file,
                line=line,
                rule="docstring-opener",
                message=(f"docstring summary starts with banned word {first_word!r}"),
            )


def _field_entries(lines: Sequence[str]) -> Iterator[str]:
    """Yield each Args:/Returns:/Yields:/Raises: entry's description text.

    An entry is the first line after a recognized section header at a given
    indentation; a more-indented following line is a wrapped continuation of
    the same entry, not a new one. Only entries shaped like `name: text` or
    `name (Type): text` are recognized (the `text` after the first colon);
    a bare-summary entry with no colon at all is skipped.

    Args:
        lines (Sequence[str]): The docstring's lines (already dedented).

    Yields:
        str: Each recognized entry's description text.
    """
    section_indent: int | None = None
    entry_indent: int | None = None
    for line in lines:
        stripped = line.strip()
        if stripped in _DOCSTRING_SECTION_HEADERS:
            section_indent = len(line) - len(line.lstrip())
            entry_indent = None
            continue
        if section_indent is None:
            continue
        if not stripped:
            section_indent = None
            entry_indent = None
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= section_indent:
            section_indent = None
            entry_indent = None
            continue
        if entry_indent is None:
            entry_indent = indent
        if indent > entry_indent:
            continue  # wrapped continuation line, not a new entry
        _name_and_type, _, description = stripped.partition(":")
        if description:
            yield description.strip()


def _docstring_field_opener_violations(tree: ast.Module, *, file: Path) -> Iterator[ConventionViolation]:
    """Flag a field entry opening with a banned word or a leading article.

    Mirrors `_docstring_opener_violations`, but applies to each individual
    `Args:`/`Returns:`/`Yields:`/`Raises:` entry's description instead of
    just the docstring's overall summary line — an entry can restate
    "Returns ..." or open with a bare "A"/"An"/"The" just as easily as the
    summary can.

    Args:
        tree (ast.Module): Parsed module AST.
        file (Path): File the AST was parsed from, for reporting.

    Yields:
        ConventionViolation: One per non-compliant field entry.
    """
    scoped_types = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            docstring, line = ast.get_docstring(node, clean=True), 1
        elif isinstance(node, scoped_types):
            docstring, line = ast.get_docstring(node, clean=True), node.lineno
        else:
            continue
        if not docstring:
            continue
        for description in _field_entries(docstring.splitlines()):
            first_word = description.split(maxsplit=1)[0].rstrip(".,:")
            if first_word in _BANNED_DOCSTRING_OPENERS:
                yield ConventionViolation(
                    file=file,
                    line=line,
                    rule="docstring-field-opener",
                    message=(f"docstring field entry starts with banned word {first_word!r}"),
                )
            elif first_word in _BANNED_LEADING_ARTICLES:
                yield ConventionViolation(
                    file=file,
                    line=line,
                    rule="docstring-leading-article",
                    message=(
                        f"docstring field entry starts with article {first_word!r}; "
                        "drop it (e.g. 'Order identifier', not 'An order identifier')"
                    ),
                )


def _init_docstring_shape_violations(tree: ast.Module, *, file: Path) -> Iterator[ConventionViolation]:
    """Flag `__init__` docstrings that break the two-shape rule.

    Args:
        tree (ast.Module): Parsed module AST.
        file (Path): File the AST was parsed from, for reporting.

    Yields:
        ConventionViolation: One per non-compliant `__init__` docstring.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if node.name != "__init__":
            continue
        docstring = ast.get_docstring(node, clean=True)
        if docstring is None:
            continue
        real_param_count = (
            len(node.args.posonlyargs)
            + len(node.args.args)
            + len(node.args.kwonlyargs)
            + (1 if node.args.vararg else 0)
            + (1 if node.args.kwarg else 0)
            - 1
        )
        if real_param_count <= 0:
            yield ConventionViolation(
                file=file,
                line=node.lineno,
                rule="init-docstring-shape",
                message=("`__init__` with no parameters should omit its docstring entirely, not carry one"),
            )
        elif "Args:" not in docstring:
            yield ConventionViolation(
                file=file,
                line=node.lineno,
                rule="init-docstring-shape",
                message=("`__init__` with parameters must use a full `Args:` section, not a bare one-line docstring"),
            )


def _real_parameter_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Collect parameter names an `Args:` section is expected to cover.

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): Function to inspect.

    Returns:
        list[str]: Parameter names, excluding a leading `self`/`cls`.
    """
    names = [arg.arg for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)]
    if names and names[0] in ("self", "cls"):
        names = names[1:]
    return names


class _OwnBodySignals(ast.NodeVisitor):
    """Detect return/yield/raise statements belonging to a function's own body."""

    def __init__(self):  # noqa: ANN204
        self.returns_value = False
        self.yields_value = False
        self.raises_explicitly = False

    def visit_Return(self, node: ast.Return) -> None:
        """Record a `return <value>` that isn't a bare `return None`."""
        is_none_literal = isinstance(node.value, ast.Constant) and node.value.value is None
        if node.value is not None and not is_none_literal:
            self.returns_value = True

    def visit_Yield(self, node: ast.Yield) -> None:
        """Record a `yield <value>` that isn't a bare `yield`."""
        if node.value is not None:
            self.yields_value = True

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        """Record a `yield from` delegation as yielding a value."""
        del node  # unused: any `yield from` delegation counts
        self.yields_value = True

    def visit_Raise(self, node: ast.Raise) -> None:
        """Record an explicit `raise <exc>`, ignoring a bare re-raise."""
        if node.exc is not None:
            self.raises_explicitly = True

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Skip a nested function's own body."""

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Skip a nested function's own body."""

    def visit_Lambda(self, node: ast.Lambda) -> None:
        """Skip a lambda's own body."""


def _missing_docstring_sections(node: ast.FunctionDef | ast.AsyncFunctionDef, docstring: str) -> list[str]:
    """Determine which applicable structured sections a docstring omits.

    A pytest test function (`test_*`) is exempt from `Args:` even when it
    takes fixture parameters — fixtures are dependency-injected, not
    documented per-argument; the test docstring instead states what/why
    (optionally a `Spec:`/`Scenario:` pointer to the spec file).

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): Function to inspect.
        docstring (str): The function's cleaned docstring.

    Returns:
        list[str]: Section markers that apply but are absent, e.g. `"Args:"`.
    """
    signals = _OwnBodySignals()
    for statement in node.body:
        signals.visit(statement)

    is_pytest_test = node.name.startswith("test_")
    applicable = {
        "Args:": bool(_real_parameter_names(node)) and not is_pytest_test,
        "Returns:": signals.returns_value,
        "Yields:": signals.yields_value,
        "Raises:": signals.raises_explicitly,
    }
    return [marker for marker, applies in applicable.items() if applies and marker not in docstring]


def _is_one_line_summary(docstring: str) -> bool:
    """Check whether a cleaned docstring has no content beyond its summary.

    Args:
        docstring (str): The function's cleaned docstring.

    Returns:
        bool: True if the docstring is a bare one-line summary.
    """
    return len(docstring.strip().splitlines()) <= 1


def _docstring_sections_all_or_nothing_violations(tree: ast.Module, *, file: Path) -> Iterator[ConventionViolation]:
    """Flag a multi-line docstring that omits a section that applies.

    Args:
        tree (ast.Module): Parsed module AST.
        file (Path): File the AST was parsed from, for reporting.

    Yields:
        ConventionViolation: One per missing-but-applicable section.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if node.name == "__init__":
            continue  # covered by init-docstring-shape
        docstring = ast.get_docstring(node, clean=True)
        if docstring is None or _is_one_line_summary(docstring):
            continue

        for section in _missing_docstring_sections(node, docstring):
            yield ConventionViolation(
                file=file,
                line=node.lineno,
                rule="docstring-sections-all-or-nothing",
                message=(
                    f"'{node.name}' docstring has more than a one-line summary "
                    f"but is missing the applicable {section!r} section — "
                    "document every applicable section or collapse to a "
                    "one-line summary"
                ),
            )


def _internal_constant_annotation_violations(tree: ast.Module, *, file: Path) -> Iterator[ConventionViolation]:
    """Flag a type-annotated internal module-level constant.

    Args:
        tree (ast.Module): Parsed module AST.
        file (Path): File the AST was parsed from, for reporting.

    Yields:
        ConventionViolation: One per annotated internal constant.
    """
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.AnnAssign):
            continue
        target = node.target
        if (
            isinstance(target, ast.Name)
            and target.id.startswith("_")
            and not target.id.startswith("__")
            and target.id[1:].isupper()
        ):
            yield ConventionViolation(
                file=file,
                line=node.lineno,
                rule="internal-constant-annotated",
                message=(f"internal constant '{target.id}' carries a type annotation; internal constants stay untyped"),
            )


def check_file(file: Path) -> list[ConventionViolation]:
    """Run every convention check against a single file.

    Args:
        file (Path): Python file to inspect.

    Returns:
        list[ConventionViolation]: Violations found, if any.
    """
    tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
    return [
        *_quoted_forward_ref_violations(tree, file=file),
        *_dataclass_kw_only_violations(tree, file=file),
        *_import_style_violations(tree, file=file),
        *_init_return_annotation_violations(tree, file=file),
        *_docstring_opener_violations(tree, file=file),
        *_docstring_field_opener_violations(tree, file=file),
        *_init_docstring_shape_violations(tree, file=file),
        *_docstring_sections_all_or_nothing_violations(tree, file=file),
        *_internal_constant_annotation_violations(tree, file=file),
    ]


def check_conventions(paths: Sequence[Path]) -> list[ConventionViolation]:
    """Run every convention check against a set of files or directories.

    Args:
        paths (Sequence[Path]): Files or directories to scan.

    Returns:
        list[ConventionViolation]: All violations found, unsorted.
    """
    violations: list[ConventionViolation] = []
    for file in _iter_python_files(paths):
        violations.extend(check_file(file))
    return violations


def _report(violations: list[ConventionViolation]) -> int:
    """Write a human-readable report and compute the process exit code.

    Args:
        violations (list[ConventionViolation]): Violations to report.

    Returns:
        int: ``0`` when there are no violations, otherwise ``1``.
    """
    if not violations:
        sys.stdout.write("python-conventions: no violations found.\n")
        return 0
    sys.stderr.write("python-conventions: violations found:\n")
    for violation in sorted(violations, key=lambda v: (str(v.file), v.line)):
        sys.stderr.write(f"  - {violation.file}:{violation.line} [{violation.rule}] {violation.message}\n")
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the convention checks and return a process exit code.

    Args:
        argv (Sequence[str] | None): Optional CLI arguments naming files or
            directories to scan; defaults to ``src`` and ``tests``.

    Returns:
        int: ``0`` on success, ``1`` when violations are found.
    """
    args = list(argv if argv is not None else sys.argv[1:])
    paths = [Path(arg) for arg in args] if args else [Path("src"), Path("tests")]
    return _report(check_conventions(paths))


if __name__ == "__main__":
    raise SystemExit(main())
