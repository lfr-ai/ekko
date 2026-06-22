---
description: Repository-wide development conventions (project-agnostic)
applyTo: "**"
---

# Development Instructions

Use this file as the global Copilot baseline.

## Scope and precedence

1. This file (global baseline)
2. `.github/instructions/*.instructions.md` (path-scoped rules)
3. `.github/skills/**/SKILL.md` (task-specific playbooks)

Prefer the most specific applicable rule.

## Architecture

- Follow Clean Architecture dependency direction (outer layers depend inward).
- Keep domain/core framework-agnostic.
- Keep adapters/integrations in infrastructure.
- Keep orchestration in application.
- Keep controllers/routes thin.

## Frontend-first baseline

- React + TypeScript strict mode.
- Vite-based build pipeline.
- shadcn/ui components via CLI (never copy-paste component source from docs).
- Storybook for component docs and interaction coverage.
- Playwright for end-to-end flows.
- Accessibility checks (role/label selectors first).

## Agentic + MCP baseline

- Maintain parity for these MCP servers in `.vscode/mcp.json` and `.mcp.json`:
  - `context7`
  - `gitnexus`
  - `playwright`
  - `shadcn` (frontend workspaces)
  - `storybook` (frontend component review)
- Keep VS Code settings aligned:
  - `"chat.mcp.discovery.enabled": false`
  - `"chat.mcp.autoStart": true`

## OpenSpec workflow

Use OpenSpec for non-trivial features/refactors:

- `/opsx-propose <change>`
- `/opsx-apply <change>`
- `/opsx-sync <change>`
- `/opsx-verify <change>`
- `/opsx-archive <change>`

Behavior specs should stay implementation-agnostic; put implementation detail in tasks/design docs.

## Quality rules

- Keep changes minimal, reversible, and well-scoped.
- Update docs when behavior/configuration changes.
- No hardcoded secrets.
- Keep `.env.example` current when new variables are introduced.
- Keep `.secrets.baseline` tracked.

## Validation before completion

- Run test suite(s).
- Run lint/format/typecheck.
- Run configured quality/pre-commit hooks where available.
