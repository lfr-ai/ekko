"""Check for hardcoded magic strings that should be constants.

Scans ``backend/src/ekko/`` and reports string literals that should be extracted
into named constants. Run locally or in CI to enforce string constant consistency.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess  # nosec B404
import sys
from dataclasses import dataclass
from enum import StrEnum, auto, unique
from pathlib import Path
from typing import Final

ROOT: Final = Path(__file__).resolve().parents[2]
SRC: Final = ROOT / "backend" / "src" / "ekko"
REGISTRY: Final = ROOT / "registry" / "naming_registry.json"
TESTS: Final = ROOT / "tests"
EXCEPTIONS_FILE: Final = (
    ROOT / "tools" / "conventions" / "magic_strings_exceptions.json"
)


@unique
class ViolationCategory(StrEnum):
    """Categories of magic string violations."""

    FIELD_NAME = auto()
    ROUTE_PATH = auto()
    STATUS_VALUE = auto()
    MESSAGE_ROLE = auto()
    ENUM_VALUE = auto()
    UNKNOWN = auto()


@dataclass(frozen=True, slots=True)
class Violation:
    """Magic string violation."""

    file: Path
    line: int
    column: int
    literal: str
    category: ViolationCategory
    context: str
    suggested_fix: str


@dataclass(frozen=True, slots=True)
class Exception:
    """Exception for a known legitimate string literal."""

    file: str
    line: int
    literal: str
    reason: str


# Common field names that should be constants
FIELD_PATTERNS: Final = {
    "id",
    "name",
    "status",
    "role",
    "label",
    "type",
    "username",
    "email",
    "created_at",
    "updated_at",
    "timestamp",
    "content",
    "message",
    "data",
    "value",
    "key",
    "token",
    "session_id",
    "user_id",
    "request_id",
}

# Status values that should be enums or constants
STATUS_PATTERNS: Final = {
    "completed",
    "failed",
    "pending",
    "processing",
    "queued",
    "received",
    "cancelled",
    "active",
    "inactive",
    "success",
    "error",
}

# Message role keys
ROLE_PATTERNS: Final = {"system", "user", "assistant", "tool"}

# Exclusion patterns (regex)
EXCLUSION_PATTERNS: Final = [
    re.compile(r"^\s*logger\.(debug|info|warning|error|critical)"),  # Log calls
    re.compile(r"^\s*raise\s+\w+Error"),  # Exception messages
    re.compile(r'^\s*"""'),  # Docstrings
    re.compile(r"^\s*'''"),  # Docstrings
    re.compile(r"#.*external-api"),  # External API payloads (anywhere in line)
    re.compile(r"Literal\["),  # Type hints with Literal
]


def _load_registry() -> dict[str, dict[str, dict[str, str]]]:
    """Load naming registry JSON.

    Returns:
        Registry data structure.
    """
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _load_exceptions() -> list[Exception]:
    """Load exceptions from JSON file.

    Returns:
        List of exceptions. Empty list if file does not exist.
    """
    if not EXCEPTIONS_FILE.exists():
        return []

    data = json.loads(EXCEPTIONS_FILE.read_text(encoding="utf-8"))
    return [
        Exception(
            file=exc["file"],
            line=exc["line"],
            literal=exc["literal"],
            reason=exc["reason"],
        )
        for exc in data.get("exceptions", [])
    ]


def _is_exception(violation: Violation, exceptions: list[Exception]) -> bool:
    """Check if a violation matches an exception.

    Args:
        violation: Violation to check.
        exceptions: List of known exceptions.

    Returns:
        True if violation is in exceptions list.
    """
    # Normalize paths for cross-platform comparison
    violation_file = str(violation.file).replace("\\", "/")
    return any(
        exc.file.replace("\\", "/") == violation_file
        and exc.line == violation.line
        and exc.literal == violation.literal
        for exc in exceptions
    )


