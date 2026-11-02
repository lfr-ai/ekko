"""Guard the multi-runtime agent configuration.

The guard checks portable-skill boundaries, customization metadata, and parity
across skills, agents, scoped instructions, runtime hooks, and MCP declarations.

Run standalone (``uv run python .agents/guard/verify_agent_config.py``) or via
pre-commit. Exit status is non-zero when any violation is found.
"""

from __future__ import annotations

import ast
import json
import re
import sys
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_TREES = (".github/skills", ".claude/skills", ".agents/skills")
_PROJECT_SKILL_ROOT = "project"
_SKILL_FILE = "SKILL.md"
_SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SKILL_SCOPE_FIELDS = {"applyTo", "paths"}
_STANDARD_SKILL_FIELDS = {
    "allowed-tools",
    "compatibility",
    "description",
    "license",
    "metadata",
    "name",
}
_COMMAND_BACKED_SKILL_ROOTS = {"frontend", "ponytail", "project"}
_THIN_FACADE_SKILL_ROOTS = {"frontend", "ponytail"}
_EXPECTED_NESTED_SKILL_ROOTS = (
    "frontend",
    "gitnexus",
    "opsx",
    "ponytail",
    "project",
)
_EXPECTED_FAMILY_PROMPT_ROOTS = ("gitnexus", "opsx")
_RETIRED_FLAT_SKILL_IDS = {
    "accessibility": "frontend/accessibility",
    "frontend-configuration": "frontend/runtime-config",
    "frontend-debugging": "frontend/browser-debugging",
    "frontend-react-stack": "frontend/react-stack",
    "frontend-structure": "frontend/structure",
    "frontend-testing": "frontend/testing",
    "playwright": "frontend/playwright",
    "ponytail-audit": "ponytail/audit",
    "ponytail-debt": "ponytail/debt",
    "ponytail-help": "ponytail/quick-reference",
    "ponytail-review": "ponytail/overengineering-review",
    "shadcn-ui": "frontend/shadcn",
    "ui-ux-frontend": "frontend/ui-ux",
}
_VSCODE_SETTINGS_FILE = ".vscode/settings.json"
_CLAUDE_SETTINGS_FILE = ".claude/settings.json"
_PROJECT_IDENTITY_PREFIX = "- Agent portability tokens:"
_GITHUB_INSTRUCTIONS_DIR = ".github/instructions"
_CLAUDE_RULES_DIR = ".claude/rules"
_CLAUDE_COMMANDS_DIR = ".claude/commands"
# Non-skill portable prose that must also stay project-agnostic: scoped
# instructions/rules, agent profiles, and prompt/command facades. Skills get
# their own `_SKILL_TREES` scan because they alone support a `project/`
# subfolder carve-out; everything here has no such exemption.
_PORTABLE_PROSE_TREES = (
    _GITHUB_INSTRUCTIONS_DIR,
    _CLAUDE_RULES_DIR,
    ".github/agents",
    ".claude/agents",
    ".github/prompts",
    _CLAUDE_COMMANDS_DIR,
)
# The three always-loaded policy files are portable too: they carry the
# cross-runtime operating policy, defer every project fact to PROJECT.md, and
# load in full on every session/request — so a project token here leaks more
# broadly than one in a path-scoped instruction. Scanned as individual files
# (no tree glob) alongside the prose trees above.
_PORTABLE_ROOT_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
)

# Every agent runtime this repo targets loads these files in full on every
# session/request (VS Code: chat.useAgentsMdFile; Claude Code: CLAUDE.md +
# its @AGENTS.md import). Each budget is a FROZEN round ceiling: the next
# multiple of 5 above the file's current line count (guard method:
# content.count("\n") + 1), giving a clean, stable number with a few lines of
# natural headroom instead of an arbitrary max+1 value. Pinned by
# tests/unit/agent_config/test_verify_agent_config.py::test_line_budgets_are_frozen
# — NEVER raise a budget to fit new content; trim the file or relocate deep
# worked examples into the matching on-demand skill instead (the enforced
# rule, not a suggestion). AGENTS.md additionally must stay at or under 290:
# it is the ONE canonical policy loaded in full on every runtime, so
# Anthropic's <200-line CLAUDE.md guidance
# (docs.claude.com/en/docs/claude-code/memory) is knowingly exceeded — see the
# `agent-config` skill's "Canonical vs mirrored" section.
_POLICY_FILE_LINE_BUDGETS = {
    "AGENTS.md": 290,
    "CLAUDE.md": 65,
    ".github/copilot-instructions.md": 165,
}
# The root llms.txt (llms.txt standard) is read on demand, not auto-loaded
# every session like the policy files above, but it must stay a terse index
# (links only) rather than growing into a second documentation tree. 45 is
# the next multiple of 5 above its current line count — a FROZEN ceiling
# pinned by test_line_budgets_are_frozen, same rule as the budgets above:
# trim the file, never raise the number.
_LLMS_TXT_LINE_BUDGET = 45
# Scoped instructions/rules only load when an agent touches a matching path
# (applyTo/paths glob), not on every session — a looser budget than the
# always-loaded policy files above is warranted. 140 is the next multiple of 5
# above the densest current file (python-conventions instructions/rules at 137
# lines): a clean FROZEN ceiling with a few lines of headroom, pinned by
# test_line_budgets_are_frozen. Never raise it to fit new content — trim the
# file or move deep worked examples into the matching on-demand skill instead.
_SCOPED_INSTRUCTION_LINE_BUDGET = 140
_SCOPED_INSTRUCTION_GLOBS = (
    ".github/instructions/*.instructions.md",
    ".claude/rules/*.md",
)
# Agent profile files (`.github/agents/*.agent.md` + `.claude/agents/*.md`)
# load once per whole mode/subagent session, not every request — but nothing
# bounded their size before this budget, and it showed: `refactor.agent.md`
# and `testing.agent.md` had grown to 213/185 lines by inlining full worked
# code examples and tables already covered by their matching skill (`ddd`,
# `sdd`, `tdd`, `testing-conventions`). After moving that duplicated content
# to skills, the largest agent file is `refactor` at 121/122 lines; the
# per-agent "## Diagrams" blocks were removed in favor of one canonical
# directive in AGENTS.md's Response Format section. 125 is the next multiple
# of 5 above that — a clean FROZEN ceiling pinned by
# test_line_budgets_are_frozen; never raise it to fit new content, move
# duplicated examples/tables into the matching skill instead.
_AGENT_LINE_BUDGET = 125
# lessons.md/decisions.md are a growing historical log, not a static policy
# file, so this budget is a rotation trigger rather than a "never grows"
# ceiling: once either file exceeds it, consolidate (merge near-duplicate
# entries about the same evolving topic, move fully-resolved incident
# narratives to memories/archive/<file>.md verbatim) instead of raising the
# number. 500 matches the existing SKILL.md authoring limit (_check_skill_length)
# rather than a fresh arbitrary value. Pinned by test_line_budgets_are_frozen.
_MEMORY_LOG_LINE_BUDGET = 500
_MEMORY_LOG_FILES = ("memories/lessons.md", "memories/decisions.md")
_INSTRUCTION_RULE_PAIRS = {
    "api-contracts": "api-contracts",
    "python-conventions": "python-conventions",
    "cognitive-load": "cognitive-load",
    "css-conventions": "css-conventions",
    "database": "database",
    "ddd": "ddd",
    "frontend-tooling": "frontend-tooling",
    "jinja2": "jinja2",
    "markdown": "markdown",
    "prompt": "prompt",
    "pyinstaller": "pyinstaller",
    "react-conventions": "react-conventions",
    "repository-files": "repository-files",
    "sdd": "sdd",
    "shell": "shell",
    "tdd": "tdd",
    "testing": "testing",
    "typescript-conventions": "typescript-conventions",
    "update-docs-on-code-change": "update-docs-on-code-change",
    "agentic-config": "agentic-config",
    "ci-pipelines": "ci-pipelines",
    "containers": "containers",
    "devops": "devops",
    "memories": "memories",
}
_AGENT_DIRS = (".github/agents", ".claude/agents")
_WORKER_AGENT_IDS = {
    "backend-implementer",
    "code-reviewer",
    "codebase-researcher",
    "contract-iac-lint",
    "devops-implementer",
    "docs-writer",
    "frontend-implementer",
    "plan-architect",
    "planner",
    "security-reviewer",
    "solid-review",
    "test-author",
}
_EDITING_WORKER_AGENT_IDS = {
    "backend-implementer",
    "devops-implementer",
    "docs-writer",
    "frontend-implementer",
    "test-author",
}
# Workers live in this subfolder of each agent directory; primary modes and the
# orchestrator stay flat. Both runtimes discover agents recursively (subfolders
# are fine) but resolve a subagent by its kebab-case identifier (file basename),
# not its Title-Case ``name`` — verified live 2026-09-28 (`codebase-researcher`
# resolved via runSubagent, `Codebase Researcher` did not). So ``agents``
# allowlists and runSubagent calls must use the identifier; nesting only
# organizes the roster.
_WORKER_SUBFOLDER = "subagents"
_SMALL_MODEL_MARKERS = ("haiku", "mini")
_GITHUB_ROOT = ".github"
_GITHUB_AGENT_SUFFIX = ".agent.md"
_GITHUB_HOOKS_DIR = ".github/hooks"
_GITHUB_PROMPTS_DIR = ".github/prompts"
_SETUP_DIR = ".agents/agentic-setup"
_SETUP_PROFILES_FILE = ".agents/agentic-setup/profiles.json"
_SETUP_ASSETS_FILE = ".agents/agentic-setup/assets.json"
_PROFILE_CAPABILITIES = (
    "skills",
    "agents",
    "instructions",
    "mcpServers",
    "assets",
)
_TOOL_GUARD_FILE = ".agents/guard/tool-guardian.ts"
_HOOK_SCRIPT_PATTERN = re.compile(
    r"([a-z0-9-]+)\.(?:mjs|ps1|sh|ts)",
    re.IGNORECASE,
)
_MCP_FILES = {
    ".mcp.json": "mcpServers",
    ".vscode/mcp.json": "servers",
    ".claude/mcp.json": "mcpServers",
    ".warp/.mcp.json": "mcpServers",
}


