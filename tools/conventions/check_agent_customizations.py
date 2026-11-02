"""Validate repository agent customizations and their mirrored configuration."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import yaml

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
GITHUB_AGENTS_DIR: Final[Path] = Path(".github/agents")
GITHUB_AGENT_PATTERN: Final[str] = "*.agent.md"
SKILL_FILENAME: Final[str] = "SKILL.md"
SKILL_ROOTS: Final[tuple[Path, ...]] = (
    Path(".github/skills"),
    Path(".claude/skills"),
    Path(".agents/skills"),
)
CUSTOMIZATION_GROUPS: Final[tuple[tuple[Path, str, str], ...]] = (
    (GITHUB_AGENTS_DIR, GITHUB_AGENT_PATTERN, "copilot-agent"),
    (Path(".claude/agents"), "*.md", "claude-agent"),
    (Path(".github/instructions"), "*.instructions.md", "instruction"),
    (Path(".claude/rules"), "*.md", "rule"),
    (Path(".github/prompts"), "*.prompt.md", "prompt"),
)
MCP_MANIFESTS: Final[tuple[tuple[Path, str], ...]] = (
    (Path(".vscode/mcp.json"), "servers"),
    (Path(".mcp.json"), "mcpServers"),
    (Path(".claude/mcp.json"), "mcpServers"),
)
SKILL_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
AGENT_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"[a-z][a-z0-9-]*")
MCP_TOOL_PATTERN: Final[re.Pattern[str]] = re.compile(r"['\"]([a-z0-9-]+)/\*['\"]")
EXTENSION_TOOL_NAMESPACES: Final[frozenset[str]] = frozenset({"azure-mcp", "bicep", "foundry-mcp", "postgresql-mcp"})
PROHIBITED_GIT_COMMAND_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\bgit\s+(?:commit|diff|log|merge|status)\b",
    re.IGNORECASE,
)
STALE_GUIDANCE: Final[tuple[tuple[str, str], ...]] = (
    ("Python 3.12", "references the retired Python 3.12 runtime"),
    ("dict[str, Any]", "recommends Any-based dictionary typing"),
    ("utils -> config", "references the removed utils architecture layer"),
    ("faster-whisper", "references the retired speech provider"),
)
MOJIBAKE_MARKERS: Final[tuple[str, ...]] = ("â", "Â", "Ã", "Γ")
PROJECT_PORTABILITY_LINE_PREFIX: Final[str] = "- Agent portability tokens:"
PROFILE_CAPABILITIES: Final[tuple[str, ...]] = (
    "skills",
    "agents",
    "instructions",
    "mcpServers",
    "optionalMcpServers",
    "assets",
)


@dataclass(frozen=True, kw_only=True, slots=True)
class Violation:
    """Customization validation failure."""

    path: Path
    message: str

    def format(self, *, root: Path) -> str:
        """Format the violation relative to the repository root."""
        return f"{self.path.relative_to(root).as_posix()}: {self.message}"


def _read_frontmatter(path: Path) -> tuple[dict[str, object] | None, str | None]:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---\n"):
        return None, "missing YAML frontmatter"

    closing_marker = text.find("\n---", 4)
    if closing_marker < 0:
        return None, "unterminated YAML frontmatter"

    try:
        raw = yaml.safe_load(text[4:closing_marker])
    except yaml.YAMLError as error:
        return None, f"invalid YAML frontmatter: {error}"

    if not isinstance(raw, dict) or not all(isinstance(key, str) for key in raw):
        return None, "frontmatter must be a string-keyed mapping"
    return {key: value for key, value in raw.items() if isinstance(key, str)}, None


def _load_mcp_servers(path: Path, *, key: str) -> tuple[set[str], list[Violation]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return set(), [Violation(path=path, message=f"invalid MCP manifest: {error}")]

    if not isinstance(raw, dict) or not isinstance(raw.get(key), dict):
        return set(), [Violation(path=path, message=f"missing {key!r} server mapping")]
    servers = raw[key]
    violations: list[Violation] = []
    for server_name, server_config in servers.items():
        if not isinstance(server_name, str) or not isinstance(server_config, dict):
            continue
        url = server_config.get("url")
        if isinstance(url, str) and server_config.get("type") != "http":
            violations.append(Violation(path=path, message=f"HTTP MCP server {server_name!r} requires type 'http'"))
        is_vscode_manifest = path.parent.name == ".vscode" and path.name == "mcp.json"
        if server_config.get("cwd") == "${workspaceFolder}" and not is_vscode_manifest:
            violations.append(Violation(path=path, message="non-VS Code MCP manifest uses ${workspaceFolder}"))
    return {name for name in servers if isinstance(name, str)}, violations


def _load_json_object(path: Path) -> tuple[dict[str, object] | None, list[Violation]]:
    """Load a JSON object and report malformed content."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [Violation(path=path, message=f"invalid JSON: {error}")]
    if not isinstance(raw, dict):
        return None, [Violation(path=path, message="JSON root must be an object")]
    return {str(key): value for key, value in raw.items()}, []