def _is_excluded_file(path: Path) -> bool:
    """Check if file should be excluded from scanning.

    Args:
        path: File path to check.

    Returns:
        True if file should be excluded.
    """
    # Exclude tests
    if str(path).startswith(str(TESTS)):
        return True
    # Exclude __init__.py (often has imports only)
    if path.name == "__init__.py":
        return True
    # Exclude generated files
    if "registry_constants.py" in str(path):
        return True
    return False


def _is_excluded_context(line_content: str, prev_line: str) -> bool:
    """Check if line context should be excluded.

    Args:
        line_content: Current line content.
        prev_line: Previous line content.

    Returns:
        True if context should be excluded.
    """
    for pattern in EXCLUSION_PATTERNS:
        if pattern.search(line_content) or pattern.search(prev_line):
            return True
    return False


def _categorize_literal(literal: str) -> ViolationCategory:
    """Categorize a string literal.

    Args:
        literal: String literal to categorize.

    Returns:
        Violation category.
    """
    # Check route paths
    if literal.startswith("/"):
        return ViolationCategory.ROUTE_PATH

    # Check field names
    if literal in FIELD_PATTERNS:
        return ViolationCategory.FIELD_NAME

    # Check status values
    if literal in STATUS_PATTERNS:
        return ViolationCategory.STATUS_VALUE

    # Check message roles
    if literal in ROLE_PATTERNS:
        return ViolationCategory.MESSAGE_ROLE

    return ViolationCategory.UNKNOWN


def _suggest_fix(literal: str, category: ViolationCategory) -> str:
    """Suggest a fix for the violation.

    Args:
        literal: String literal.
        category: Violation category.

    Returns:
        Suggested fix description.
    """
    if category == ViolationCategory.ROUTE_PATH:
        constant_name = literal.strip("/").replace("/", "_").upper()
        return f"Extract to ROUTE_{constant_name} constant or use registry"

    if category == ViolationCategory.FIELD_NAME:
        constant_name = literal.upper()
        return f"Use FIELD_{constant_name} from registry_constants or define locally"

    if category == ViolationCategory.STATUS_VALUE:
        constant_name = literal.upper()
        return f"Use STATUS_{constant_name} enum value or define locally"

    if category == ViolationCategory.MESSAGE_ROLE:
        return f"Use MessageRole.{literal.upper()} enum value"

    return "Extract to named constant"


def _parse_file_ast(path: Path) -> list[Violation]:
    """Parse file using AST and detect magic strings.

    Args:
        path: Python file to parse.

    Returns:
        List of violations found.
    """
    violations: list[Violation] = []

    try:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()
        tree = ast.parse(content, filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return violations

    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant):
            continue
        if not isinstance(node.value, str):
            continue

        literal = node.value
        # Skip empty strings and very short strings
        if len(literal) < 2:
            continue

        # Get line content for context checking
        line_idx = node.lineno - 1
        line_content = lines[line_idx] if line_idx < len(lines) else ""
        prev_line = lines[line_idx - 1] if line_idx > 0 else ""

        # Check exclusions
        if _is_excluded_context(line_content, prev_line):
            continue

        # Categorize the literal
        category = _categorize_literal(literal)
        if category == ViolationCategory.UNKNOWN:
            continue

        # Try to make path relative to ROOT, but use absolute if not possible
        try:
            rel_path = path.relative_to(ROOT)
        except ValueError:
            rel_path = path

        violations.append(
            Violation(
                file=rel_path,
                line=node.lineno,
                column=node.col_offset,
                literal=literal,
                category=category,
                context=line_content.strip(),
                suggested_fix=_suggest_fix(literal, category),
            )
        )

    return violations