def _skill_ids(tree: Path) -> set[str]:
    """Collect skill identifiers (relative directories) within a tree.

    Args:
        tree (Path): Absolute path to a ``<runtime>/skills`` directory.

    Returns:
        set[str]: POSIX-style relative directories that contain a ``SKILL.md``.
    """
    if not tree.is_dir():
        return set()
    return {
        skill.parent.relative_to(tree).as_posix() for skill in tree.rglob(_SKILL_FILE)
    }


def _portable_skill_files(tree: Path) -> list[Path]:
    """Collect portable ``SKILL.md`` files, excluding the ``project/`` subfolder.

    Args:
        tree (Path): Absolute path to a ``<runtime>/skills`` directory.

    Returns:
        list[Path]: ``SKILL.md`` paths whose skill is not project-scoped.
    """
    if not tree.is_dir():
        return []
    return [
        skill
        for skill in tree.rglob(_SKILL_FILE)
        if skill.relative_to(tree).parts[0] != _PROJECT_SKILL_ROOT
    ]


def _project_tokens() -> tuple[str, ...]:
    """Read explicit project identity tokens from ``PROJECT.md``.

    Returns:
        tuple[str, ...]: Tokens forbidden in portable skills.
    """
    project_file = _REPO_ROOT / "PROJECT.md"
    if not project_file.is_file():
        return ()
    for line in project_file.read_text(encoding="utf-8").splitlines():
        if line.startswith(_PROJECT_IDENTITY_PREFIX):
            return tuple(re.findall(r"`([^`]+)`", line))
    return ()


def _check_portability(tokens: tuple[str, ...]) -> list[str]:
    """Detect project-identifying tokens leaking into portable agent config.

    Scans each portable skill's ``SKILL.md`` plus its bundled ``assets/``,
    ``references/``, and ``scripts/`` resources, every scoped instruction/rule,
    agent profile, and prompt/command facade, and the three always-loaded root
    policy files (``AGENTS.md``, ``CLAUDE.md``,
    ``.github/copilot-instructions.md``) — a template, reference doc,
    agent-role file, or the canonical policy leaks project identity exactly
    like skill prose does.

    Args:
        tokens (tuple[str, ...]): Project identity tokens from ``PROJECT.md``.

    Returns:
        list[str]: Human-readable violation messages; empty when clean.
    """
    if not tokens:
        return [
            "PROJECT.md: missing '- Agent portability tokens:' identity declaration"
        ]
    alternatives = "|".join(re.escape(token) for token in tokens)
    token_pattern = re.compile(
        rf"(?<![A-Za-z0-9])(?:{alternatives})(?![A-Za-z0-9])",
        re.IGNORECASE,
    )
    violations: list[str] = []
    for tree_name in _SKILL_TREES:
        for skill in _portable_skill_files(_REPO_ROOT / tree_name):
            violations.extend(_skill_portability_violations(skill, token_pattern))
    violations.extend(
        violation
        for path in _portable_prose_files()
        if (violation := _portability_violation(path, token_pattern))
    )
    violations.extend(
        violation
        for name in _PORTABLE_ROOT_FILES
        if (root := _REPO_ROOT / name).is_file()
        if (violation := _portability_violation(root, token_pattern))
    )
    return violations


def _portable_prose_files() -> list[Path]:
    """Collect non-skill portable Markdown that must also stay project-agnostic.

    Returns:
        list[Path]: Every Markdown file under an instruction/rule, agent, or
            prompt/command tree (no ``project/``-style carve-out applies here).
    """
    files: list[Path] = []
    for tree_name in _PORTABLE_PROSE_TREES:
        tree = _REPO_ROOT / tree_name
        if tree.is_dir():
            files.extend(tree.rglob("*.md"))
    return files


def _skill_portability_violations(
    skill: Path, token_pattern: re.Pattern[str]
) -> list[str]:
    """Detect project tokens leaking into one skill's file and its resources.

    Args:
        skill (Path): Skill's ``SKILL.md`` path.
        token_pattern (re.Pattern[str]): Compiled pattern matching forbidden tokens.

    Returns:
        list[str]: Human-readable violation messages; empty when clean.
    """
    paths = [skill]
    for subdir in ("assets", "references", "scripts"):
        paths.extend(_skill_resource_paths(skill.parent, subdir))
    return [
        violation
        for path in paths
        if (violation := _portability_violation(path, token_pattern))
    ]


def _portability_violation(path: Path, token_pattern: re.Pattern[str]) -> str | None:
    """Detect a project token leaking into a single file.

    Args:
        path (Path): Candidate file to scan.
        token_pattern (re.Pattern[str]): Compiled pattern matching forbidden tokens.

    Returns:
        str | None: Violation message, or ``None`` when clean.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    match = token_pattern.search(text)
    if not match:
        return None
    rel = path.relative_to(_REPO_ROOT).as_posix()
    return (
        f"{rel}: portable file contains project token '{match.group()}' "
        "(read project facts from PROJECT.md; skills may move under project/, "
        "other config may not)"
    )


def _frontmatter(path: Path) -> list[str]:
    """Read YAML frontmatter lines without adding a YAML dependency.

    Args:
        path (Path): Markdown file with optional YAML frontmatter.

    Returns:
        list[str]: Frontmatter lines, or an empty list when absent.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return []
    try:
        end = lines.index("---", 1)
    except ValueError:
        return []
    return lines[1:end]


def _frontmatter_values(path: Path) -> dict[str, str]:
    """Read top-level scalar and folded frontmatter values.

    Args:
        path (Path): Markdown file with YAML frontmatter.

    Returns:
        dict[str, str]: Top-level frontmatter values keyed by field name.
    """
    lines = _frontmatter(path)
    values: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith((" ", "-")) or ":" not in line:
            index += 1
            continue
        key, _, raw_value = line.partition(":")
        value = raw_value.strip()
        if value not in {">", "|", ">-", "|-"}:
            values[key] = _unquote(value)
            index += 1
            continue
        folded: list[str] = []
        index += 1
        while index < len(lines) and lines[index].startswith(" "):
            folded.append(lines[index].strip())
            index += 1
        values[key] = " ".join(folded)
    return values


def _unquote(value: str) -> str:
    """Strip matching single or double quotes from a scalar.

    Args:
        value (str): Frontmatter scalar value.

    Returns:
        str: Unquoted scalar.
    """
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _split_globs(value: str) -> set[str]:
    """Split comma-delimited globs without splitting brace expressions.

    Args:
        value (str): One or more comma-delimited glob patterns.

    Returns:
        set[str]: Normalized glob patterns.
    """
    value = _unquote(value)
    patterns: set[str] = set()
    current: list[str] = []
    brace_depth = 0
    for character in value:
        if character == "{":
            brace_depth += 1
        elif character == "}":
            brace_depth = max(0, brace_depth - 1)
        if character == "," and brace_depth == 0:
            if pattern := _unquote("".join(current).strip()):
                patterns.update(_expand_braces(pattern))
            current = []
            continue
        current.append(character)
    if pattern := _unquote("".join(current).strip()):
        patterns.update(_expand_braces(pattern))
    return patterns


def _expand_braces(pattern: str) -> set[str]:
    """Expand one comma-delimited brace expression in a glob.

    Args:
        pattern (str): Glob pattern with optional brace alternatives.

    Returns:
        set[str]: Expanded patterns, or the original pattern when unbraced.
    """
    match = re.search(r"\{([^{}]+)\}", pattern)
    if match is None:
        return {pattern}
    prefix = pattern[: match.start()]
    suffix = pattern[match.end() :]
    return {f"{prefix}{option}{suffix}" for option in match.group(1).split(",")}


def _github_scope(path: Path) -> set[str]:
    """Read a GitHub instruction's ``applyTo`` scope.

    Args:
        path (Path): GitHub instruction file.

    Returns:
        set[str]: Normalized glob patterns.
    """
    for line in _frontmatter(path):
        if line.startswith("applyTo:"):
            return _split_globs(line.partition(":")[2])
    return set()