def _skill_ids(*, root: Path) -> set[str]:
    """Collect canonical skill identifiers from the portable tree."""
    skill_root = root / ".agents/skills"
    return {path.parent.relative_to(skill_root).as_posix() for path in skill_root.rglob(SKILL_FILENAME)}


def _agent_ids(*, root: Path) -> set[str]:
    """Collect provider agent identifiers."""
    github_ids = {
        path.name.removesuffix(".agent.md") for path in (root / GITHUB_AGENTS_DIR).rglob(GITHUB_AGENT_PATTERN)
    }
    claude_ids = {path.stem for path in (root / ".claude/agents").rglob("*.md")}
    return github_ids | claude_ids


def _instruction_ids(*, root: Path) -> set[str]:
    """Collect GitHub instruction identifiers."""
    suffix = ".instructions.md"
    return {path.name.removesuffix(suffix) for path in (root / ".github/instructions").glob(f"*{suffix}")}


def _catalog_ids(*, root: Path, relative_path: str, key: str) -> tuple[set[str], list[Violation]]:
    """Collect identifiers from an optional setup catalog."""
    path = root / relative_path
    if not path.is_file():
        return set(), []
    raw, violations = _load_json_object(path)
    if raw is None:
        return set(), violations
    entries = raw.get(key)
    if not isinstance(entries, dict):
        return set(), [*violations, Violation(path=path, message=f"missing {key!r} object")]
    return {str(name) for name in entries}, violations


def _profile_inventory(*, root: Path) -> tuple[dict[str, set[str]], list[Violation]]:
    """Collect capabilities available to machine-readable profiles."""
    optional_mcp, optional_violations = _catalog_ids(
        root=root,
        relative_path=".agents/agentic-setup/mcp-catalog.json",
        key="servers",
    )
    assets, asset_violations = _catalog_ids(
        root=root,
        relative_path=".agents/agentic-setup/assets.json",
        key="assets",
    )
    active_mcp, mcp_violations = _load_mcp_servers(root / ".mcp.json", key="mcpServers")
    return (
        {
            "skills": _skill_ids(root=root),
            "agents": _agent_ids(root=root),
            "instructions": _instruction_ids(root=root),
            "mcpServers": active_mcp,
            "optionalMcpServers": optional_mcp,
            "assets": assets,
        },
        [*optional_violations, *asset_violations, *mcp_violations],
    )


def _validate_asset_paths(*, root: Path) -> list[Violation]:
    """Require every declared setup asset path to exist."""
    path = root / ".agents/agentic-setup/assets.json"
    if not path.is_file():
        return []
    raw, violations = _load_json_object(path)
    if raw is None:
        return violations
    entries = raw.get("assets")
    if not isinstance(entries, dict):
        return [*violations, Violation(path=path, message="missing 'assets' object")]
    for name, entry in entries.items():
        relative_path = entry.get("path") if isinstance(entry, dict) else None
        if not isinstance(relative_path, str) or not (path.parent / relative_path).exists():
            violations.append(Violation(path=path, message=f"asset {name!r} references a missing path"))
    return violations


def _validate_profile_extends(*, path: Path, name: object, profile: dict, profile_names: set[str]) -> list[Violation]:
    """Validate a profile's `extends` list references only known profiles."""
    parents = profile.get("extends")
    if not isinstance(parents, list) or not all(isinstance(parent, str) for parent in parents):
        return [Violation(path=path, message=f"profile {name!r} extends must be a string list")]
    return [
        Violation(path=path, message=f"profile {name!r} references unknown parent {parent!r}")
        for parent in parents
        if parent not in profile_names
    ]


