---
name: gitnexus
description: Graph-powered code intelligence for analyzing dependencies, call chains, and module boundaries. Use when analyzing cross-layer dependencies, before refactoring, or when verifying Clean Architecture compliance.
when_to_use: When analyzing code dependencies, import chains, module boundaries, or architecture relationships. Use before cross-layer refactors, when exploring unfamiliar code, or when verifying Clean Architecture compliance across files.
paths:
  - "backend/src/ekko/**/*.py"
  - "frontend/src/**/*.{ts,tsx}"
---

# Skill: GitNexus

## What It Is

GitNexus is a graph-powered code intelligence tool that builds a knowledge graph
of the codebase. AI agents (GitHub Copilot, Claude Code) query this graph
through the Model Context Protocol (MCP) to get accurate, up-to-date structural
information about the project — imports, call chains, module boundaries, and
cross-file relationships.

## Why It Is Used

- **Accurate context** — agents receive precise dependency and call-graph data
  instead of relying on heuristic file search.
- **Architecture awareness** — the graph encodes Clean Architecture layer
  boundaries, making it easier for agents to respect import rules.
- **Faster agent responses** — pre-indexed knowledge avoids redundant file
  scanning during chat sessions.

## Installation

GitNexus is installed globally via Bun:

```bash
bun install -g gitnexus@latest
```

## CLI Commands

| Command | Purpose |
|---------|---------|
| `gitnexus setup` | Initial configuration (run once per repo) |
| `gitnexus analyze .` | Build or rebuild the full knowledge graph |
| `gitnexus status` | Show current index status and staleness |

## MCP Integration

GitNexus is configured as an MCP server in both `.mcp.json` (Claude Code CLI)
and `.vscode/mcp.json` (VS Code Copilot). Once configured, agents can query
the knowledge graph directly during chat sessions.

`.mcp.json` entry:

```json
{
  "mcpServers": {
    "gitnexus": {
      "type": "stdio",
      "command": "bunx",
      "args": ["gitnexus@latest", "mcp"],
      "cwd": "."
    }
  }
}
```

## When to Rebuild the Index

Rebuild the knowledge graph (`gitnexus analyze .`) when:

- **Major refactors** — files moved, renamed, or layers restructured.
- **New modules added** — new packages or service layers introduced.
- **Post-merge** — after pulling large feature branches.
- **Stale index** — `gitnexus status` reports the index is outdated.

The `.gitnexus/hooks/post-commit` hook handles incremental re-indexing
automatically after each commit.

## Quick Reference

```bash
# First-time setup
gitnexus setup

# Build the full knowledge graph
gitnexus analyze .

# Check index health
gitnexus status

# Start MCP server manually (usually handled by the IDE)
gitnexus mcp
```

## Rules

- Run `gitnexus analyze .` after significant structural changes.
- Keep `.mcp.json` and `.vscode/mcp.json` entries up to date.
- Do not commit generated index files (covered in `.gitignore`).
- Prefer incremental indexing via the post-commit hook for day-to-day work.