def _claude_scope(path: Path) -> set[str]:
    """Read a Claude rule's ``paths`` scope.

    Args:
        path (Path): Claude rule file.

    Returns:
        set[str]: Normalized glob patterns.
    """
    frontmatter = _frontmatter(path)
    for index, line in enumerate(frontmatter):
        if not line.startswith("paths:"):
            continue
        inline = line.partition(":")[2].strip()
        if inline:
            return _split_globs(inline.strip("[]"))
        patterns: set[str] = set()
        for nested in frontmatter[index + 1 :]:
            stripped = nested.strip()
            if not stripped.startswith("-"):
                break
            patterns.update(_expand_braces(_unquote(stripped[1:].strip())))
        return patterns
    return set()


def _check_instruction_rule_parity() -> list[str]:
    """Detect missing or differently scoped instruction/rule pairs.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    github_dir = _REPO_ROOT / _GITHUB_INSTRUCTIONS_DIR
    claude_dir = _REPO_ROOT / _CLAUDE_RULES_DIR
    expected_github = {f"{name}.instructions.md" for name in _INSTRUCTION_RULE_PAIRS}
    expected_claude = {f"{name}.md" for name in _INSTRUCTION_RULE_PAIRS.values()}
    actual_github = {path.name for path in github_dir.glob("*.instructions.md")}
    actual_claude = {path.name for path in claude_dir.glob("*.md")}
    violations = [
        f".github/instructions: unpaired instruction '{name}'"
        for name in sorted(actual_github - expected_github)
    ]
    violations.extend(
        f".claude/rules: unpaired rule '{name}'"
        for name in sorted(actual_claude - expected_claude)
    )
    for github_name, claude_name in _INSTRUCTION_RULE_PAIRS.items():
        github_path = github_dir / f"{github_name}.instructions.md"
        claude_path = claude_dir / f"{claude_name}.md"
        if not github_path.is_file():
            violations.append(f".github/instructions: missing '{github_path.name}'")
            continue
        if not claude_path.is_file():
            violations.append(f".claude/rules: missing '{claude_path.name}'")
            continue
        github_scope = _github_scope(github_path)
        claude_scope = _claude_scope(claude_path)
        if github_scope != claude_scope:
            violations.append(
                f"{github_name}: instruction/rule scope differs "
                f"({sorted(github_scope)} != {sorted(claude_scope)})"
            )
    return violations


def _instruction_rule_body(path: Path, *, strip_suffix: bool) -> str:
    """Read a scoped instruction/rule body, excluding YAML frontmatter.

    Args:
        path (Path): Instruction or rule markdown file.
        strip_suffix (bool): Normalize GitHub's ``.instructions.md`` self-references
            to Claude's bare ``.md`` so only real content differences remain.

    Returns:
        str: Body text after the closing frontmatter delimiter.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines and lines[0] == "---":
        try:
            end = lines.index("---", 1)
            lines = lines[end + 1 :]
        except ValueError:
            pass
    body = "\n".join(lines).strip()
    if strip_suffix:
        body = body.replace(".instructions.md", ".md")
    return body


def _check_instruction_rule_content_parity() -> list[str]:
    """Detect instruction/rule pairs whose bodies have drifted apart.

    Frontmatter (``applyTo``/``description`` vs ``paths``) is expected to
    differ per runtime and is excluded from comparison; only the Markdown
    body — the actual guidance an agent loads — must stay identical after
    normalizing GitHub's ``.instructions.md`` self-references to Claude's
    bare ``.md`` suffix. Deep worked examples belong in the shared skill, not
    a runtime-specific aside, so the two bodies should never need to differ.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    github_dir = _REPO_ROOT / _GITHUB_INSTRUCTIONS_DIR
    claude_dir = _REPO_ROOT / _CLAUDE_RULES_DIR
    violations: list[str] = []
    for github_name, claude_name in _INSTRUCTION_RULE_PAIRS.items():
        github_path = github_dir / f"{github_name}.instructions.md"
        claude_path = claude_dir / f"{claude_name}.md"
        if not github_path.is_file() or not claude_path.is_file():
            continue
        github_body = _instruction_rule_body(github_path, strip_suffix=True)
        claude_body = _instruction_rule_body(claude_path, strip_suffix=False)
        if github_body != claude_body:
            violations.append(
                f"{github_name}: instruction/rule body differs from "
                f"'.claude/rules/{claude_path.name}' (keep Markdown bodies "
                "identical; only frontmatter may differ)"
            )
    return violations


def _check_agentic_config_scope_coverage() -> list[str]:
    """Ensure the agentic-config instruction governs every managed surface.

    The ``agentic-config`` instruction/rule pair is the always-on layer an agent
    loads when editing agent configuration. If a governed surface (the MCP
    manifests, the ``llms.txt`` index, or the discovery settings files) falls
    outside its ``applyTo`` scope, an agent can edit that surface without the
    governance rules ever loading — the exact drift this check prevents.

    Returns:
        list[str]: Human-readable violation messages; empty when every governed
        surface is in scope.
    """
    instruction = _REPO_ROOT / ".github/instructions/agentic-config.instructions.md"
    if not instruction.is_file():
        return ["agentic-config: instruction file is missing"]
    scope = _github_scope(instruction)
    required = {
        *_MCP_FILES,
        "llms.txt",
        _VSCODE_SETTINGS_FILE,
        _CLAUDE_SETTINGS_FILE,
    }
    return [
        f"agentic-config: instruction applyTo must cover governed surface '{path}'"
        for path in sorted(required - scope)
    ]


def _check_parity() -> list[str]:
    """Detect skill sets diverging across the runtime trees.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    per_tree = {name: _skill_ids(_REPO_ROOT / name) for name in _SKILL_TREES}
    union = set().union(*per_tree.values())
    violations: list[str] = []
    for tree_name, skills in per_tree.items():
        violations.extend(
            f"{tree_name}: missing skill '{missing}'"
            for missing in sorted(union - skills)
        )
    return violations


def _skill_identity_violations(
    *,
    skill_id: str,
    name: str,
    expected_name: str,
    skill_ids_by_name: dict[str, str],
) -> list[str]:
    """Validate one skill's identifier and global name uniqueness.

    Args:
        skill_id (str): Repository-relative canonical skill identifier.
        name (str): Skill name declared in frontmatter.
        expected_name (str): Immediate parent directory name.
        skill_ids_by_name (dict[str, str]): Previously observed names and IDs.

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    if not name:
        return [f"{skill_id}: missing required skill name"]
    violations: list[str] = []
    if name != expected_name:
        violations.append(
            f"{skill_id}: skill name '{name}' must match directory '{expected_name}'"
        )
    elif len(name) > 64 or _SKILL_NAME_PATTERN.fullmatch(name) is None:
        violations.append(f"{skill_id}: invalid Agent Skills name '{name}'")
    if existing_skill_id := skill_ids_by_name.get(name):
        violations.append(
            f"{skill_id}: duplicate skill name '{name}' also used by "
            f"'{existing_skill_id}'"
        )
    else:
        skill_ids_by_name[name] = skill_id
    return violations


def _skill_description_violations(*, skill_id: str, description: str) -> list[str]:
    """Validate one skill description.

    Args:
        skill_id (str): Repository-relative canonical skill identifier.
        description (str): Skill description declared in frontmatter.

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    if not description:
        return [f"{skill_id}: missing required skill description"]
    if len(description) > 1024:
        return [f"{skill_id}: skill description exceeds 1024 characters"]
    return []


def _skill_field_violations(*, skill_id: str, values: dict[str, str]) -> list[str]:
    """Validate portable fields in one skill's frontmatter.

    Args:
        skill_id (str): Repository-relative canonical skill identifier.
        values (dict[str, str]): Parsed top-level frontmatter values.

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    violations: list[str] = []
    if nonstandard_fields := set(values) - _STANDARD_SKILL_FIELDS:
        fields = ", ".join(sorted(nonstandard_fields))
        violations.append(
            f"{skill_id}: non-portable skill frontmatter field(s): {fields}"
        )
    if misplaced_scopes := _SKILL_SCOPE_FIELDS.intersection(values):
        fields = ", ".join(sorted(misplaced_scopes))
        violations.append(
            f"{skill_id}: path scope field(s) {fields} belong in instructions/rules"
        )
    return violations


def _check_skill_metadata() -> list[str]:
    """Detect invalid canonical Agent Skills metadata.

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    canonical = _REPO_ROOT / _SKILL_TREES[-1]
    violations: list[str] = []
    skill_ids_by_name: dict[str, str] = {}
    for skill in sorted(canonical.rglob(_SKILL_FILE)):
        skill_id = skill.parent.relative_to(canonical).as_posix()
        values = _frontmatter_values(skill)
        name = values.get("name", "")
        description = values.get("description", "")
        expected_name = skill.parent.name
        violations.extend(
            _skill_identity_violations(
                skill_id=skill_id,
                name=name,
                expected_name=expected_name,
                skill_ids_by_name=skill_ids_by_name,
            )
        )
        violations.extend(
            _skill_description_violations(
                skill_id=skill_id,
                description=description,
            )
        )
        violations.extend(_skill_field_violations(skill_id=skill_id, values=values))
    return violations


def _skill_resource_paths(skill_directory: Path, subdir: str) -> list[Path]:
    """Collect files bundled under one skill's resource subdirectory.

    Args:
        skill_directory (Path): Directory containing ``SKILL.md`` and resources.
        subdir (str): Bundled resource subdirectory name (e.g. ``assets``).

    Returns:
        list[Path]: Files under ``skill_directory/subdir``, recursively.
    """
    root = skill_directory / subdir
    if not root.is_dir():
        return []
    return [path for path in sorted(root.rglob("*")) if path.is_file()]


