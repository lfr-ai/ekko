"""Synchronize agentic assets across .github, .claude, and .agents surfaces.

This script ensures parity between the three agent runtime surfaces:
- `.github/` (VS Code / Copilot)
- `.claude/` (Claude Code CLI)
- `.agents/` (neutral canonical topology)

Run after updating skills, prompts, commands, or agents in any surface.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import structlog

GITHUB_DIR = ".github"
CLAUDE_DIR = ".claude"
AGENTS_DIR = ".agents"

logger = structlog.get_logger(__name__)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _copy_file(*, source: Path, target: Path) -> bool:
    """Copy source file to target when content differs.

    Returns:
        bool: Whether target content changed.
    """
    _ensure_dir(target.parent)
    if target.exists() and source.read_bytes() == target.read_bytes():
        return False

    shutil.copy2(source, target)
    return True


def _remove_stale_gitkeep(root: Path) -> int:
    removed = 0
    for marker in root.rglob(".gitkeep"):
        parent = marker.parent
        siblings = [path for path in parent.iterdir() if path.name != ".gitkeep"]
        if siblings:
            marker.unlink(missing_ok=True)
            removed += 1
    return removed


def sync_skills(*, root: Path) -> int:
    """Sync SKILL.md files from .github/skills to .claude/skills and .agents/skills."""
    changes = 0
    source_root = root / GITHUB_DIR / "skills"
    target_roots = [
        root / AGENTS_DIR / "skills",
        root / CLAUDE_DIR / "skills",
    ]

    for source in source_root.rglob("SKILL.md"):
        relative_path = source.relative_to(source_root)
        for target_root in target_roots:
            target = target_root / relative_path
            if _copy_file(source=source, target=target):
                changes += 1
    return changes


def sync_open_spec_prompts(*, root: Path) -> int:
    """Sync flat opsx-*.prompt.md to grouped openspec/ folders."""
    changes = 0
    source_root = root / GITHUB_DIR / "prompts"
    target_roots = [
        root / GITHUB_DIR / "prompts" / "openspec",
        root / AGENTS_DIR / "prompts" / "openspec",
    ]

    for source in source_root.glob("opsx-*.prompt.md"):
        renamed = source.name.replace("opsx-", "", 1)
        for target_root in target_roots:
            if _copy_file(source=source, target=target_root / renamed):
                changes += 1
    return changes


def sync_open_spec_commands(*, root: Path) -> int:
    """Sync .claude/commands/opsx/ to grouped openspec/ folders."""
    changes = 0
    source_root = root / CLAUDE_DIR / "commands" / "opsx"
    target_roots = [
        root / CLAUDE_DIR / "commands" / "openspec",
        root / AGENTS_DIR / "commands" / "openspec",
    ]

    if not source_root.exists():
        return changes

    for source in source_root.glob("*.md"):
        for target_root in target_roots:
            if _copy_file(source=source, target=target_root / source.name):
                changes += 1
    return changes


def sync_agents(*, root: Path) -> int:
    """Sync .claude/agents/ profiles to .agents/agents/."""
    changes = 0
    source_root = root / CLAUDE_DIR / "agents"
    target_root = root / AGENTS_DIR / "agents"

    for source in source_root.glob("*.md"):
        if _copy_file(source=source, target=target_root / source.name):
            changes += 1
    return changes


def ensure_gitnexus_scaffolding(*, root: Path) -> int:
    """Bootstrap GitNexus prompt/command scaffolding in all relevant folders."""
    changes = 0
    prompt_template = """---
description: Investigate {name} concerns with GitNexus and summarize blast radius before edits.
---

Use GitNexus to perform **{name}** analysis before implementing changes.

Required behavior:

1. Find relevant symbols/processes with `mcp_gitnexus_query`.
2. Inspect critical symbols with `mcp_gitnexus_context`.
3. Assess risk using `mcp_gitnexus_impact` for touched symbols.
4. Summarize impacted modules/processes and recommended safe change order.
5. If risk is HIGH/CRITICAL, propose staged rollout with validation checkpoints.
"""
    command_template = """---
name: "GitNexus: {title}"
description: Run {name} workflow with GitNexus before code changes.
category: Analysis
tags: [gitnexus, architecture, risk]
---

Run a GitNexus **{name}** workflow:

1. Start with `mcp_gitnexus_query` for semantic process discovery.
2. Use `mcp_gitnexus_context` on top candidate symbols.
3. Run `mcp_gitnexus_impact` upstream with depth 2-3 for blast radius.
4. Return findings grouped as: direct impact, transitive impact, test priorities.
5. Recommend the safest incremental refactoring sequence.
"""

    prompt_targets = {
        root / GITHUB_DIR / "prompts" / "gitnexus" / "impact.prompt.md": "impact",
        root / GITHUB_DIR / "prompts" / "gitnexus" / "debug.prompt.md": "debug",
        root / AGENTS_DIR / "prompts" / "gitnexus" / "impact.prompt.md": "impact",
        root / AGENTS_DIR / "prompts" / "gitnexus" / "debug.prompt.md": "debug",
    }
    command_targets = {
        root / CLAUDE_DIR / "commands" / "gitnexus" / "impact.md": ("impact", "Impact Analysis"),
        root / CLAUDE_DIR / "commands" / "gitnexus" / "debug.md": ("debug", "Debug Analysis"),
        root / AGENTS_DIR / "commands" / "gitnexus" / "impact.md": ("impact", "Impact Analysis"),
        root / AGENTS_DIR / "commands" / "gitnexus" / "debug.md": ("debug", "Debug Analysis"),
    }

    for path, name in prompt_targets.items():
        _ensure_dir(path.parent)
        content = prompt_template.format(name=name)
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
            changes += 1

    for path, (name, title) in command_targets.items():
        _ensure_dir(path.parent)
        content = command_template.format(name=name, title=title)
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
            changes += 1

    return changes


def main() -> None:
    root = _repo_root()
    updated_files = 0

    updated_files += sync_skills(root=root)
    updated_files += sync_open_spec_prompts(root=root)
    updated_files += sync_open_spec_commands(root=root)
    updated_files += sync_agents(root=root)
    updated_files += ensure_gitnexus_scaffolding(root=root)
    updated_files += _remove_stale_gitkeep(root / AGENTS_DIR)
    updated_files += _remove_stale_gitkeep(root / GITHUB_DIR / "prompts")
    updated_files += _remove_stale_gitkeep(root / CLAUDE_DIR / "commands")

    logger.info("sync_agentic_setup_complete", updated_files=updated_files)


if __name__ == "__main__":
    main()
