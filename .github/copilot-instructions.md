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

## Default Working Method

Apply this to every task unless the user explicitly asks for a lighter touch:

**IMPORTANT!** You MUST be exhaustive and follow best practices. Consult, search,
and fetch the web and relevant documentation. Make an extensive TODO/plan, then
run a systematic walkthrough ensuring everything is addressed and considered —
clean, aligned, consistent, up to date, and working. Keep cognitive load
manageable and follow the existing structure, setup, and conventions. Enforce
Clean Architecture and ensure alignment and consistency throughout the codebase.

## Response Format

End every response with a short `tldr;` section, placed **last** so it is easy to
find. Keep it minimal and human-readable — only the most important information
(key files touched, changes made, and any next step) as a few tight bullets, with
no extra prose. Omit the `tldr;` only when the user explicitly requests otherwise.

## Architecture

- Follow Clean Architecture dependency direction (outer layers depend inward).
- Keep domain/core framework-agnostic.
- Keep adapters/integrations in infrastructure.
- Keep orchestration in application.
- Keep controllers/routes thin.
- Configuration naming: `*Settings` = an environment-sourced facet (a `BaseSettings` subclass owning one cohesive group of prefixed env fields, composed into the app config); `*Config` = a complete assembled configuration (the aggregate app config and its per-environment subclasses) or a consumer's structural view of it.
- Build config-consuming components via `from_config(cls, config: _XConfig)` where `_XConfig` is a private structural `Protocol` (same module) naming only the fields read; never import the aggregate app config (it satisfies the protocol structurally). Name the view `_<Component>Config`, never `_<…>Settings`.

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
- Keep VS Code settings aligned:
  - disable external MCP discovery providers under `"chat.mcp.discovery.enabled"`
  - `"chat.mcp.autoStart": true`

## OpenSpec workflow

Use OpenSpec for non-trivial features/refactors:

- `/propose <change>`
- `/apply <change>`
- `/sync <change>`
- `/verify <change>`
- `/archive <change>`

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