def _check_template_syntax() -> list[str]:
    """Detect syntax errors in bundled Python, JSON, and TOML template assets.

    Returns:
        list[str]: Human-readable violation messages; empty when all parse.
    """
    canonical = _REPO_ROOT / _SKILL_TREES[-1]
    violations: list[str] = []
    for skill in sorted(canonical.rglob(_SKILL_FILE)):
        skill_id = skill.parent.relative_to(canonical).as_posix()
        for path in _skill_resource_paths(skill.parent, "assets"):
            try:
                content = path.read_text(encoding="utf-8")
                if path.name.endswith((".py.template", ".spec.template")):
                    ast.parse(content)
                elif path.name.endswith(".json.template"):
                    json.loads(content)
                elif path.name.endswith(".toml.template"):
                    tomllib.loads(content)
            except (
                SyntaxError,
                json.JSONDecodeError,
                tomllib.TOMLDecodeError,
            ) as error:
                violations.append(
                    f"{skill_id}: {path.name} has invalid template syntax ({error})"
                )
    return violations


def _check_skill_resource_references() -> list[str]:
    """Detect bundled assets/references that are orphaned or broken-linked.

    Every file under a skill's ``assets/`` or ``references/`` directory must be
    linked from its ``SKILL.md`` (discoverable), and every such link in
    ``SKILL.md`` must resolve to a real file (not broken).

    Returns:
        list[str]: Human-readable violation messages; empty when all linked.
    """
    canonical = _REPO_ROOT / _SKILL_TREES[-1]
    violations: list[str] = []
    for skill in sorted(canonical.rglob(_SKILL_FILE)):
        skill_id = skill.parent.relative_to(canonical).as_posix()
        body = skill.read_text(encoding="utf-8")
        for subdir in ("assets", "references"):
            for path in _skill_resource_paths(skill.parent, subdir):
                relative = path.relative_to(skill.parent).as_posix()
                if relative not in body:
                    violations.append(
                        f"{skill_id}: {relative} is not linked from SKILL.md"
                    )
        violations.extend(
            f"{skill_id}: SKILL.md links missing resource '{relative}'"
            for relative in re.findall(r"\]\(((?:assets|references)/[^)\s]+)\)", body)
            if not (skill.parent / relative).is_file()
        )
    return violations


def _check_reference_depth() -> list[str]:
    """Detect ``references/`` resources nested more than one level deep.

    Returns:
        list[str]: Human-readable violation messages; empty when shallow.
    """
    canonical = _REPO_ROOT / _SKILL_TREES[-1]
    violations: list[str] = []
    for skill in sorted(canonical.rglob(_SKILL_FILE)):
        skill_id = skill.parent.relative_to(canonical).as_posix()
        for path in _skill_resource_paths(skill.parent, "references"):
            relative = path.relative_to(skill.parent / "references")
            if len(relative.parts) > 2:
                violations.append(
                    f"{skill_id}: references/{relative.as_posix()} nested "
                    "more than one level deep"
                )
    return violations


def _check_policy_file_length() -> list[str]:
    """Detect always-loaded policy files exceeding their line budget.

    Returns:
        list[str]: Human-readable violation messages; empty when within budget.
    """
    violations: list[str] = []
    for relative, budget in _POLICY_FILE_LINE_BUDGETS.items():
        path = _REPO_ROOT / relative
        if not path.is_file():
            continue
        line_count = path.read_text(encoding="utf-8").count("\n") + 1
        if line_count > budget:
            violations.append(
                f"{relative}: {line_count} lines exceeds the {budget}-line "
                "context budget (see _POLICY_FILE_LINE_BUDGETS)"
            )
    return violations


def _check_memory_log_length() -> list[str]:
    """Detect a memory log exceeding its consolidation-trigger line budget.

    Unlike the frozen policy-file budgets above, this is a rotation trigger:
    remediation is to consolidate (merge near-duplicate entries, move
    resolved incident narratives to ``memories/archive/<file>.md`` verbatim),
    never to raise the budget.

    Returns:
        list[str]: Human-readable violation messages; empty when within budget.
    """
    violations: list[str] = []
    for relative in _MEMORY_LOG_FILES:
        path = _REPO_ROOT / relative
        if not path.is_file():
            continue
        line_count = path.read_text(encoding="utf-8").count("\n") + 1
        if line_count > _MEMORY_LOG_LINE_BUDGET:
            violations.append(
                f"{relative}: {line_count} lines exceeds the "
                f"{_MEMORY_LOG_LINE_BUDGET}-line budget \u2014 consolidate "
                "(merge near-duplicate entries, move resolved narratives to "
                "memories/archive/) instead of raising the budget"
            )
    return violations


def _check_llms_txt_index() -> list[str]:
    """Detect a missing/oversized root ``llms.txt`` or a broken link inside it.

    ``llms.txt`` (llms.txt standard) is the machine-readable entry index a
    fresh agent reads first; it must exist, stay terse, and every relative
    markdown link inside it must resolve to a real repository path.

    Returns:
        list[str]: Human-readable violation messages; empty when clean.
    """
    path = _REPO_ROOT / "llms.txt"
    if not path.is_file():
        return ["llms.txt: missing root machine-readable entry index"]
    body = path.read_text(encoding="utf-8")
    violations: list[str] = []
    line_count = body.count("\n") + 1
    if line_count > _LLMS_TXT_LINE_BUDGET:
        violations.append(
            f"llms.txt: {line_count} lines exceeds the {_LLMS_TXT_LINE_BUDGET}-line "
            "terse-index budget (see _LLMS_TXT_LINE_BUDGET)"
        )
    for raw_target in re.findall(r"\]\(([^)\s]+)\)", body):
        target = raw_target.split("#", 1)[0]
        if not target or target.startswith(("http://", "https://")):
            continue
        if not (_REPO_ROOT / target).exists():
            violations.append(f"llms.txt: link target '{target}' does not exist")
    return violations


def _check_scoped_instruction_length() -> list[str]:
    """Detect scoped instructions/rules exceeding the context budget.

    Returns:
        list[str]: Human-readable violation messages; empty when within budget.
    """
    violations: list[str] = []
    for glob in _SCOPED_INSTRUCTION_GLOBS:
        for path in sorted(_REPO_ROOT.glob(glob)):
            relative = path.relative_to(_REPO_ROOT).as_posix()
            line_count = path.read_text(encoding="utf-8").count("\n") + 1
            if line_count > _SCOPED_INSTRUCTION_LINE_BUDGET:
                violations.append(
                    f"{relative}: {line_count} lines exceeds the "
                    f"{_SCOPED_INSTRUCTION_LINE_BUDGET}-line context budget "
                    "(move worked examples to the matching skill)"
                )
    return violations


def _check_agent_line_budgets() -> list[str]:
    """Detect agent profile files exceeding the context budget.

    Returns:
        list[str]: Human-readable violation messages; empty when within budget.
    """
    violations: list[str] = []
    for directory_name in _AGENT_DIRS:
        suffix = (
            _GITHUB_AGENT_SUFFIX if directory_name.startswith(_GITHUB_ROOT) else ".md"
        )
        for path in sorted((_REPO_ROOT / directory_name).rglob(f"*{suffix}")):
            relative = path.relative_to(_REPO_ROOT).as_posix()
            line_count = path.read_text(encoding="utf-8").count("\n") + 1
            if line_count > _AGENT_LINE_BUDGET:
                violations.append(
                    f"{relative}: {line_count} lines exceeds the "
                    f"{_AGENT_LINE_BUDGET}-line context budget "
                    "(move worked examples to the matching skill)"
                )
    return violations


def _check_skill_length() -> list[str]:
    """Detect ``SKILL.md`` bodies exceeding the 500-line authoring limit.

    Skills whose frontmatter declares a ``generatedBy`` field are vendored
    from an external generator (e.g. the OpenSpec CLI's ``opsx`` skills);
    hand-trimming vendored content causes drift from the upstream generator,
    so those skills are exempt from this authoring limit.

    Returns:
        list[str]: Human-readable violation messages; empty when within limit.
    """
    canonical = _REPO_ROOT / _SKILL_TREES[-1]
    violations: list[str] = []
    for skill in sorted(canonical.rglob(_SKILL_FILE)):
        skill_id = skill.parent.relative_to(canonical).as_posix()
        if any(line.strip().startswith("generatedBy:") for line in _frontmatter(skill)):
            continue
        line_count = skill.read_text(encoding="utf-8").count("\n") + 1
        if line_count > 500:
            violations.append(f"{skill_id}: SKILL.md is {line_count} lines (limit 500)")
    return violations


def _check_family_skill_layout() -> list[str]:
    """Detect family-root skills and retired flat family identifiers.

    Returns:
        list[str]: Human-readable violation messages; empty when canonical.
    """
    canonical = _REPO_ROOT / _SKILL_TREES[-1]
    skill_ids = _skill_ids(canonical)
    violations = [
        f"{family}: family root must not contain SKILL.md; use a concise leaf skill"
        for family in sorted(_EXPECTED_NESTED_SKILL_ROOTS)
        if family in skill_ids
    ]
    violations.extend(
        f"{retired}: retired flat skill; use '{replacement}'"
        for retired, replacement in sorted(_RETIRED_FLAT_SKILL_IDS.items())
        if retired in skill_ids
    )
    return violations


