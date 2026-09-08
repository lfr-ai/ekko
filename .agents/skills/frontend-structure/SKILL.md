---
name: frontend-structure
description: Enforce the React + TypeScript frontend project structure — layered src (application/domain/infrastructure/presentation/router/lib), provider bootstrap, route constants, shadcn ui folder, Tailwind v4, and file/naming conventions. Use when scaffolding a frontend, adding components/pages/hooks, or reviewing frontend layout.
---

# Frontend project structure (React + TypeScript + Clean Architecture)

## Layers (`src/`)

- `domain/` — models, types, pure domain logic (no framework deps)
- `application/` — hooks, stores, orchestration (server state via TanStack Query)
- `infrastructure/` — API clients, config, observability
- `presentation/` — components, pages, features, styles
- `router/` — route constants + router setup
- `lib/` — framework-agnostic utilities (e.g. `cn()`)

Dependencies flow inward: presentation → application → domain.

Use an automated import-boundary check in frontend packages. At minimum it must
reject domain imports from outer layers, presentation imports of concrete
infrastructure, and cross-feature relative imports that bypass public module
surfaces. A fast script may use text parsing initially; treat it as a guard, not
as a substitute for TypeScript resolution and architecture tests.

## Composition root

- `bootstrap.tsx` wires providers in order: `ErrorBoundary` → `ThemeProvider` →
  `QueryClientProvider` → router → `Toaster`. The entry (`app.ts` / `main.tsx`) mounts it.

## Routing

- Route paths are a single source of truth in `router/` (`ROUTES`, `NAV_ROUTES`
  constants); never hardcode path strings inside components.

## Components

- shadcn primitives in `presentation/components/ui/`; composed components in
  `presentation/components/`; pages in `presentation/pages/` with an `index.ts`
  re-export. Keep components thin and presentational; delegate orchestration to
  application hooks.

## Naming & exports

- kebab-case file names; PascalCase components and types; SCREAMING_SNAKE_CASE
  constants; `_`-prefixed internal constants. **Named exports only** (Biome
  `noDefaultExport`), except framework config files.

## Styling

- Tailwind v4 via the Vite plugin + CSS variables (no `tailwind.config` /
  `postcss.config`); no CSS modules; compose classes with `cn()`.

## Tests

- Unit/component: follow `frontend-testing` under `tests/` (happy-dom).
  E2E: Playwright under `tests/e2e/`. Prefer semantic queries: role → label →
  text → test id.
