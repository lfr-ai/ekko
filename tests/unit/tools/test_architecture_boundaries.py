"""Tests for the Clean Architecture boundary gate.

The gate delegates to import-linter (contracts in ``backend/pyproject.toml``).
These tests assert the contracts are declared and that the repository currently
satisfies every contract.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
_CHECKER = _ROOT / "tools" / "security" / "check_architecture_boundaries.py"
_BACKEND_PYPROJECT = _ROOT / "backend" / "pyproject.toml"

_EXPECTED_CONTRACTS = frozenset(
    {
        "Clean Architecture layers",
        "AI and Infrastructure are independent siblings",
        "Presentation must not reach into infrastructure or AI",
        "Core is framework-independent",
    }
)

_EXPECTED_LAYERS = (
    "cli",
    "composition",
    "presentation",
    "application",
    "ai",
    "infrastructure",
    "core",
    "config",
)


def _load_contracts() -> list[dict[str, object]]:
    data = tomllib.loads(_BACKEND_PYPROJECT.read_text(encoding="utf-8"))
    return data["tool"]["importlinter"]["contracts"]


@pytest.mark.unit
def test_expected_contracts_are_defined() -> None:
    """The import-linter config declares every Clean Architecture contract."""
    names = {contract["name"] for contract in _load_contracts()}
    assert names >= _EXPECTED_CONTRACTS


@pytest.mark.unit
def test_layers_contract_covers_every_layer() -> None:
    """The layers contract lists all architectural layers, inner to outer."""
    layers_contract = next(c for c in _load_contracts() if c["type"] == "layers")
    joined = " ".join(layers_contract["layers"])
    for layer in _EXPECTED_LAYERS:
        assert f"ekko.{layer}" in joined


@pytest.mark.unit
def test_repository_satisfies_all_contracts() -> None:
    """The repository passes the import-linter architecture gate (exit code 0)."""
    result = subprocess.run(  # noqa: S603 — fixed local command with trusted input
        [sys.executable, str(_CHECKER)],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