def _validate_profile_capabilities(
    *, path: Path, name: object, profile: dict, inventory: dict[str, set[str]], declared: dict[str, set[str]]
) -> list[Violation]:
    """Validate a profile's capability lists and accumulate them into `declared`."""
    violations: list[Violation] = []
    for capability in PROFILE_CAPABILITIES:
        values = profile.get(capability)
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            violations.append(Violation(path=path, message=f"profile {name!r} {capability} must be a string list"))
            continue
        declared[capability].update(values)
        violations.extend(
            Violation(
                path=path,
                message=f"profile {name!r} references unknown {capability.removesuffix('s')} {value!r}",
            )
            for value in values
            if value not in inventory[capability]
        )
    return violations


def _validate_profiles(*, root: Path) -> list[Violation]:
    """Validate setup profile inheritance and capability references."""
    path = root / ".agents/agentic-setup/profiles.json"
    if not path.is_file():
        return []
    raw, violations = _load_json_object(path)
    if raw is None:
        return violations
    profiles = raw.get("profiles")
    if not isinstance(profiles, dict):
        return [*violations, Violation(path=path, message="missing 'profiles' object")]
    inventory, inventory_violations = _profile_inventory(root=root)
    violations.extend(inventory_violations)
    declared: dict[str, set[str]] = {capability: set() for capability in PROFILE_CAPABILITIES}
    profile_names = {str(name) for name in profiles}
    for name, profile in profiles.items():
        if not isinstance(profile, dict):
            violations.append(Violation(path=path, message=f"profile {name!r} must be an object"))
            continue
        violations.extend(_validate_profile_extends(path=path, name=name, profile=profile, profile_names=profile_names))
        violations.extend(
            _validate_profile_capabilities(
                path=path, name=name, profile=profile, inventory=inventory, declared=declared
            )
        )
    for capability in PROFILE_CAPABILITIES:
        for value in sorted(inventory[capability] - declared[capability]):
            violations.append(Violation(path=path, message=f"uncategorized {capability} capability {value!r}"))
    violations.extend(_validate_asset_paths(root=root))
    return violations


def _validate_skill_parity(*, root: Path) -> list[Violation]:
    inventories = [
        {path.relative_to(root / skill_root) for path in (root / skill_root).rglob("*") if path.is_file()}
        for skill_root in SKILL_ROOTS
    ]
    expected_paths = inventories[0]
    violations: list[Violation] = []
    for skill_root, paths in zip(SKILL_ROOTS[1:], inventories[1:], strict=True):
        if paths != expected_paths:
            violations.append(
                Violation(
                    path=root / skill_root,
                    message="skill file inventory differs from .github/skills",
                ),
            )

    for relative_path in sorted(expected_paths):
        files = [root / skill_root / relative_path for skill_root in SKILL_ROOTS]
        if all(path.is_file() for path in files) and len({path.read_bytes() for path in files}) != 1:
            violations.append(Violation(path=files[0], message="skill mirrors differ"))
    return violations


def _validate_skill(path: Path) -> list[Violation]:
    metadata, error = _read_frontmatter(path)
    if error is not None or metadata is None:
        return [Violation(path=path, message=error or "missing metadata")]

    violations: list[Violation] = []
    name = metadata.get("name")
    description = metadata.get("description")
    if name != path.parent.name:
        violations.append(Violation(path=path, message=f"skill name {name!r} must match its directory"))
    if not isinstance(name, str) or SKILL_NAME_PATTERN.fullmatch(name) is None:
        violations.append(Violation(path=path, message="skill name must use lowercase letters, digits, and hyphens"))
    if not isinstance(description, str) or not description.strip():
        violations.append(Violation(path=path, message="skill description is required"))
    return violations


def _validate_customization(path: Path, *, kind: str) -> list[Violation]:
    metadata, error = _read_frontmatter(path)
    if error is not None or metadata is None:
        return [Violation(path=path, message=error or "missing metadata")]

    violations: list[Violation] = []
    if kind == "claude-agent":
        name = metadata.get("name")
        tools = metadata.get("tools")
        expected_id = path.stem
        normalized_name = name.lower().replace(" ", "-") if isinstance(name, str) else ""
        invalid_name = normalized_name != expected_id
        invalid_identifier = AGENT_NAME_PATTERN.fullmatch(expected_id) is None
        if invalid_name or invalid_identifier:
            violations.append(
                Violation(
                    path=path,
                    message=f"Claude agent name must normalize to file identifier {expected_id!r}",
                )
            )
        if tools is not None and not isinstance(tools, str):
            violations.append(Violation(path=path, message="Claude agent tools must be a comma-separated string"))
    elif kind == "prompt":
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip():
            violations.append(Violation(path=path, message="prompt description is required"))
    return violations


