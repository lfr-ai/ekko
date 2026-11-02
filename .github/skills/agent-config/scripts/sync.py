"""Sync mirrored skill bundles from the canonical ``.agents/skills`` tree.

Closes a real gap: keeping ``.github/skills``, ``.claude/skills``, and
``.agents/skills`` byte-identical today means hand-running ``Copy-Item`` per
touched file plus a manual hash check. ``verify_agent_config.py`` already
detects drift (read-only, pre-commit gate); this script is the write-side
counterpart it does not provide — copy canonical files into the two provider
mirrors on request.

This script is read-only unless ``--apply`` is given. It never deletes a file
that exists only in a mirror (not in canonical) — removing an extra is a
human-reviewed decision, not an automatic one.

Usage:
    uv run python .agents/skills/agent-config/scripts/sync.py
    uv run python .agents/skills/agent-config/scripts/sync.py --apply

Exit codes:
    0 - every mirror already matches canonical (or now does, after --apply)
    1 - drift found and --apply was not given
    2 - usage error (canonical skills root not found)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

_REPO_ROOT = Path(__file__).resolve().parents[4]
_CANONICAL_TREE = ".agents/skills"
_MIRROR_TREES = (".github/skills", ".claude/skills")


def _skill_files(skill_directory: Path) -> dict[str, bytes]:
    """Collect every file bundled with one skill.

    Args:
        skill_directory (Path): Directory containing ``SKILL.md`` and resources.

    Returns:
        dict[str, bytes]: Relative file paths mapped to content.
    """
    if not skill_directory.is_dir():
        return {}
    return {
        path.relative_to(skill_directory).as_posix(): path.read_bytes()
        for path in skill_directory.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def _iter_skill_dirs(canonical_root: Path) -> Iterator[Path]:
    for skill_md in sorted(canonical_root.rglob("SKILL.md")):
        yield skill_md.parent


def _sync_skill(
    *,
    skill_id: str,
    canonical_dir: Path,
    mirror_root: Path,
    mirror_tree: str,
    apply: bool,
) -> list[str]:
    """Compare and, when requested, copy one skill into one mirror tree.

    Args:
        skill_id (str): Canonical skill identifier (relative path under the tree).
        canonical_dir (Path): Canonical skill directory to copy from.
        mirror_root (Path): Mirror skill-tree root (e.g. ``.github/skills``).
        mirror_tree (str): Mirror tree label (e.g. ``.github/skills``).
        apply (bool): Copy canonical files into the mirror when ``True``.

    Returns:
        list[str]: Human-readable messages, one per missing/differing file.
    """
    expected = _skill_files(canonical_dir)
    mirror_dir = mirror_root / skill_id
    actual = _skill_files(mirror_dir)
    missing = expected.keys() - actual.keys()
    differing = {
        path
        for path in expected.keys() & actual.keys()
        if expected[path] != actual[path]
    }
    messages: list[str] = []
    for rel_path in sorted(missing | differing):
        reason = "missing" if rel_path in missing else "differs"
        messages.append(f"{skill_id}: {mirror_tree} {reason}: {rel_path}")
        if apply:
            destination = mirror_dir / rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(canonical_dir / rel_path, destination)
    return messages


def main(argv: list[str] | None = None) -> int:
    """Report (and optionally fix) skill-mirror drift against canonical."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="copy canonical files into the mirrors (never deletes extras)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_REPO_ROOT,
        help="repo root containing the skill trees (default: inferred)",
    )
    args = parser.parse_args(argv)

    canonical_root = args.repo_root / _CANONICAL_TREE
    if not canonical_root.is_dir():
        print(
            f"error: canonical skills root not found: {canonical_root}", file=sys.stderr
        )
        return 2

    messages: list[str] = []
    for skill_dir in _iter_skill_dirs(canonical_root):
        skill_id = skill_dir.relative_to(canonical_root).as_posix()
        for mirror_tree in _MIRROR_TREES:
            messages.extend(
                _sync_skill(
                    skill_id=skill_id,
                    canonical_dir=skill_dir,
                    mirror_root=args.repo_root / mirror_tree,
                    mirror_tree=mirror_tree,
                    apply=args.apply,
                )
            )

    for message in messages:
        print(message)

    if not messages:
        print("All skill mirrors match the canonical .agents/skills tree.")
        return 0
    if args.apply:
        print("Applied: canonical files copied into mirrors.")
        return 0
    print("Run again with --apply to copy canonical files into the mirrors.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
