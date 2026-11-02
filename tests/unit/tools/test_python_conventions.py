"""Tests for supplemental Python convention checks."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

_CHECKER_PATH = Path(__file__).resolve().parents[3] / ".agents" / "skills" / "python-conventions" / "scripts"
sys.path.insert(0, str(_CHECKER_PATH))

from check_conventions import _internal_constant_annotation_violations  # noqa: E402


@pytest.mark.unit
def test_internal_constant_annotation_reports_private_constant() -> None:
    tree = ast.parse("_MAX_RETRIES: int = 3")

    violations = list(_internal_constant_annotation_violations(tree, file=Path("sample.py")))

    assert [violation.rule for violation in violations] == ["internal-constant-annotated"]


@pytest.mark.unit
def test_internal_constant_annotation_ignores_private_state_and_dunder_exports() -> None:
    tree = ast.parse("_request_id_var: ContextVar[str | None] = ContextVar('request_id')\n__all__: list[str] = []")

    violations = list(_internal_constant_annotation_violations(tree, file=Path("sample.py")))

    assert violations == []
