"""Check class-name and filename correspondence beyond Ruff/Biome checks.

Ruff and Biome check symbol casing, not whether a filename matches its class.

Three read-only AST checks:

- ``single-class-filename``: a module defining exactly one top-level public
  class must be named after it (its PascalCase name converted to
  snake_case), optionally with one recognized layer-role suffix (``Port``,
  ``Client``, ``Repository``, ``Store``, ``Settings``, ``Config``,
  ``Handler``, ``Orchestrator``, ``Service``, ``Manager``, ``Container``,
  ``Middleware``, ``Filter``, ``Formatter``) stripped — the suffix is only
  safe to drop from the filename for a strict Port<->Adapter pair whose bare
  concept name is unique in the tree (``ports/repositories/order.py`` ->
  ``OrderRepositoryPort``); it must stay whenever the bare concept name recurs
  elsewhere under a different role (``application/handlers/
  expiry_handler.py``, never bare ``expiry.py``, which would
  collide with the unrelated ``core/policies/expiry_policy.py``
  concept) — see the `consistency` skill's Naming section for the full test
  and worked examples. This check accepts either spelling rather than
  inferring which applies from the folder name alone, since that requires a
  repo-wide same-name search a folder path can't answer on its own.
- ``multi-class-file``: 2+ top-level public classes in one module is only
  legitimate for a themed/data module that groups a cohesive family of
  types by theme (``errors``/``exceptions``, ``enums``, ``models``,
  ``types``, ``value_objects``, ``events``, ``dtos``, ``constants``) — a
  single behavioral component (handler, client, port, repository, store,
  orchestrator, service, manager, config, container) owns exactly one
  public class per module.
- ``private-name-exported``: a module-level ``__all__`` entry must never
  name a leading-underscore (private) symbol — that defeats the point of
  marking it private.

Run standalone::

    uv run python .agents/skills/consistency/scripts/check_class_file_naming.py [path ...]

Exit status is non-zero when any violation is found.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

_DEFAULT_ROOTS = (
    Path("src"),
    Path("backend/src"),
    Path("backend/alembic"),
    Path("scripts"),
    Path("tools"),
    Path("registry"),
)

# Filenames that legitimately group a cohesive family of types (or a single
# framework-adapter concern, e.g. "logging") by theme rather than defining
# one single-purpose behavioral component — exempt from both the
# single-class-filename and multi-class-file checks.
_THEMED_STEMS = frozenset(
    {
        "__init__",
        "constants",
        "dtos",
        "enums",
        "errors",
        "events",
        "exceptions",
        "logging",
        "middleware",
        "models",
        "types",
        "value_objects",
    }
)

# Folders whose files follow a topical/abbreviated naming convention instead
# of a mechanical class-name derivation (e.g. `configs/settings/paths.py` ->
# `PathSettings`, `configs/environments/dev.py` -> `DevelopmentConfig`) —
# exempt entirely from both checks rather than special-casing every file.
_EXEMPT_FOLDER_PARTS = frozenset({"config", "configs"})

# Layer-role suffixes a behavioral class name may carry; stripped when
# checking whether the filename matches, since the folder often already
# names the role (see module docstring).
_ROLE_SUFFIXES = (
    "Port",
    "Client",
    "Repository",
    "Store",
    "Settings",
    "Config",
    "Handler",
    "Orchestrator",
    "Service",
    "Manager",
    "Container",
    "Middleware",
    "Filter",
    "Formatter",
)

_ACRONYM_BOUNDARY_1 = re.compile(r"(.)([A-Z][a-z]+)")
_ACRONYM_BOUNDARY_2 = re.compile(r"([a-z0-9])([A-Z])")


@dataclass(frozen=True, kw_only=True, slots=True)
class NamingViolation:
    """One class/filename-naming convention breach."""

    path: Path
    line: int
    rule: str
    message: str


def _to_snake_case(name: str) -> str:
    """Convert a PascalCase identifier to snake_case, acronym-aware.

    Args:
        name (str): PascalCase identifier, e.g. ``'OCRScannerClient'``.

    Returns:
        str: snake_case form, e.g. ``'ocr_scanner_client'``.
    """
    step1 = _ACRONYM_BOUNDARY_1.sub(r"\1_\2", name)
    step2 = _ACRONYM_BOUNDARY_2.sub(r"\1_\2", step1)
    return step2.lower()


def _strip_role_suffixes(name: str) -> set[str]:
    """Recursively strip every recognized role suffix a name ends with.

    A compound role name like ``OrderRepositoryPort`` layers two suffixes
    (``Repository`` + ``Port``) that a folder path may drop together (e.g.
    ``ports/repositories/order.py``), so stripping must repeat until no
    further recognized suffix remains.

    Args:
        name (str): PascalCase name to strip, at any stripping depth.

    Returns:
        set[str]: The name itself plus every shorter form reachable by
            stripping one recognized suffix at a time.
    """
    variants = {name}
    for suffix in _ROLE_SUFFIXES:
        if name.endswith(suffix) and len(name) > len(suffix):
            variants |= _strip_role_suffixes(name[: -len(suffix)])
    return variants


def _candidate_stems(class_name: str) -> set[str]:
    """Build every filename stem accepted for a given class name.

    Includes the full snake_case conversion and, for each combination of
    recognized role suffixes the class name ends with, the conversion with
    those suffixes stripped.

    Args:
        class_name (str): Public top-level class name.

    Returns:
        set[str]: Accepted snake_case filename stems.
    """
    return {_to_snake_case(variant) for variant in _strip_role_suffixes(class_name)}


def _top_level_public_classes(tree: ast.Module) -> list[ast.ClassDef]:
    """Collect public (non-underscore) top-level class definitions.

    Args:
        tree (ast.Module): Parsed module AST.

    Returns:
        list[ast.ClassDef]: Public top-level classes, in source order.
    """
    return [
        node for node in ast.iter_child_nodes(tree) if isinstance(node, ast.ClassDef) and not node.name.startswith("_")
    ]


def _is_exempt_module(path: Path) -> bool:
    """Whether a module is out of scope for the behavioral-naming checks.

    Exempts themed/data modules, private (leading-underscore) modules, and
    files under a folder with its own topical naming convention.

    Args:
        path (Path): File under inspection.

    Returns:
        bool: True when the module should be skipped entirely.
    """
    if path.stem in _THEMED_STEMS or path.stem.startswith("_"):
        return True
    return any(part in _EXEMPT_FOLDER_PARTS for part in path.parts)


def _role_suffixed_classes(classes: list[ast.ClassDef]) -> list[ast.ClassDef]:
    """Filter to classes whose name carries a recognized layer-role suffix.

    Args:
        classes (list[ast.ClassDef]): Candidate top-level classes.

    Returns:
        list[ast.ClassDef]: Classes ending in a role suffix (Port, Client,
            Repository, ...) — the behavioral components a module should
            carry at most one of.
    """
    return [c for c in classes if c.name.endswith(_ROLE_SUFFIXES)]


def _single_class_filename_violation(tree: ast.Module, *, path: Path) -> Iterator[NamingViolation]:
    """Flag a single-public-class module whose filename doesn't match it.

    Args:
        tree (ast.Module): Parsed module AST.
        path (Path): File the AST was parsed from.

    Yields:
        NamingViolation: At most one, when the sole public class's name
            doesn't correspond to the filename.
    """
    if _is_exempt_module(path):
        return
    public_classes = _role_suffixed_classes(_top_level_public_classes(tree))
    if len(public_classes) != 1:
        return
    (node,) = public_classes
    candidates = _candidate_stems(node.name)
    if path.stem not in candidates:
        yield NamingViolation(
            path=path,
            line=node.lineno,
            rule="single-class-filename",
            message=(
                f"class '{node.name}' does not match filename '{path.name}' "
                f"(expected one of: {', '.join(sorted(candidates))}.py)"
            ),
        )


def _multi_class_file_violation(tree: ast.Module, *, path: Path) -> Iterator[NamingViolation]:
    """Flag 2+ public top-level classes in a non-themed module.

    Args:
        tree (ast.Module): Parsed module AST.
        path (Path): File the AST was parsed from.

    Yields:
        NamingViolation: At most one, listing every public class found.
    """
    if _is_exempt_module(path):
        return
    public_classes = _role_suffixed_classes(_top_level_public_classes(tree))
    if len(public_classes) <= 1:
        return
    names = ", ".join(node.name for node in public_classes)
    yield NamingViolation(
        path=path,
        line=public_classes[0].lineno,
        rule="multi-class-file",
        message=(
            f"module defines {len(public_classes)} behavioral classes ({names}) — "
            "split into one file per behavioral component, or rename to a "
            "themed filename if these are genuinely one cohesive family"
        ),
    )


# Role word a `*Port` class must carry before the `Port` suffix when it lives
# directly under `ports/<folder>/` — keeps every port's own name self-
# describing (`ChatClientPort`, not bare `ChatPort`), matching the repository
# family's existing `OrderRepositoryPort` shape.
_PORT_FOLDER_ROLE_WORDS = {
    "clients": "Client",
    "repositories": "Repository",
    "stores": "Store",
}


def _is_dunder_all_assignment(node: ast.Assign) -> bool:
    """Whether an assignment node targets the module-level ``__all__`` list."""
    return any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)


def _private_string_elements(elts: list[ast.expr]) -> Iterator[str]:
    """Yield private (leading-underscore) string constants from a list/tuple literal."""
    for element in elts:
        if isinstance(element, ast.Constant) and isinstance(element.value, str) and element.value.startswith("_"):
            yield element.value


def _private_name_exported_violations(tree: ast.Module, *, path: Path) -> Iterator[NamingViolation]:
    """Flag a leading-underscore name listed in module-level ``__all__``.

    Args:
        tree (ast.Module): Parsed module AST.
        path (Path): File the AST was parsed from.

    Yields:
        NamingViolation: One per private name found in ``__all__``.
    """
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign) or not _is_dunder_all_assignment(node):
            continue
        if not isinstance(node.value, ast.List | ast.Tuple):
            continue
        for private_name in _private_string_elements(node.value.elts):
            yield NamingViolation(
                path=path,
                line=node.lineno,
                rule="private-name-exported",
                message=(
                    f"__all__ exports private name '{private_name}' — "
                    "remove the leading underscore or drop it from __all__"
                ),
            )


def _port_missing_category_suffix_violations(tree: ast.Module, *, path: Path) -> Iterator[NamingViolation]:
    """Flag a `*Port` class under `ports/<folder>/` missing that folder's role word.

    A port class must carry its own category word before the `Port` suffix
    (`ChatClientPort`, not bare `ChatPort`) so the type name is self-describing
    without needing the file path — matching the repository family's existing
    `OrderRepositoryPort` shape (see module docstring / consistency SKILL.md).

    Args:
        tree (ast.Module): Parsed module AST.
        path (Path): File the AST was parsed from.

    Yields:
        NamingViolation: One per `*Port` class missing the required role word.
    """
    if path.parent.parent.name != "ports":
        return
    category = _PORT_FOLDER_ROLE_WORDS.get(path.parent.name)
    if category is None:
        return
    for node in _top_level_public_classes(tree):
        if not node.name.endswith("Port") or node.name.endswith(f"{category}Port"):
            continue
        yield NamingViolation(
            path=path,
            line=node.lineno,
            rule="port-missing-category-suffix",
            message=(
                f"class '{node.name}' lives under 'ports/{path.parent.name}/' "
                f"but its name doesn't carry the '{category}' role word "
                f"(expected a name ending in '{category}Port')"
            ),
        )


def check_file(path: Path) -> list[NamingViolation]:
    """Run every class/filename-naming check against one source file.

    Args:
        path (Path): Python file to inspect.

    Returns:
        list[NamingViolation]: Violations found, in source order.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [
        *_single_class_filename_violation(tree, path=path),
        *_multi_class_file_violation(tree, path=path),
        *_private_name_exported_violations(tree, path=path),
        *_port_missing_category_suffix_violations(tree, path=path),
    ]


