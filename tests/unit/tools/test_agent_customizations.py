"""Tests for agent customization validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

TOOLS_PATH = Path(__file__).resolve().parents[3] / "tools" / "conventions"
sys.path.insert(0, str(TOOLS_PATH))

from check_agent_customizations import validate  # noqa: E402


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_valid_tree(root: Path) -> None:
    skill = "---\nname: example\ndescription: Use for example tasks.\n---\n\n# Example\n"
    for skill_root in (".github/skills", ".claude/skills", ".agents/skills"):
        _write(root / skill_root / "example" / "SKILL.md", skill)

    _write(
        root / ".github/agents/example.agent.md",
        "---\nname: Example\ndescription: Example agent.\ntools: ['context7/*']\n---\n",
    )
    _write(
        root / ".claude/agents/example.md",
        "---\nname: example\ndescription: Example agent.\ntools: Read, Grep\n---\n",
    )
    _write(
        root / ".github/prompts/example.prompt.md",
        "---\ndescription: Run an example task.\n---\n",
    )
    _write(root / ".github/instructions/example.instructions.md", "---\napplyTo: '**'\n---\n")
    _write(root / ".claude/rules/example.md", "---\npaths: ['**']\n---\n")

    vscode_manifest = {"servers": {"context7": {"type": "http", "url": "https://example.invalid"}}}
    generic_manifest = {"mcpServers": {"context7": {"type": "http", "url": "https://example.invalid"}}}
    _write(root / ".vscode/mcp.json", json.dumps(vscode_manifest))
    _write(root / ".mcp.json", json.dumps(generic_manifest))
    _write(root / ".claude/mcp.json", json.dumps(generic_manifest))


@pytest.mark.unit
def test_validate_with_consistent_customizations_returns_no_violations(tmp_path: Path) -> None:
    """A complete aligned customization tree passes validation."""
    _write_valid_tree(tmp_path)

    violations = validate(root=tmp_path)

    assert violations == []


@pytest.mark.unit
def test_validate_with_mismatched_skill_name_reports_violation(tmp_path: Path) -> None:
    """A skill name that differs from its directory is rejected."""
    _write_valid_tree(tmp_path)
    _write(
        tmp_path / ".github/skills/example/SKILL.md",
        "---\nname: wrong-name\ndescription: Use for example tasks.\n---\n",
    )

    messages = [violation.message for violation in validate(root=tmp_path)]

    assert any("must match its directory" in message for message in messages)


@pytest.mark.unit
def test_validate_with_unconfigured_agent_mcp_server_reports_violation(tmp_path: Path) -> None:
    """An agent cannot request tools from an undeclared MCP server."""
    _write_valid_tree(tmp_path)
    _write(
        tmp_path / ".github/agents/example.agent.md",
        "---\nname: Example\ndescription: Example agent.\ntools: ['missing/*']\n---\n",
    )

    messages = [violation.message for violation in validate(root=tmp_path)]

    assert "references unconfigured MCP server 'missing'" in messages


@pytest.mark.unit
def test_validate_with_mcp_manifest_drift_reports_violation(tmp_path: Path) -> None:
    """All runtime MCP manifests must expose the same server keys."""
    _write_valid_tree(tmp_path)
    _write(
        tmp_path / ".claude/mcp.json",
        json.dumps({"mcpServers": {"other": {"url": "https://example.invalid"}}}),
    )

    messages = [violation.message for violation in validate(root=tmp_path)]

    assert "MCP server keys differ across manifests" in messages


@pytest.mark.unit
@pytest.mark.parametrize(
    ("guidance", "expected_message"),
    [
        ("Use Python 3.12 for this task.", "references the retired Python 3.12 runtime"),
        ("JSONDict = dict[str, Any]", "recommends Any-based dictionary typing"),
        ("Use utils -> config -> core.", "references the removed utils architecture layer"),
        ("Run git status before continuing.", "instructs an agent to run prohibited Git shell commands"),
    ],
)
def test_validate_with_stale_guidance_reports_violation(
    tmp_path: Path,
    guidance: str,
    expected_message: str,
) -> None:
    """Active customization text cannot reintroduce retired policies."""
    _write_valid_tree(tmp_path)
    _write(
        tmp_path / ".github/prompts/example.prompt.md",
        f"---\ndescription: Run an example task.\n---\n\n{guidance}\n",
    )

    messages = [violation.message for violation in validate(root=tmp_path)]

    assert expected_message in messages


@pytest.mark.unit
def test_validate_with_implicit_http_mcp_transport_reports_violation(tmp_path: Path) -> None:
    """Generic HTTP MCP definitions require an explicit transport type."""
    _write_valid_tree(tmp_path)
    _write(
        tmp_path / ".mcp.json",
        json.dumps({"mcpServers": {"context7": {"url": "https://example.invalid"}}}),
    )

    messages = [violation.message for violation in validate(root=tmp_path)]

    assert "HTTP MCP server 'context7' requires type 'http'" in messages
