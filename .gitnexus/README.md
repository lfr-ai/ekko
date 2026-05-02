# GitNexus Configuration

This directory contains [GitNexus](https://github.com/abhigyanpatwari/GitNexus)
configuration for the **Ekko** project.

GitNexus is a zero-server code intelligence engine that indexes the codebase into a
knowledge graph and can expose structure-aware context to AI coding agents via MCP.

## Contents

| Path | Purpose |
|------|---------|
| `config.json` | Indexing scope and MCP tool configuration |
| `hooks/post-commit` | Optional incremental post-commit re-index hook |

## Core Commands

- Build/rebuild index: `gitnexus analyze`
- Force full re-index: `gitnexus analyze --force`
- Incremental update: `gitnexus analyze --incremental`
- Index health: `gitnexus status`
- Run MCP server: `gitnexus mcp`

## MCP Integration

VS Code MCP configuration is stored in `.vscode/mcp.json`.

## Git Tracking Policy

Only configuration and hooks are committed:

- ✅ commit: `.gitnexus/config.json`, `.gitnexus/README.md`, `.gitnexus/hooks/*`
- 🚫 ignore: generated index/cache/artifact files under `.gitnexus/`
