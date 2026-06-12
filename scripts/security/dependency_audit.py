"""Run dependency vulnerability audit for the backend."""

import os
import subprocess
import tempfile
from pathlib import Path

try:
    from common import _constant as _shared_constants
except ModuleNotFoundError:
    from scripts.common import _constant as _shared_constants

_AUDIT_GROUP = "audit"
_PIP_AUDIT = "pip-audit"
_IGNORED_VULNERABILITIES: tuple[str, ...] = ()


def _run_dependency_audit() -> int:
    """Export dependencies and run 'pip-audit'.

    Returns:
        int: Exit code.
    """
    file_descriptor, temporary_path = tempfile.mkstemp(
        prefix="ekko-requirements-",
        suffix=".txt",
    )
    os.close(file_descriptor)
    requirements_path = Path(temporary_path)

    pip_audit_command = [
        "uv",
        "tool",
        "run",
        "--from",
        _PIP_AUDIT,
        "pip-audit",
        "-r",
        str(requirements_path),
        "--desc",
        "on",
        "--no-deps",
        "--disable-pip",
        *[arg for vuln in _IGNORED_VULNERABILITIES for arg in ("--ignore-vuln", vuln)],
    ]

    try:
        subprocess.run(
            [
                "uv",
                "export",
                "--project",
                "backend",
                "--all-groups",
                "--no-group",
                _AUDIT_GROUP,
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
    finally:
        requirements_path.unlink(missing_ok=True)

    return _shared_constants.EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(_run_dependency_audit())
