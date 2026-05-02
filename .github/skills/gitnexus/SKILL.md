---
name: gitnexus
description: Graph-powered code intelligence tool for AI agents via MCP.
---

# Skill: GitNexus

## What It Is

GitNexus is a graph-powered code intelligence tool that builds a knowledge graph
of the codebase. AI agents (GitHub Copilot, Claude Code) query this graph
through the Model Context Protocol (MCP) to get accurate, up-to-date structural
information about the project -- imports, call chains, module boundaries, and
cross-file relationships.

## Why It Is Used

- **Accurate context** -- agents receive precise dependency and call-graph data
  instead of relying on heuristic file search.
- **Architecture awareness** -- the graph encodes Clean Architecture layer
  boundaries, making it easier for agents to respect import rules.
- **Faster agent responses** -- pre-indexed knowledge avoids redundant file
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

GitNexus is configured as an MCP server in `.vscode/mcp.json`. Once configured,
VS Code Copilot (and other MCP-aware agents) can query the knowledge graph
directly during chat sessions -- no manual CLI invocation required.

Example `.vscode/mcp.json` entry:

```json
{
  "servers": {
    "gitnexus": {
      "command": "gitnexus",
      "args": ["mcp"]
    }
  }
}
```

After adding the entry, restart VS Code or reload the MCP server list to
activate the integration.

## When to Rebuild the Index

Rebuild the knowledge graph (`gitnexus analyze .`) when:

- **Major refactors** -- files moved, renamed, or layers restructured.
- **New modules added** -- new packages or service layers introduced.
- **Post-merge** -- after pulling large feature branches.
- **Stale index** -- `gitnexus status` reports the index is outdated.

For incremental updates on smaller changes, GitNexus supports a **post-commit
hook** that re-indexes only the changed files automatically.

## Post-Commit Hook

To enable automatic incremental indexing after each commit, add a post-commit
hook:

```bash
# .git/hooks/post-commit
#!/bin/sh
gitnexus analyze --incremental .
```

Make the hook executable:

```bash
chmod +x .git/hooks/post-commit
```

## Quick Reference

```bash
# First-time setup
gitnexus setup

# Build the full knowledge graph
gitnexus analyze .

# Check index health
gitnexus status

# Start MCP server manually (usually handled by VS Code)
gitnexus mcp
```

## Rules

- Run `gitnexus analyze .` after significant structural changes.
- Keep the `.vscode/mcp.json` entry up to date if the GitNexus CLI path changes.
- Do not commit the generated index files to version control (they should be
  in `.gitignore`).
- Prefer incremental indexing via the post-commit hook for day-to-day work.
