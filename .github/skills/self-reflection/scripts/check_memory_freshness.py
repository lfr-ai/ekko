"""Flag stale file references inside repo memory markdown files.

Closes a real gap: memory notes cite exact paths (`file:line`, backtick
paths, or markdown links) as evidence, but nothing re-checks those paths
still exist after the code they describe is renamed, moved, or deleted — a
memory note is only useful if the next agent can still verify it.

This script is read-only and stdlib-only. It does not understand markdown
semantics deeply; it extracts two literal patterns per line — backtick-quoted
paths (`` `src/foo/bar.py` ``) and markdown link targets (`[text](path)`) —
and reports any that look like a repo-relative path but do not exist on disk.
It is intentionally conservative (see `_looks_like_path`) to avoid false
positives on code identifiers, command flags, or prose that happens to
contain a slash or a dot.

Usage:
    uv run python check_memory_freshness.py memories/lessons.md memories/decisions.md
    uv run python check_memory_freshness.py memories/**/*.md

Exit codes:
    0 - every extracted path exists (or no paths were found)
    1 - at least one extracted path does not exist (printed, one per line)
    2 - usage error (a given file does not exist)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

_BACKTICK_PATH = re.compile(r"`([\w./-]+/[\w./-]+)`")
_MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)#\s]+)\)")
_URL_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
_PATH_LIKE_SUFFIXES = frozenset(
    {
        ".py",
        ".md",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".sql",
        ".ts",
        ".tsx",
        ".js",
        ".cjs",
        ".mjs",
    }
)


def _looks_like_path(candidate: str) -> bool:
    """Filter out command flags, code identifiers, and external URLs."""
    if _URL_SCHEME.match(candidate):
        return False
    if candidate.startswith(("-", "--", "#")):
        return False
    if "/" not in candidate:
        return False
    return Path(candidate).suffix in _PATH_LIKE_SUFFIXES


def _extract_candidates(text: str) -> Iterator[str]:
    for match in _BACKTICK_PATH.finditer(text):
        yield match.group(1)
    for match in _MARKDOWN_LINK.finditer(text):
        yield match.group(1)


def _stale_paths(memory_file: Path, *, repo_root: Path) -> list[str]:
    text = memory_file.read_text(encoding="utf-8")
    stale: list[str] = []
    seen: set[str] = set()
    for candidate in _extract_candidates(text):
        if not _looks_like_path(candidate) or candidate in seen:
            continue
        seen.add(candidate)
        resolved = (memory_file.parent / candidate).resolve()
        root_resolved = (repo_root / candidate).resolve()
        if not resolved.exists() and not root_resolved.exists():
            stale.append(candidate)
    return stale


def main(argv: list[str] | None = None) -> int:
    """Scan each memory file given on the CLI for paths that no longer exist."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "memory_files",
        nargs="+",
        type=Path,
        help="one or more memory markdown files",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="repo root to resolve repo-relative paths against (default: cwd)",
    )
    args = parser.parse_args(argv)

    exit_code = 0
    for memory_file in args.memory_files:
        if not memory_file.is_file():
            print(f"error: not a file: {memory_file}", file=sys.stderr)
            return 2
        stale = _stale_paths(memory_file, repo_root=args.repo_root)
        if stale:
            exit_code = 1
            print(f"{memory_file}:")
            for path in stale:
                print(f"  stale reference: {path}")

    if exit_code == 0:
        print("No stale path references found.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
