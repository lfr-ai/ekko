"""Tests that enforce the repository-wide Python runtime policy."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[3]
_EXPECTED_MINOR = "3.14"
_EXPECTED_REQUIRES_PYTHON = ">=3.14,<3.15"
_EXPECTED_RUFF_TARGET = "py314"


@pytest.mark.unit
def test_python_runtime_declarations_are_consistent() -> None:
    """Active runtime declarations should select the supported Python line."""
    pyproject = tomllib.loads((_ROOT / "backend/pyproject.toml").read_text(encoding="utf-8"))
    ruff = tomllib.loads((_ROOT / "ruff.toml").read_text(encoding="utf-8"))
    root_ty = tomllib.loads((_ROOT / "ty.toml").read_text(encoding="utf-8"))
    backend_ty = tomllib.loads((_ROOT / "backend/ty.toml").read_text(encoding="utf-8"))
    pre_commit = yaml.safe_load((_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8"))

    assert (_ROOT / ".python-version").read_text(encoding="utf-8").strip() == _EXPECTED_MINOR
    assert (_ROOT / "backend/.python-version").read_text(encoding="utf-8").strip() == _EXPECTED_MINOR
    assert pyproject["project"]["requires-python"] == _EXPECTED_REQUIRES_PYTHON
    assert ruff["target-version"] == _EXPECTED_RUFF_TARGET
    assert root_ty["environment"]["python-version"] == _EXPECTED_MINOR
    assert backend_ty["environment"]["python-version"] == _EXPECTED_MINOR
    assert pre_commit["default_language_version"]["python"] == f"python{_EXPECTED_MINOR}"


@pytest.mark.unit
@pytest.mark.parametrize(
    "relative_path",
    [
        ".github/workflows/ci.yml",
        ".github/workflows/codecov.yml",
        "docker/Containerfile",
        ".devcontainer/Containerfile.dev",
    ],
)
def test_automation_does_not_reference_retired_python_runtime(relative_path: str) -> None:
    """Automation and images should not select the retired Python line."""
    content = (_ROOT / relative_path).read_text(encoding="utf-8")

    assert re.search(r"(?<![\d.])3\.12(?![\d.])", content) is None
