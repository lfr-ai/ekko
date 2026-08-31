---
name: frontend-react-stack
description: Bootstrap or modernize a React frontend with Bun, Vite (SWC), strict TypeScript, Biome, Tailwind CSS v4, shadcn/ui, Vitest, Testing Library, and Playwright. Use for frontend-only repositories and bounded frontend packages in full-stack repositories.
---

# Frontend bootstrap (React + TypeScript)

Use the repository root for a frontend-only project. In a full-stack repository,
use a bounded `frontend/` package; Python remains owned by uv at the root and
JavaScript remains owned by Bun inside `frontend/`.

## Required artifacts

- `package.json` with an exact `packageManager` and scripts below.
- Committed text `bun.lock`; remove foreign lockfiles after verified migration.
- `bunfig.toml` only for intentional Bun settings (for example disabling
	auto-install); do not restate defaults without a reason.
- `tsconfig.json`, `vite.config.ts`, `biome.json`, `vitest.config.ts`,
	`playwright.config.ts`, and `components.json`.
- A locally pinned `shadcn` CLI dev dependency; use `bunx --bun shadcn`, not an
	unpinned remote CLI.
- `src/` laid out by the `frontend-structure` skill and a Tailwind CSS v4 entry
	under `presentation/styles/`.

## Stack

| Concern | Standard |
| --- | --- | --- |
| Runtime/package manager | Bun only; commit `bun.lock`; frozen installs in CI |
| UI/build | React 19 + Vite + `@vitejs/plugin-react-swc` |
| Types | Strict TypeScript; `@/*` resolves to `src/*` |
| Lint/format | Biome only; formatter, linter, assist/import organization |
| Styling | Tailwind CSS v4 Vite plugin + semantic CSS variables |
| Components | shadcn/ui (`new-york`) + Radix + Lucide |
| State/forms | TanStack Query, Zustand, React Hook Form + Zod |
| Tests | Vitest + Testing Library; Playwright for journeys |

Add optional libraries (TanStack Table, Sonner, fast-check, axe) only when a
feature uses them; do not preload a template with speculative dependencies.

## Package scripts

```bash
bun install
bun install --frozen-lockfile     # CI
bun run dev                       # vite
bun run build                     # tsc --noEmit && vite build
bun run check                     # biome check . && tsc --noEmit && vitest run
bun run check:fix                 # biome check --write .
bun run test                      # vitest run (never `bun test`)
bun run test:coverage             # vitest run --coverage
bun run test:e2e                  # playwright test
```

Use Task wrappers only after these package scripts exist. A full-stack root may
aggregate them as `frontend:*`; a frontend-only project can use Bun directly.

## Setup checklist

1. Scaffold Vite React + SWC + TypeScript in the chosen frontend root.
2. Install and configure Tailwind's Vite plugin and CSS-first import.
3. Configure strict TypeScript and matching Vite aliases.
4. Configure Biome, including CSS formatting and Tailwind directive parsing.
5. Initialize shadcn only after aliases and CSS paths are correct.
6. Add Vitest/Testing Library setup and Playwright configuration.
7. Add only the devcontainer runtimes, forwarded ports, Docker stages, MCP
	 servers, and Task wrappers required by the selected project shape.
8. Run the package's check/build/test scripts before claiming the scaffold works.

## Guardrails

- Never mix npm, Yarn, or pnpm state into a Bun package.
- Never hardcode portable ports, backend URLs, coverage thresholds, or visual
	tokens; those are project facts.
- Biome is the only formatter/linter; do not add ESLint or Prettier by habit.
- Follow `frontend-structure`, `frontend-testing`, `shadcn-ui`, `accessibility`,
  and `playwright`.