def _check_vscode_deprecated_local_harness_locations() -> list[str]:
    """Detect deprecated Local-harness customization location settings.

    Returns:
        list[str]: Human-readable violation messages; empty when absent.
    """
    path = _REPO_ROOT / _VSCODE_SETTINGS_FILE
    if not path.is_file():
        return [f"{_VSCODE_SETTINGS_FILE}: missing VS Code settings file"]
    text = path.read_text(encoding="utf-8")
    deprecated_settings = (
        "chat.agentSkillsLocations",
        "chat.promptFilesLocations",
    )
    return [
        (
            f"{_VSCODE_SETTINGS_FILE}: remove deprecated Local-harness setting "
            f"'{setting}' and rely on native customization discovery"
        )
        for setting in deprecated_settings
        if re.search(rf'"{re.escape(setting)}"\s*:', text) is not None
    ]


def _check_vscode_hook_sources() -> list[str]:
    """Detect duplicate cross-runtime hook discovery in VS Code.

    VS Code loads both ``.github/hooks`` and ``.claude/settings.json`` by
    default. This repository mirrors equivalent hooks across those locations,
    so the Claude source must be disabled in VS Code to avoid running every
    policy hook twice; Claude Code still reads it natively.

    Returns:
        list[str]: Human-readable violation messages; empty when configured.
    """
    path = _REPO_ROOT / _VSCODE_SETTINGS_FILE
    if not path.is_file():
        return [f"{_VSCODE_SETTINGS_FILE}: missing VS Code settings file"]
    text = path.read_text(encoding="utf-8")
    expected = {
        _GITHUB_HOOKS_DIR: "true",
        _CLAUDE_SETTINGS_FILE: "false",
    }
    return [
        f"{_VSCODE_SETTINGS_FILE}: hook source '{source}' must be {value} "
        "to prevent duplicate mirrored hook execution"
        for source, value in expected.items()
        if re.search(rf'"{re.escape(source)}"\s*:\s*{value}\b', text) is None
    ]


def _prompt_ids() -> set[str]:
    """Collect repository prompt identifiers.

    Returns:
        set[str]: Prompt paths relative to ``.github/prompts`` without suffixes.
    """
    root = _REPO_ROOT / _GITHUB_PROMPTS_DIR
    return {
        path.relative_to(root).as_posix().removesuffix(".prompt.md")
        for path in root.rglob("*.prompt.md")
    }


def _command_ids() -> set[str]:
    """Collect Claude command identifiers.

    Returns:
        set[str]: Command paths relative to ``.claude/commands`` without suffixes.
    """
    root = _REPO_ROOT / _CLAUDE_COMMANDS_DIR
    return {
        path.relative_to(root).as_posix().removesuffix(".md")
        for path in root.rglob("*.md")
    }


def _command_backed_skill_ids() -> set[str]:
    """Collect nested skills that require direct Claude command entry points.

    Returns:
        set[str]: Nested skill identifiers under command-backed roots.
    """
    canonical = _REPO_ROOT / _SKILL_TREES[-1]
    return {
        skill_id
        for skill_id in _skill_ids(canonical)
        if skill_id.partition("/")[0] in _COMMAND_BACKED_SKILL_ROOTS
    }


def _check_prompt_family_roots() -> list[str]:
    """Detect prompt family subdirectories outside the expected set.

    ``.github/prompts`` holds top-level ``*.prompt.md`` files plus one
    subdirectory per directly-invoked skill family. Only the families in
    ``_EXPECTED_FAMILY_PROMPT_ROOTS`` are mirrored by Claude commands; a stray or
    vestigial family root (an empty ``frontend/``/``ponytail/`` folder left
    behind by a refactor, or a misplaced new family) is silent drift the other
    parity checks do not catch.

    Returns:
        list[str]: Human-readable violation messages; empty when canonical.
    """
    prompts_root = _REPO_ROOT / _GITHUB_PROMPTS_DIR
    if not prompts_root.is_dir():
        return []
    expected = set(_EXPECTED_FAMILY_PROMPT_ROOTS)
    return [
        f".github/prompts/{child.name}: unexpected prompt family root "
        f"(expected only {sorted(expected)})"
        for child in sorted(prompts_root.iterdir())
        if child.is_dir() and child.name not in expected
    ]


def _check_prompt_command_parity() -> list[str]:
    """Detect missing cross-runtime prompt commands and orphaned commands.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    prompts = _prompt_ids()
    commands = _command_ids()
    command_backed_skills = _command_backed_skill_ids()
    violations = [
        f".claude/commands: missing command for prompt '{prompt}'"
        for prompt in sorted(prompts - commands)
    ]
    violations.extend(
        f".github/prompts: missing prompt for command '{command}'"
        for command in sorted(commands - prompts - command_backed_skills)
    )
    return violations


def _check_nested_skill_commands() -> list[str]:
    """Detect command-backed nested skills without Claude command fallbacks.

    Returns:
        list[str]: Human-readable violation messages; empty when reachable.
    """
    commands = _command_ids()
    return [
        f".claude/commands: nested skill '{skill_id}' needs a command fallback"
        for skill_id in sorted(_command_backed_skill_ids() - commands)
    ]


def _check_family_facade_targets() -> list[str]:
    """Detect thin family façades that reference the wrong canonical skill.

    Returns:
        list[str]: Human-readable violation messages; empty when targets align.
    """
    violations: list[str] = []
    for skill_id in sorted(_command_backed_skill_ids()):
        family, _, leaf = skill_id.partition("/")
        if family not in _THIN_FACADE_SKILL_ROOTS or not leaf:
            continue
        prompt_path = _REPO_ROOT / _GITHUB_PROMPTS_DIR / family / f"{leaf}.prompt.md"
        expected_prompt_name = f"{family}-{leaf}"
        if (
            prompt_path.is_file()
            and _frontmatter_values(prompt_path).get("name") != expected_prompt_name
        ):
            violations.append(
                f"{skill_id}: Copilot façade name must be '{expected_prompt_name}'"
            )
        targets = (
            (
                "Copilot",
                prompt_path,
                f".github/skills/{skill_id}/SKILL.md",
            ),
            (
                "Claude",
                _REPO_ROOT / _CLAUDE_COMMANDS_DIR / family / f"{leaf}.md",
                f".claude/skills/{skill_id}/SKILL.md",
            ),
        )
        for runtime, path, expected_target in targets:
            if path.is_file() and expected_target not in path.read_text(
                encoding="utf-8"
            ):
                violations.append(
                    f"{skill_id}: {runtime} façade must reference '{expected_target}'"
                )
    return violations


def _agent_paths(directory: Path) -> dict[str, Path]:
    """Map each agent identifier to its file within one runtime directory.

    Both VS Code and Claude Code discover agent definitions in subfolders
    (recursive scan) and resolve each by its kebab-case identifier — the file's
    basename without its suffix — not by its Title-Case ``name`` display value,
    so workers live in the ``subagents/`` subfolder while primary modes stay
    flat. ``_check_agent_parity`` requires each ``name`` to normalize to that
    identifier.

    Args:
        directory (Path): Runtime agent directory.

    Returns:
        dict[str, Path]: Agent identifier -> discovered file path.
    """
    suffix = (
        _GITHUB_AGENT_SUFFIX
        if directory.name == "agents" and directory.parent.name == ".github"
        else ".md"
    )
    return {
        path.name.removesuffix(suffix): path
        for path in sorted(directory.rglob(f"*{suffix}"))
        if path.is_file()
    }


def _agent_ids(directory: Path) -> set[str]:
    """Collect normalized agent identifiers in one runtime directory.

    Args:
        directory (Path): Runtime agent directory.

    Returns:
        set[str]: Agent identifiers derived from file basenames.
    """
    return set(_agent_paths(directory))


def _check_agent_parity() -> list[str]:
    """Detect agent roster, name, and behavior divergence across runtimes.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    per_runtime = {name: _agent_paths(_REPO_ROOT / name) for name in _AGENT_DIRS}
    union = set().union(*(set(paths) for paths in per_runtime.values()))
    violations: list[str] = []
    for directory_name, agent_paths in per_runtime.items():
        violations.extend(
            f"{directory_name}: missing agent '{agent_id}'"
            for agent_id in sorted(union - set(agent_paths))
        )
        for agent_id in sorted(agent_paths):
            path = agent_paths[agent_id]
            name = _frontmatter_values(path).get("name", "")
            normalized_name = name.lower().replace(" ", "-")
            if normalized_name != agent_id:
                violations.append(
                    f"{path.relative_to(_REPO_ROOT).as_posix()}: agent name "
                    f"'{name}' must match identifier '{agent_id}'"
                )
    github_paths = per_runtime[_AGENT_DIRS[0]]
    claude_paths = per_runtime[_AGENT_DIRS[1]]
    for agent_id in sorted(set(github_paths) & set(claude_paths)):
        github_body = _markdown_body(github_paths[agent_id])
        claude_body = _markdown_body(claude_paths[agent_id])
        if github_body != claude_body:
            violations.append(f"{agent_id}: agent body differs across runtimes")
    return violations


