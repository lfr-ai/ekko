"""Validate Clean Architecture import boundaries via import-linter.

The contracts are defined in ``backend/.importlinter``. This module is the
single stable entrypoint used by pre-commit, the Taskfile, CI, and the verify
scripts, so every gate runs the same authoritative check. Invoke it with the
backend environment active::

    uv run --project backend python tools/security/check_architecture_boundaries.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_BACKEND = _ROOT / "backend"


def _resolve_lint_imports() -> str | None:
    """Locate the ``lint-imports`` console script.

    Searches ``PATH`` first, then the active interpreter's script directory so
    the gate works whether Python was launched through ``uv run`` (which puts the
    virtual environment on ``PATH``) or invoked directly.

    Returns:
        str | None: Executable path when import-linter is installed.
    """
    on_path = shutil.which("lint-imports")
    if on_path is not None:
        return on_path
    return shutil.which("lint-imports", path=str(Path(sys.executable).parent))


def main() -> int:
    """Run the import-linter contracts and return a process exit code."""
    lint_imports = _resolve_lint_imports()
    if lint_imports is None:
        sys.stderr.write(
            "import-linter not found. Install backend dev dependencies first:\n  uv sync --project backend\n"
        )
        return 1

    result = subprocess.run(
        [lint_imports, "--config", ".importlinter"],
        cwd=_BACKEND,
        env={**os.environ, "PYTHONPATH": "src"},
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
