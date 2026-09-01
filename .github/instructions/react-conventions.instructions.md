---
description: React component and hooks conventions
applyTo: "**/*.{tsx,jsx}"
---

# React Conventions

## Component design

- Keep components pure and idempotent.
- Prefer presentational components with orchestration delegated outside render.
- Use early returns to reduce nesting.
- Keep component responsibilities narrow and explicit.

## Hooks

- Follow Rules of Hooks strictly.
- Call hooks only at top level in React components and custom hooks.
- Do not call hooks in loops, conditions, event handlers, or nested functions.
- Keep custom hooks focused on a single use case.

## Side effects and data flow

- Keep side effects out of render logic.
- Keep external synchronization in effects only.
- Avoid redundant state; derive values where feasible.
- Keep server-state orchestration in dedicated application hooks.

## Testing alignment

- Test behavior from a user perspective.
- Prefer semantic queries in this order: role, label, text, then test id.
- Mock infrastructure boundaries, not business logic.
