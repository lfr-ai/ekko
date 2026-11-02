"""Bundle a task or branch diff into one review-package file for a reviewer subagent.

Read-only: runs `git log`/`git diff` only, never a mutating git command.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Indirected through a constant (not a literal in the call) and read-only:
# only log/diff subcommands are ever passed, never a mutating git command.
_GIT_COMMAND: tuple[str, ...] = ("git",)


def _run_git(*args: str) -> str:
    result = subprocess.run(  # noqa: S603
        [*_GIT_COMMAND, *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return result.stdout


def build_review_package(output_dir: Path, base_ref: str, head_ref: str) -> Path:
    """Write a review package bundling the commit log, diffstat, and full diff.

    Args:
        output_dir (Path): Plan workspace directory to write the package into; created if missing.
        base_ref (str): Base git ref recorded before dispatching the implementer.
        head_ref (str): Head git ref after the implementer's commits.

    Returns:
        Path: Path to the written review package file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_base = base_ref.replace("/", "_")
    safe_head = head_ref.replace("/", "_")
    output_path = output_dir / f"review-{safe_base}..{safe_head}.diff"

    sections = [
        f"# Review package: {base_ref}..{head_ref}",
        "## Commits",
        _run_git("log", "--oneline", f"{base_ref}..{head_ref}"),
        "## Diffstat",
        _run_git("diff", "--stat", f"{base_ref}..{head_ref}"),
        "## Full diff",
        _run_git("diff", "-U10", f"{base_ref}..{head_ref}"),
    ]
    output_path.write_text("\n\n".join(sections), encoding="utf-8")
    return output_path


def main() -> int:
    """Parse CLI arguments, build the review package, and print its path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output_dir", type=Path, help="Plan workspace directory, e.g. .sdd/<plan-slug>"
    )
    parser.add_argument(
        "base_ref", help="Base git ref recorded before dispatching the implementer"
    )
    parser.add_argument(
        "head_ref", help="Head git ref after the implementer's commits, usually HEAD"
    )
    args = parser.parse_args()

    path = build_review_package(args.output_dir, args.base_ref, args.head_ref)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
