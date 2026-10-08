"""Scaffold an isolated git worktree for a second, concurrently-running agent
session — a fresh worktree directory plus a derived `.env.local` overriding
every port/name a dev server or Docker Compose stack could collide on with
the primary worktree (or any other agent's worktree).

Never run by an agent: `AGENTS.md` Hard Rule 11 forbids agents from executing
`git`. This is an operator-run setup script — symmetric with the
`az repos policy create` commands the `azure-devops-pipeline` skill documents
for a human to run, not something dispatched from inside an agent session.

The derived port and Compose project name are a deterministic hash of the
branch name, so re-running this script for the same branch always reproduces
the same values (safe to re-run after a worktree was removed and recreated).

Usage::

    uv run python .agents/skills/parallel-agents/scripts/new_agent_worktree.py \\
        <branch> [--base <base-branch>] [--path <worktree-path>] \\
        [--port-env-var APP_PORT] [--db-name-env-var POSTGRES_DB] \\
        [--base-port 8000]

Example (project-specific env var names)::

    uv run python .agents/skills/parallel-agents/scripts/new_agent_worktree.py \\
        feat/retrieval-tuning --port-env-var MYAPP_PORT --db-name-env-var MYAPP_POSTGRESQL_NAME
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

_PORT_OFFSET_RANGE = 500
_DEFAULT_BASE_PORT = 8000
_DEFAULT_PORT_ENV_VAR = "APP_PORT"
_DEFAULT_DB_NAME_ENV_VAR = "POSTGRES_DB"


def _slug(branch: str) -> str:
    """Convert a branch name to a filesystem/Compose-safe slug.

    Args:
        branch (str): Branch name, e.g. `"feat/rag-tuning"`.

    Returns:
        str: Lowercase slug with only `[a-z0-9-]`, e.g. `"feat-rag-tuning"`.
    """
    return "".join(c if c.isalnum() else "-" for c in branch).strip("-").lower()


def _derived_port(branch: str, *, base_port: int) -> int:
    """Derive a stable, collision-resistant port offset from the branch name.

    Args:
        branch (str): Branch name the worktree is created for.
        base_port (int): The primary worktree's port; the derived port never
            equals it.

    Returns:
        int: A port in `(base_port, base_port + _PORT_OFFSET_RANGE]`.
    """
    digest = hashlib.sha256(branch.encode()).hexdigest()
    return base_port + 1 + (int(digest[:8], 16) % _PORT_OFFSET_RANGE)


def _env_local_contents(
    *, branch: str, port: int, port_env_var: str, db_name_env_var: str
) -> str:
    """Render the isolating `.env.local` overrides for one worktree.

    Args:
        branch (str): Branch name the worktree is created for.
        port (int): Derived, collision-resistant application port.
        port_env_var (str): Environment variable the app reads its port from.
        db_name_env_var (str): Environment variable the app reads its
            database name from.

    Returns:
        str: Complete `.env.local` file contents.
    """
    slug = _slug(branch)
    lines = [
        f"# Auto-generated for branch '{branch}' by new_agent_worktree.py.",
        "# Isolates this worktree's dev server and Docker Compose stack from",
        "# every other worktree of the same repository running concurrently.",
        f"COMPOSE_PROJECT_NAME={slug}",
        f"{port_env_var}={port}",
        f"{db_name_env_var}={slug.replace('-', '_')}",
        "",
    ]
    return "\n".join(lines)


def _run_git(args: Sequence[str]) -> None:
    """Run one git command, propagating a non-zero exit as a subprocess error.

    Args:
        args (Sequence[str]): Arguments passed after `git`.

    Raises:
        subprocess.CalledProcessError: If the git command exits non-zero.
    """
    subprocess.run(["git", *args], check=True)  # noqa: S603


def main(argv: Sequence[str] | None = None) -> int:
    """Create an isolated worktree and its collision-free `.env.local`.

    Args:
        argv (Sequence[str] | None): Optional CLI arguments; defaults to
            `sys.argv[1:]`.

    Returns:
        int: `0` on success, non-zero if `git worktree add` fails.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("branch", help="Branch name for the new worktree")
    parser.add_argument("--base", default="HEAD", help="Base ref (default: HEAD)")
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Worktree directory (default: '../<repo-name>-<branch-slug>')",
    )
    parser.add_argument("--base-port", type=int, default=_DEFAULT_BASE_PORT)
    parser.add_argument("--port-env-var", default=_DEFAULT_PORT_ENV_VAR)
    parser.add_argument("--db-name-env-var", default=_DEFAULT_DB_NAME_ENV_VAR)
    args = parser.parse_args(argv)

    slug = _slug(args.branch)
    repo_root = Path.cwd().resolve()
    worktree = args.path or repo_root.parent / f"{repo_root.name}-{slug}"

    try:
        _run_git(["worktree", "add", "-b", args.branch, str(worktree), args.base])
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"git worktree add failed: {exc}\n")
        return exc.returncode or 1

    port = _derived_port(args.branch, base_port=args.base_port)
    (worktree / ".env.local").write_text(
        _env_local_contents(
            branch=args.branch,
            port=port,
            port_env_var=args.port_env_var,
            db_name_env_var=args.db_name_env_var,
        ),
        encoding="utf-8",
    )

    sys.stdout.write(f"Worktree ready at {worktree}\n")
    sys.stdout.write(
        f"  COMPOSE_PROJECT_NAME={slug}  {args.port_env_var}={port}  "
        f"{args.db_name_env_var}={slug.replace('-', '_')}\n"
    )
    sys.stdout.write(
        "Next: cd into it, run the project's onboarding task to fill in "
        "secrets, then sync dependencies before starting the agent session.\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