def _iter_python_files(paths: Sequence[Path]) -> Iterator[Path]:
    """Expand a mix of files and directories into concrete `.py` files.

    Args:
        paths (Sequence[Path]): Files or directories to scan.

    Yields:
        Path: Each `.py` file found, skipping caches.
    """
    for path in paths:
        if path.is_dir():
            for candidate in path.rglob("*.py"):
                if "__pycache__" not in candidate.parts:
                    yield candidate
        elif path.suffix == ".py":
            yield path


def check_class_file_naming(paths: Sequence[Path]) -> list[NamingViolation]:
    """Run every check against a set of files or directories.

    Args:
        paths (Sequence[Path]): Files or directories to scan.

    Returns:
        list[NamingViolation]: All violations found, unsorted.
    """
    violations: list[NamingViolation] = []
    for file in _iter_python_files(paths):
        violations.extend(check_file(file))
    return violations


def _report(violations: list[NamingViolation]) -> int:
    """Write a human-readable report and compute the process exit code.

    Args:
        violations (list[NamingViolation]): Violations to report.

    Returns:
        int: ``0`` when there are no violations, otherwise ``1``.
    """
    if not violations:
        sys.stdout.write("consistency: no class/filename-naming violations found.\n")
        return 0
    sys.stderr.write("consistency: class/filename-naming violations found:\n")
    for violation in sorted(violations, key=lambda v: (str(v.path), v.line)):
        sys.stderr.write(f"  - {violation.path}:{violation.line} [{violation.rule}] {violation.message}\n")
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the checks and return a process exit code.

    Args:
        argv (Sequence[str] | None): Optional CLI arguments naming files or
            directories to scan; defaults to the repository's `src`.

    Returns:
        int: ``0`` on success, ``1`` when violations are found.
    """
    args = list(argv if argv is not None else sys.argv[1:])
    paths = [Path(arg) for arg in args] if args else list(_DEFAULT_ROOTS)
    return _report(check_class_file_naming(paths))


if __name__ == "__main__":
    raise SystemExit(main())
