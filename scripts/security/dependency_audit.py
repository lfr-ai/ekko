"""Run dependency vulnerability audit for the backend."""

import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_PROJECT_DIRECTORY = _REPO_ROOT / "backend"
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.common import _constant as _shared_constants  # noqa: E402 — import after sys.path setup

_PIP_AUDIT = "pip-audit"
_IGNORED_VULNERABILITIES = (
    # Ignored while upstream transitive dependency graph remains unresolved.
    "GHSA-xf7x-x43h-rpqh",
    # Ignored while upstream transitive dependency graph remains unresolved.
    "PYSEC-2026-311",
)


def _run_dependency_audit() -> int:
    """Export dependencies and run 'pip-audit'.

    Returns:
        int: Exit code.
    """
    with tempfile.TemporaryDirectory(prefix="ekko-dependency-audit-") as temporary_directory:
        requirements_path = Path(temporary_directory) / "requirements.txt"
        pip_audit_command = [
            "uv",
            "run",
            "--with",
            _PIP_AUDIT,
            "pip-audit",
            "-r",
            str(requirements_path),
            "--desc",
            "on",
            "--no-deps",
            "--disable-pip",
            *[arg for vulnerability in _IGNORED_VULNERABILITIES for arg in ("--ignore-vuln", vulnerability)],
        ]

        try:
            subprocess.run(
                [
                    "uv",
                    "export",
                    "--project",
                    str(_BACKEND_PROJECT_DIRECTORY),
                    "--all-groups",
                    "--no-hashes",
                    "--frozen",
                    "-o",
                    str(requirements_path),
                ],
                check=True,
                shell=False,
            )
            subprocess.run(pip_audit_command, check=True, shell=False)
        except subprocess.CalledProcessError:
            return _shared_constants.EXIT_FAILURE

    return _shared_constants.EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(_run_dependency_audit())