def _markdown_body(path: Path) -> str:
    """Read Markdown content after normalized YAML frontmatter.

    Args:
        path (Path): Markdown file path.

    Returns:
        str: LF-normalized body without frontmatter.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return "\n".join(lines)
    try:
        end = lines.index("---", 1)
    except ValueError:
        return "\n".join(lines)
    return "\n".join(lines[end + 1 :]).strip()


def _frontmatter_list(path: Path, field: str) -> list[str] | None:
    """Read an inline YAML list or comma-delimited scalar from frontmatter.

    Args:
        path (Path): Agent file to inspect.
        field (str): Frontmatter field name.

    Returns:
        list[str] | None: Parsed values, or ``None`` when absent or malformed.
    """
    raw_value = _frontmatter_values(path).get(field)
    if raw_value is None:
        return None
    if raw_value.startswith("["):
        try:
            parsed: object = ast.literal_eval(raw_value)
        except (SyntaxError, ValueError):
            return None
        return _string_list(parsed)
    return [value.strip() for value in raw_value.split(",") if value.strip()]


def _agent_has_tool(path: Path, tool: str) -> bool:
    """Check whether an agent exposes a tool by its runtime-specific name.

    Args:
        path (Path): Agent file to inspect.
        tool (str): Case-insensitive tool name.

    Returns:
        bool: Whether the exact tool is configured.
    """
    tools = _frontmatter_list(path, "tools") or []
    return tool.casefold() in {value.casefold() for value in tools}


def _agent_has_any_tool(path: Path, tools: set[str]) -> bool:
    """Check whether an agent exposes any tool in a runtime-neutral set.

    Args:
        path (Path): Agent file to inspect.
        tools (set[str]): Case-insensitive tool names.

    Returns:
        bool: Whether any configured tool matches.
    """
    configured = _frontmatter_list(path, "tools") or []
    normalized = {value.casefold() for value in configured}
    return bool(normalized.intersection(tool.casefold() for tool in tools))


def _worker_invocation_violations(path: Path, *, agent_id: str) -> list[str]:
    """Validate one hidden, non-recursive, small-model worker.

    Args:
        path (Path): Worker agent definition.
        agent_id (str): Canonical worker identifier.

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    relative = path.relative_to(_REPO_ROOT).as_posix()
    values = _frontmatter_values(path)
    violations: list[str] = []
    if values.get("user-invocable") != "false":
        violations.append(f"{relative}: worker must set user-invocable: false")
    if values.get("disable-model-invocation") != "false":
        violations.append(
            f"{relative}: worker must set disable-model-invocation: false"
        )
    if _frontmatter_list(path, "agents") != []:
        violations.append(f"{relative}: worker must set agents: []")
    model = values.get("model", "").casefold()
    if not any(marker in model for marker in _SMALL_MODEL_MARKERS):
        violations.append(f"{relative}: worker must prefer a small model")
    if _agent_has_tool(path, "agent"):
        violations.append(f"{relative}: worker must not include the agent tool")
    can_edit = _agent_has_any_tool(path, {"edit", "write"})
    can_execute = _agent_has_any_tool(path, {"execute", "bash", "powershell"})
    if agent_id in _EDITING_WORKER_AGENT_IDS:
        if not can_edit or not can_execute:
            violations.append(
                f"{relative}: bounded implementer must include edit and execute tools"
            )
    elif can_edit or can_execute:
        violations.append(
            f"{relative}: read-only worker must not include edit/execute tools"
        )
    return violations


def _primary_invocation_violations(
    path: Path,
    *,
    worker_ids: set[str],
) -> list[str]:
    """Validate one top-level coordinator's visibility and worker allowlist.

    VS Code and Claude Code match ``agents`` allowlist entries and
    ``runSubagent`` requests against each worker's kebab-case identifier (its
    file basename), not its Title-Case ``name`` display value, so allowlists
    are validated against the worker identifiers.

    Args:
        path (Path): Top-level agent definition.
        worker_ids (set[str]): Valid worker identifiers (kebab-case file stems).

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    relative = path.relative_to(_REPO_ROOT).as_posix()
    values = _frontmatter_values(path)
    is_github = relative.startswith(".github/")
    expected_visibility = "true" if is_github else "false"
    violations: list[str] = []
    if values.get("user-invocable") != expected_visibility:
        violations.append(
            f"{relative}: primary must set user-invocable: {expected_visibility}"
        )
    if values.get("disable-model-invocation") != "true":
        violations.append(
            f"{relative}: primary must set disable-model-invocation: true"
        )
    allowed_agents = _frontmatter_list(path, "agents")
    if not allowed_agents or "*" in allowed_agents:
        violations.append(
            f"{relative}: primary must explicitly allow every worker it may use; "
            "wildcards are forbidden"
        )
    else:
        unknown = set(allowed_agents) - worker_ids
        violations.extend(
            f"{relative}: unknown or top-level subagent '{name}' in agents allowlist"
            for name in sorted(unknown)
        )
        if path.stem.removesuffix(".agent") == "orchestrator":
            missing = worker_ids - set(allowed_agents)
            violations.extend(
                f"{relative}: orchestrator must allow worker '{name}'"
                for name in sorted(missing)
            )
    if not _agent_has_tool(path, "agent"):
        violations.append(f"{relative}: primary must include the agent tool")
    return violations


def _check_agent_invocation_policy() -> list[str]:
    """Enforce the top-level coordinator and hidden-worker tier contract.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    violations: list[str] = []
    for directory_name in _AGENT_DIRS:
        directory = _REPO_ROOT / directory_name
        paths = _agent_paths(directory)
        workers = {
            agent_id: path
            for agent_id, path in paths.items()
            if agent_id in _WORKER_AGENT_IDS
        }
        worker_subfolder = directory / _WORKER_SUBFOLDER
        for agent_id, path in paths.items():
            if agent_id in _WORKER_AGENT_IDS:
                if path.parent != worker_subfolder:
                    violations.append(
                        f"{path.relative_to(_REPO_ROOT).as_posix()}: worker must "
                        f"live in the {_WORKER_SUBFOLDER}/ subfolder"
                    )
            elif path.parent != directory:
                violations.append(
                    f"{path.relative_to(_REPO_ROOT).as_posix()}: primary agent must "
                    f"stay flat (only workers live in the {_WORKER_SUBFOLDER}/ "
                    "subfolder)"
                )
        worker_ids = set(workers)
        for agent_id, path in workers.items():
            violations.extend(_worker_invocation_violations(path, agent_id=agent_id))
        for agent_id, path in paths.items():
            if agent_id not in workers:
                violations.extend(
                    _primary_invocation_violations(
                        path,
                        worker_ids=worker_ids,
                    )
                )
    return violations


def _string_list(value: object) -> list[str] | None:
    """Validate and normalize a JSON list of strings.

    Args:
        value (object): Potential JSON list value.

    Returns:
        list[str] | None: String values, or ``None`` when invalid.
    """
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return [item for item in value if isinstance(item, str)]


def _as_object_dict(value: object) -> dict[str, object] | None:
    """Narrow a JSON value to a string-keyed object mapping.

    Rebuilding the mapping (rather than relying on ``isinstance(value, dict)``
    alone) works around a type-checker narrowing gap where a bare ``dict``
    isinstance check on an ``object``-typed value infers ``dict[Never, Never]``
    instead of ``dict[Unknown, Unknown]``.

    Args:
        value (object): Potential JSON object value.

    Returns:
        dict[str, object] | None: Rebuilt mapping, or ``None`` when not an object.
    """
    if not isinstance(value, dict):
        return None
    return {str(key): entry for key, entry in value.items()}


def _profile_cycle(
    name: str, profiles: dict[str, object], *, path: tuple[str, ...] = ()
) -> bool:
    """Detect cycles in profile inheritance.

    Args:
        name (str): Profile identifier to inspect.
        profiles (dict[str, object]): Raw profile declarations.
        path (tuple[str, ...]): Current inheritance path.

    Returns:
        bool: Whether the profile participates in an inheritance cycle.
    """
    if name in path:
        return True
    profile = _as_object_dict(profiles.get(name))
    if profile is None:
        return False
    parents = _string_list(profile.get("extends"))
    if parents is None:
        return False
    next_path = (*path, name)
    return any(_profile_cycle(parent, profiles, path=next_path) for parent in parents)


def _catalog_entries(relative_path: str, key: str) -> dict[str, object]:
    """Read named entries from one agentic-setup catalog.

    Args:
        relative_path (str): Repository-relative catalog path.
        key (str): Top-level object containing named entries.

    Returns:
        dict[str, object]: Catalog entries, or an empty mapping when malformed.
    """
    path = _REPO_ROOT / relative_path
    if not path.is_file():
        return {}
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get(key), dict):
        return {}
    return {str(name): value for name, value in raw[key].items()}


