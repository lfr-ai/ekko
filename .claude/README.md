# AI Assistant Configuration (`.claude/`)

This folder contains the repository-scoped Claude Code configuration. It is
self-contained — all Claude Code behavior is defined within this directory and
the root-level `CLAUDE.md` file. This configuration does not reference or depend
on any other platform-specific configuration.

## What is authoritative

- Claude Code baseline: `CLAUDE.md` (repo root)
- Claude Code settings: `settings.json`
- Claude Code MCP: `mcp.json`

## Current structure

```text
.claude/
├── settings.json       # Permissions, hooks, environment, plugins
├── settings.local.json # Local overrides (gitignored)
├── mcp.json            # MCP server configuration
├── README.md           # This file
├── agents/             # Agent profiles (*.md)
│   ├── architect.md
│   ├── code-reviewer.md
│   ├── devops.md
│   ├── frontend-reviewer.md
│   ├── refactorer.md
│   ├── researcher.md
│   ├── sdd.md
│   ├── tdd.md
│   └── test-writer.md
├── commands/           # Custom slash commands
│   ├── commit.md
│   └── opsx/           # OpenSpec workflow commands
│       ├── apply.md
│       ├── archive.md
│       ├── bulk-archive.md
│       ├── continue.md
│       ├── explore.md
│       ├── ff.md
│       ├── new.md
│       ├── onboard.md
│       ├── propose.md
│       ├── sync.md
│       └── verify.md
├── rules/              # Path-scoped rules for Claude
│   ├── architecture.md
│   ├── cognitive-load.md
│   ├── ddd.md
│   ├── docs-sync.md
│   ├── prompt.md
│   ├── python-conventions.md
│   ├── registry.md
│   ├── sdd.md
│   ├── shell.md
│   ├── tdd.md
│   └── testing.md
└── skills/             # Reusable skills (*/SKILL.md)
    ├── clean-architecture/
    ├── ddd/
    ├── dry-refactoring/
    ├── gitnexus/
    ├── jscpd/
    ├── openspec/
    ├── python-conventions/
    ├── quality-gate/
    ├── sdd/
    ├── tdd/
    └── testing-conventions/
```

## Agent profiles

The nine agents in `agents/` define specialized agent behaviors:

- architect
- code-reviewer
- devops
- frontend-reviewer
- refactorer
- researcher
- sdd
- tdd
- test-writer

All agents share these properties:

1. Same agent roster as defined in the agent profiles table.
2. Execution-capable behavior by default (read/search/edit/write/run scripts).
3. Agents never execute `git` shell commands; all git operations are manual.
4. Agents include `user-invocable: false` in YAML frontmatter to avoid duplicate
   entries in VS Code's agent picker.

## Settings summary

`settings.json` provides project defaults for:

- Tool permissions (allow/ask/deny)
- Environment variables
- Hooks (tool-guardian, dependency-license-checker)
- Plugin enablement
- Worktree symlink directories

Sensitive files remain denied for reads (e.g., `.env` patterns and key material).
Git shell commands are denied by policy and runtime guardrails.

## MCP servers

Claude Code MCP server configuration lives in `mcp.json`.

## Hooks

Hook registration is configured in `settings.json`. Hook scripts are referenced
by relative path from the project root.