def _validate_guidance(path: Path) -> list[Violation]:
    """Reject stale or prohibited instructions in active customization text."""
    text = path.read_text(encoding="utf-8-sig")
    violations = [Violation(path=path, message=message) for stale_text, message in STALE_GUIDANCE if stale_text in text]
    if PROHIBITED_GIT_COMMAND_PATTERN.search(text):
        violations.append(Violation(path=path, message="instructs an agent to run prohibited Git shell commands"))
    if any(marker in text for marker in MOJIBAKE_MARKERS):
        violations.append(Violation(path=path, message="contains likely UTF-8 mojibake"))
    return violations


def _project_tokens(*, root: Path) -> tuple[str, ...]:
    """Read explicit repository identity tokens from PROJECT.md."""
    project_path = root / "PROJECT.md"
    if not project_path.is_file():
        return ()
    for line in project_path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith(PROJECT_PORTABILITY_LINE_PREFIX):
            return tuple(re.findall(r"`([^`]+)`", line))
    return ()


def _validate_portable_skills(*, root: Path) -> list[Violation]:
    """Reject project identity tokens from portable skills."""
    tokens = _project_tokens(root=root)
    if not tokens:
        return []
    token_pattern = re.compile(
        rf"(?<![A-Za-z0-9])(?:{'|'.join(re.escape(token) for token in tokens)})(?![A-Za-z0-9])",
        re.IGNORECASE,
    )
    violations: list[Violation] = []
    for skill_root in SKILL_ROOTS:
        absolute_root = root / skill_root
        for path in absolute_root.rglob(SKILL_FILENAME):
            relative_parts = path.relative_to(absolute_root).parts
            if relative_parts and relative_parts[0] == "project":
                continue
            if match := token_pattern.search(path.read_text(encoding="utf-8-sig")):
                violations.append(
                    Violation(
                        path=path,
                        message=f"portable skill contains project token {match.group()!r}",
                    )
                )
    return violations


def validate(*, root: Path = ROOT) -> list[Violation]:
    """Validate customization metadata, MCP parity, and skill mirrors."""
    violations: list[Violation] = []
    for skill_root in SKILL_ROOTS:
        for path in sorted((root / skill_root).rglob(SKILL_FILENAME)):
            violations.extend(_validate_skill(path))

    for directory, pattern, kind in CUSTOMIZATION_GROUPS:
        for path in sorted((root / directory).rglob(pattern)):
            violations.extend(_validate_customization(path, kind=kind))

    guidance_paths = {
        path
        for directory in (Path(".github"), Path(".claude"), Path(".agents"))
        for path in (root / directory).rglob("*.md")
    }
    for path in sorted(guidance_paths):
        violations.extend(_validate_guidance(path))

    violations.extend(_validate_portable_skills(root=root))
    violations.extend(_validate_profiles(root=root))

    server_sets: list[set[str]] = []
    for relative_path, key in MCP_MANIFESTS:
        servers, manifest_violations = _load_mcp_servers(root / relative_path, key=key)
        server_sets.append(servers)
        violations.extend(manifest_violations)
    if server_sets and any(servers != server_sets[0] for servers in server_sets[1:]):
        violations.append(Violation(path=root / MCP_MANIFESTS[0][0], message="MCP server keys differ across manifests"))

    configured_servers = server_sets[0] if server_sets else set()
    for path in sorted((root / GITHUB_AGENTS_DIR).rglob(GITHUB_AGENT_PATTERN)):
        referenced_servers = MCP_TOOL_PATTERN.findall(path.read_text(encoding="utf-8-sig"))
        violations.extend(
            Violation(path=path, message=f"references unconfigured MCP server {server_name!r}")
            for server_name in referenced_servers
            if server_name not in configured_servers and server_name not in EXTENSION_TOOL_NAMESPACES
        )

    violations.extend(_validate_skill_parity(root=root))
    return violations


def main() -> int:
    """Print customization violations and return a process exit code."""
    violations = validate()
    if not violations:
        print("Agent customizations are consistent.")
        return 0

    print(f"Agent customization violations ({len(violations)}):")
    for violation in violations:
        print(f"  {violation.format(root=ROOT)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