def _check_asset_entry(name: str, entry: object) -> list[str]:
    """Validate one asset catalog entry and its on-disk target.

    Args:
        name (str): Asset identifier.
        entry (object): Raw asset declaration.

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    object_entry = _as_object_dict(entry)
    if object_entry is None:
        return [f"{_SETUP_ASSETS_FILE}: asset '{name}' must be an object"]
    violations: list[str] = []
    relative_path = object_entry.get("path")
    description = object_entry.get("description")
    if not isinstance(relative_path, str) or not relative_path:
        violations.append(f"{_SETUP_ASSETS_FILE}: asset '{name}' needs a path")
    elif not (_REPO_ROOT / _SETUP_DIR / relative_path).exists():
        violations.append(
            f"{_SETUP_ASSETS_FILE}: asset '{name}' path "
            f"'{relative_path}' does not exist"
        )
    if not isinstance(description, str) or not description:
        violations.append(f"{_SETUP_ASSETS_FILE}: asset '{name}' needs a description")
    return violations


def _check_setup_catalogs() -> list[str]:
    """Detect malformed setup catalogs and missing asset targets.

    The asset catalog is optional so a single-shape repository may omit it; it
    is validated only when its file is present.

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    violations: list[str] = []
    if (_REPO_ROOT / _SETUP_ASSETS_FILE).is_file():
        assets = _catalog_entries(_SETUP_ASSETS_FILE, "assets")
        if not assets:
            violations.append(f"{_SETUP_ASSETS_FILE}: missing non-empty assets object")
        for name, entry in assets.items():
            violations.extend(_check_asset_entry(name, entry))
    return violations


def _check_setup_markdown_links() -> list[str]:
    """Detect broken relative Markdown links in agentic setup assets.

    Returns:
        list[str]: Human-readable violation messages; empty when links resolve.
    """
    setup_root = _REPO_ROOT / _SETUP_DIR
    violations: list[str] = []
    for path in sorted(setup_root.rglob("*.md")):
        body = path.read_text(encoding="utf-8")
        for raw_target in re.findall(r"\]\(([^)\s]+)\)", body):
            target = raw_target.split("#", 1)[0]
            if not target or target.startswith(("http://", "https://")):
                continue
            if not (path.parent / target).resolve().exists():
                relative = path.relative_to(_REPO_ROOT).as_posix()
                violations.append(
                    f"{relative}: link target '{raw_target}' does not exist"
                )
    return violations


def _load_json_object(path: Path) -> dict[str, object] | None:
    """Parse a JSON object file, tolerating an absent or comment-disabled config.

    Args:
        path (Path): JSON object file, possibly commented out to disable it.

    Returns:
        dict[str, object] | None: Parsed object keyed by name, or ``None`` when the
            file is absent, is not valid JSON (for example fully commented out),
            or does not hold a JSON object.
    """
    if not path.is_file():
        return None
    try:
        raw: object = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(raw, dict):
        return None
    return {str(key): value for key, value in raw.items()}


def _profile_inventory() -> dict[str, set[str]]:
    """Collect canonical capability identifiers by profile field.

    Returns:
        dict[str, set[str]]: Available skills, agents, instructions, and MCP names.
    """
    mcp_names: set[str] = set()
    for rel, key in _MCP_FILES.items():
        raw = _load_json_object(_REPO_ROOT / rel)
        servers = raw.get(key) if raw is not None else None
        if isinstance(servers, dict):
            mcp_names.update(str(name) for name in servers)
    return {
        "skills": _skill_ids(_REPO_ROOT / _SKILL_TREES[-1]),
        "agents": _agent_ids(_REPO_ROOT / _AGENT_DIRS[-1]),
        "instructions": set(_INSTRUCTION_RULE_PAIRS),
        "mcpServers": mcp_names,
        "assets": set(_catalog_entries(_SETUP_ASSETS_FILE, "assets")),
    }


def _validate_profile(
    name: str,
    profile: object,
    profiles: dict[str, object],
    available: dict[str, set[str]],
    declared: dict[str, set[str]],
) -> list[str]:
    """Validate one setup profile and accumulate declared capabilities.

    Args:
        name (str): Profile identifier.
        profile (object): Raw profile declaration.
        profiles (dict[str, object]): All raw profile declarations.
        available (dict[str, set[str]]): Canonical capabilities by field.
        declared (dict[str, set[str]]): Mutable declared capabilities by field.

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    object_profile = _as_object_dict(profile)
    if object_profile is None:
        return [f"profile '{name}': declaration must be an object"]
    violations: list[str] = []
    parents = _string_list(object_profile.get("extends"))
    if parents is None:
        violations.append(f"profile '{name}': extends must be a string list")
    else:
        violations.extend(
            f"profile '{name}': unknown parent '{parent}'"
            for parent in parents
            if parent not in profiles
        )
    if _profile_cycle(name, profiles):
        violations.append(f"profile '{name}': inheritance cycle")
    for field in _PROFILE_CAPABILITIES:
        violations.extend(
            _validate_profile_capabilities(
                name,
                field,
                object_profile.get(field),
                available[field],
                declared[field],
            )
        )
    return violations


def _validate_profile_capabilities(
    profile_name: str,
    field: str,
    raw_values: object,
    available: set[str],
    declared: set[str],
) -> list[str]:
    """Validate one capability field in a setup profile.

    Args:
        profile_name (str): Profile identifier.
        field (str): Capability field name.
        raw_values (object): Raw field value.
        available (set[str]): Canonical capability identifiers.
        declared (set[str]): Mutable declared capability identifiers.

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    values = _string_list(raw_values)
    if values is None:
        return [f"profile '{profile_name}': {field} must be a string list"]
    declared.update(values)
    return [
        f"profile '{profile_name}': unknown {field} capability '{value}'"
        for value in values
        if value not in available
    ]


def _profile_coverage_violations(
    available: dict[str, set[str]], declared: dict[str, set[str]]
) -> list[str]:
    """Detect canonical capabilities absent from every setup profile.

    Args:
        available (dict[str, set[str]]): Canonical capabilities by field.
        declared (dict[str, set[str]]): Profile-declared capabilities by field.

    Returns:
        list[str]: Human-readable violation messages; empty when complete.
    """
    return [
        f"{_SETUP_PROFILES_FILE}: uncategorized {field} capability '{value}'"
        for field in _PROFILE_CAPABILITIES
        for value in sorted(available[field] - declared[field])
    ]


def _check_setup_profiles() -> list[str]:
    """Detect stale or incomplete machine-readable setup profiles.

    Returns:
        list[str]: Human-readable violation messages; empty when valid.
    """
    path = _REPO_ROOT / _SETUP_PROFILES_FILE
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("profiles"), dict):
        return [f"{_SETUP_PROFILES_FILE}: missing profiles object"]
    profiles = raw["profiles"]
    available = _profile_inventory()
    declared = {field: set() for field in _PROFILE_CAPABILITIES}
    violations: list[str] = []
    for name, profile in profiles.items():
        if not isinstance(name, str):
            violations.append(f"{_SETUP_PROFILES_FILE}: invalid profile declaration")
            continue
        violations.extend(
            _validate_profile(name, profile, profiles, available, declared)
        )
    violations.extend(_profile_coverage_violations(available, declared))
    return violations