def _scan_with_ripgrep(pattern: str, category: ViolationCategory) -> list[Violation]:
    """Scan using ripgrep for efficient pattern matching.

    Args:
        pattern: Regex pattern to search for.
        category: Category for found violations.

    Returns:
        List of violations found.
    """
    violations: list[Violation] = []

    try:
        result = subprocess.run(  # nosec B603 B607
            [
                "rg",
                "--json",
                "--no-heading",
                "--line-number",
                "--column",
                pattern,
                str(SRC),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        for line in result.stdout.splitlines():
            try:
                data = json.loads(line)
                if data.get("type") != "match":
                    continue

                match_data = data.get("data", {})
                path_data = match_data.get("path", {})
                file_path = Path(path_data.get("text", ""))

                if _is_excluded_file(file_path):
                    continue

                line_number = match_data.get("line_number", 0)
                lines = match_data.get("lines", {})
                context = lines.get("text", "").strip()

                # Extract the literal from the context
                # This is a simplified extraction - AST parsing is more accurate
                match = re.search(r'["\']([^"\']+)["\']', context)
                if not match:
                    continue

                literal = match.group(1)
                violations.append(
                    Violation(
                        file=file_path.relative_to(ROOT),
                        line=line_number,
                        column=0,
                        literal=literal,
                        category=category,
                        context=context,
                        suggested_fix=_suggest_fix(literal, category),
                    )
                )
            except (json.JSONDecodeError, KeyError):
                continue

    except FileNotFoundError:
        # ripgrep not available, skip
        pass

    return violations


def _scan_directory() -> list[Violation]:
    """Scan directory for magic strings.

    Returns:
        List of all violations found.
    """
    violations: list[Violation] = []

    # AST-based scanning for comprehensive detection
    for py_file in sorted(SRC.rglob("*.py")):
        if _is_excluded_file(py_file):
            continue
        violations.extend(_parse_file_ast(py_file))

    return violations


def _filter_violations(
    violations: list[Violation],
    *,
    category: ViolationCategory | None = None,
    exclude_files: list[str] | None = None,
) -> list[Violation]:
    """Filter violations by criteria.

    Args:
        violations: List of violations to filter.
        category: Filter by specific category.
        exclude_files: List of file patterns to exclude.

    Returns:
        Filtered list of violations.
    """
    filtered = violations

    if category:
        filtered = [v for v in filtered if v.category == category]

    if exclude_files:
        patterns = [re.compile(pattern) for pattern in exclude_files]
        filtered = [
            v for v in filtered if not any(p.search(str(v.file)) for p in patterns)
        ]

    return filtered


def _print_violations(violations: list[Violation], *, verbose: bool = False) -> None:
    """Print violations report.

    Args:
        violations: List of violations to report.
        verbose: Include full context and suggested fixes.
    """
    if not violations:
        print("No magic string violations found.")
        return

    # Group by category
    by_category: dict[ViolationCategory, list[Violation]] = {}
    for v in violations:
        by_category.setdefault(v.category, []).append(v)

    print(f"Found {len(violations)} magic string violations:\n")

    for category in sorted(by_category.keys(), key=lambda c: c.value):
        violations_in_cat = by_category[category]
        print(f"=== {category.upper()} ({len(violations_in_cat)}) ===\n")

        for v in violations_in_cat:
            print(f"  {v.file}:{v.line}:{v.column}")
            print(f'    Literal: "{v.literal}"')
            if verbose:
                print(f"    Context: {v.context}")
                print(f"    Fix: {v.suggested_fix}")
            print()


def main() -> int:
    """Scan for magic strings and report violations.

    Returns:
        Process exit code (1 if violations found, 0 otherwise).
    """
    parser = argparse.ArgumentParser(
        description="Check for hardcoded magic strings that should be constants."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show full context and suggested fixes",
    )
    parser.add_argument(
        "--category",
        choices=[c.value for c in ViolationCategory],
        help="Filter by specific category",
    )
    parser.add_argument(
        "--exclude-file",
        action="append",
        dest="exclude_files",
        help="File pattern to exclude (can be specified multiple times)",
    )

    args = parser.parse_args()

    # Load exceptions
    exceptions = _load_exceptions()

    violations = _scan_directory()

    # Filter out exceptions
    violations = [v for v in violations if not _is_exception(v, exceptions)]

    # Apply filters
    category_filter = ViolationCategory(args.category) if args.category else None
    violations = _filter_violations(
        violations,
        category=category_filter,
        exclude_files=args.exclude_files,
    )

    _print_violations(violations, verbose=args.verbose)

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