def _skill_files(skill_directory: Path) -> dict[str, bytes]:
    """Collect every file bundled with one skill.

    Args:
        skill_directory (Path): Directory containing ``SKILL.md`` and resources.

    Returns:
        dict[str, bytes]: Relative file paths mapped to content.
    """
    if not skill_directory.is_dir():
        return {}
    return {
        path.relative_to(skill_directory).as_posix(): path.read_bytes()
        for path in skill_directory.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def _skill_tree_content_violations(
    skill_id: str,
    expected: dict[str, bytes],
    tree: str,
) -> list[str]:
    """Compare one skill mirror with the canonical bundle.

    Args:
        skill_id (str): Canonical skill identifier.
        expected (dict[str, bytes]): Canonical relative files and content.
        tree (str): Mirrored skill-root path.

    Returns:
        list[str]: Missing, extra, or divergent resource violations.
    """
    actual = _skill_files(_REPO_ROOT / tree / skill_id)
    tree_label = Path(tree).parts[0]
    violations = [
        f"{skill_id}: {tree_label} missing skill file '{path}'"
        for path in sorted(expected.keys() - actual.keys())
    ]
    violations.extend(
        f"{skill_id}: {tree_label} has extra skill file '{path}'"
        for path in sorted(actual.keys() - expected.keys())
    )
    violations.extend(
        f"{skill_id}: skill file '{path}' differs in {tree_label}"
        for path in sorted(expected.keys() & actual.keys())
        if expected[path] != actual[path]
    )
    return violations


def _check_content_parity() -> list[str]:
    """Detect mirrored skills whose complete contents differ across trees.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    canonical = _REPO_ROOT / _SKILL_TREES[-1]
    if not canonical.is_dir():
        return []
    violations: list[str] = []
    for skill in canonical.rglob(_SKILL_FILE):
        sid = skill.parent.relative_to(canonical).as_posix()
        expected = _skill_files(skill.parent)
        for tree in _SKILL_TREES[:-1]:
            violations.extend(_skill_tree_content_violations(sid, expected, tree))
    return violations


def _script_ids(value: object) -> set[str]:
    """Extract logical hook script identifiers from a command value.

    Args:
        value (object): Potential hook command value.

    Returns:
        set[str]: Script stems referenced by the command.
    """
    if isinstance(value, str):
        return {match.group(1) for match in _HOOK_SCRIPT_PATTERN.finditer(value)}
    if isinstance(value, list):
        script_ids: set[str] = set()
        for item in value:
            script_ids.update(_script_ids(item))
        return script_ids
    return set()


def _github_manifest_targets(path: Path) -> dict[str, set[str]]:
    """Collect event targets from one hook manifest.

    Args:
        path (Path): Hook manifest path.

    Returns:
        dict[str, set[str]]: Logical script identifiers by event.
    """
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("hooks"), dict):
        return {}
    targets: dict[str, set[str]] = {}
    for event, entries in raw["hooks"].items():
        if not isinstance(event, str) or not isinstance(entries, list):
            continue
        event_targets = targets.setdefault(event, set())
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            for key in (
                "args",
                "bash",
                "command",
                "exec",
                "linux",
                "osx",
                "powershell",
                "windows",
            ):
                event_targets.update(_script_ids(entry.get(key)))
    return targets


def _github_hook_targets() -> dict[str, set[str]]:
    """Collect event-to-script wiring from GitHub hook manifests.

    Returns:
        dict[str, set[str]]: Logical script identifiers by event.
    """
    targets: dict[str, set[str]] = {}
    for path in (_REPO_ROOT / _GITHUB_HOOKS_DIR).glob("*.json"):
        for event, scripts in _github_manifest_targets(path).items():
            targets.setdefault(event, set()).update(scripts)
    return targets


def _claude_group_details(group: object) -> tuple[set[str], set[str]]:
    """Collect script targets and matchers from one hook group.

    Args:
        group (object): Potential hook matcher group.

    Returns:
        tuple[set[str], set[str]]: Script identifiers and matcher values.
    """
    object_group = _as_object_dict(group)
    if object_group is None:
        return set(), set()
    handlers = object_group.get("hooks")
    if not isinstance(handlers, list):
        return set(), set()
    targets: set[str] = set()
    for handler in handlers:
        object_handler = _as_object_dict(handler)
        if object_handler is None:
            continue
        targets.update(_script_ids(object_handler.get("command")))
        targets.update(_script_ids(object_handler.get("args")))
    matcher = object_group.get("matcher")
    if "tool-guardian" not in targets or not isinstance(matcher, str):
        return targets, set()
    return targets, set(matcher.split("|"))


def _claude_hook_targets() -> tuple[dict[str, set[str]], set[str]]:
    """Collect Claude hook wiring and tool-guardian matcher coverage.

    Returns:
        tuple[dict[str, set[str]], set[str]]: Script identifiers by event and
            shell tools matched by the tool guardian.
    """
    settings_path = _REPO_ROOT / _CLAUDE_SETTINGS_FILE
    raw: object = json.loads(settings_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}, set()
    hooks = raw.get("hooks")
    if not isinstance(hooks, dict):
        return {}, set()
    targets: dict[str, set[str]] = {}
    guardian_matchers: set[str] = set()
    for event, groups in hooks.items():
        if not isinstance(event, str) or not isinstance(groups, list):
            continue
        event_targets = targets.setdefault(event, set())
        for group in groups:
            group_targets, group_matchers = _claude_group_details(group)
            event_targets.update(group_targets)
            guardian_matchers.update(group_matchers)
    return targets, guardian_matchers


def _check_hook_parity() -> list[str]:
    """Detect hook engine, wiring, and matcher divergence.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    violations: list[str] = []
    if not (_REPO_ROOT / _TOOL_GUARD_FILE).is_file():
        violations.append(f"{_TOOL_GUARD_FILE}: shared hook policy engine is missing")

    for github_manifest in sorted((_REPO_ROOT / _GITHUB_HOOKS_DIR).glob("*.json")):
        raw: object = json.loads(github_manifest.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or raw.get("version") != 1:
            relative = github_manifest.relative_to(_REPO_ROOT).as_posix()
            violations.append(f"{relative}: version must be 1")

    github_targets = _github_hook_targets()
    claude_targets, guardian_matchers = _claude_hook_targets()
    if github_targets != claude_targets:
        violations.append(
            "hook wiring differs across runtimes "
            f"({github_targets} != {claude_targets})"
        )
    for script_id in sorted(set().union(*github_targets.values())):
        script_path = _REPO_ROOT / ".agents/guard" / f"{script_id}.ts"
        if not script_path.is_file():
            violations.append(f".agents/guard/{script_id}.ts: hook target is missing")
    covers_every_tool = "*" in guardian_matchers
    covers_both_shells = {"Bash", "PowerShell"}.issubset(guardian_matchers)
    if not covers_every_tool and not covers_both_shells:
        violations.append("Claude tool guardian must match every tool or both shells")
    return violations


def _check_mcp_parity() -> list[str]:
    """Detect MCP server sets diverging across the config files.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    present: dict[str, set[str]] = {}
    for rel, key in _MCP_FILES.items():
        raw = _load_json_object(_REPO_ROOT / rel)
        if raw is None:
            continue
        servers = raw.get(key, {})
        if not isinstance(servers, dict):
            continue
        present[rel] = {str(name) for name in servers}
    if len(present) < 2:
        return []
    union = set().union(*present.values())
    violations: list[str] = []
    for rel, names in present.items():
        violations.extend(
            f"{rel}: missing MCP server '{missing}'"
            for missing in sorted(union - names)
        )
    return violations


def _check_agent_roster_documented() -> list[str]:
    """Detect agents missing from or stale in the AGENTS.md profile table.

    The ``## Agent Profiles`` table in ``AGENTS.md`` is prose the guard cannot
    otherwise keep in step with the agent files, so a new agent can be added
    (and mirrored) yet never listed for humans. This enforces that the table's
    backticked first column matches the ``.github/agents`` roster.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    agents_file = _REPO_ROOT / "AGENTS.md"
    if not agents_file.is_file():
        return []
    documented: set[str] = set()
    in_section = False
    for line in agents_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = line.strip() == "## Agent Profiles"
            continue
        if in_section and (match := re.match(r"\|\s*`([a-z0-9-]+)`\s*\|", line)):
            documented.add(match.group(1))
    actual = _agent_ids(_REPO_ROOT / _AGENT_DIRS[0])
    violations = [
        f"AGENTS.md: Agent Profiles table missing agent '{name}'"
        for name in sorted(actual - documented)
    ]
    violations.extend(
        f"AGENTS.md: Agent Profiles table lists unknown agent '{name}'"
        for name in sorted(documented - actual)
    )
    return violations


def _check_claude_roster_documented() -> list[str]:
    """Detect agents missing from or stale in the CLAUDE.md profile table.

    CLAUDE.md's ``### Agent profiles`` table lists each agent by display name
    plus its ``.claude/agents/<id>.md`` path. Like the AGENTS.md roster check,
    this is prose the guard cannot otherwise keep in step with the agent files,
    so an agent can be added and mirrored yet never listed for Claude Code users
    (as ``fullstack`` was until 2026-09-14). This enforces that the table's
    ``.claude/agents/<id>.md`` paths match the ``.claude/agents`` roster.

    Returns:
        list[str]: Human-readable violation messages; empty when aligned.
    """
    claude_file = _REPO_ROOT / "CLAUDE.md"
    if not claude_file.is_file():
        return []
    documented: set[str] = set()
    in_section = False
    for line in claude_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = False
            continue
        if line.startswith("### "):
            in_section = line.strip() == "### Agent profiles"
            continue
        if in_section and (
            match := re.search(
                r"\.claude/agents/(?:[a-z0-9-]+/)*([a-z0-9-]+)\.md", line
            )
        ):
            documented.add(match.group(1))
    actual = _agent_ids(_REPO_ROOT / _AGENT_DIRS[1])
    violations = [
        f"CLAUDE.md: Agent profiles table missing agent '{name}'"
        for name in sorted(actual - documented)
    ]
    violations.extend(
        f"CLAUDE.md: Agent profiles table lists unknown agent '{name}'"
        for name in sorted(documented - actual)
    )
    return violations


def main() -> None:
    """Run the agent-config guard and exit non-zero on any violation."""
    violations = (
        _check_portability(_project_tokens())
        + _check_parity()
        + _check_content_parity()
        + _check_skill_metadata()
        + _check_template_syntax()
        + _check_skill_resource_references()
        + _check_reference_depth()
        + _check_skill_length()
        + _check_policy_file_length()
        + _check_memory_log_length()
        + _check_llms_txt_index()
        + _check_scoped_instruction_length()
        + _check_agent_line_budgets()
        + _check_family_skill_layout()
        + _check_vscode_deprecated_local_harness_locations()
        + _check_vscode_hook_sources()
        + _check_prompt_family_roots()
        + _check_prompt_command_parity()
        + _check_nested_skill_commands()
        + _check_family_facade_targets()
        + _check_agent_parity()
        + _check_agent_invocation_policy()
        + _check_agent_roster_documented()
        + _check_claude_roster_documented()
        + _check_setup_catalogs()
        + _check_setup_markdown_links()
        + _check_setup_profiles()
        + _check_instruction_rule_parity()
        + _check_instruction_rule_content_parity()
        + _check_agentic_config_scope_coverage()
        + _check_hook_parity()
        + _check_mcp_parity()
    )
    if violations:
        sys.stderr.write("Agent-config guard failed:\n")
        for violation in violations:
            sys.stderr.write(f"  - {violation}\n")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
