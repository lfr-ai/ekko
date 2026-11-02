# Agentic setup — design rationale

Why this repo's portable agent setup (backend-only, frontend-only, full-stack)
is shaped the way it is. The copy procedure itself lives in the
`project-bootstrap` skill (see `.agents/skills/project-bootstrap/SKILL.md`) —
this file only records the decisions and trade-offs behind it.

Standard runtime directories (`.github`, `.claude`, `.agents/skills`) remain in
their documented locations so clients discover them. Selection is organized in
this hidden, agent-only `.agents/agentic-setup/` directory: `profiles.json` maps
shared/backend/frontend/full-stack/project capabilities (including active MCP
servers), `assets.json` with `assets/` holds copyable agent-facing bundles, and
`PROJECT.template.md` seeds target-project facts.

## Ownership

| Concern | Portable source | Project source |
| --- | --- | --- |
| Always-on policy | `AGENTS.md`, `CLAUDE.md`, Copilot instructions | `PROJECT.md` facts |
| File conventions | `.github/instructions/`, `.claude/rules/` | project-specific globs only |
| Workflows | three mirrored `skills/` trees | `skills/project/` |
| Agent roles | `.github/agents/`, `.claude/agents/` | remove unused roles per shape |
| Tool servers | root and VS Code MCP manifests | only servers the project uses |
| Enforcement | `.agents/guard/verify_agent_config.py` | explicit portability tokens |

## Project shapes

- **Backend-only:** uv + Task at root; `src/<pkg>/` Clean Architecture.
- **Frontend-only:** Bun at root; Vite/React/Biome/Tailwind/shadcn/Vitest/Playwright.
- **Full-stack:** uv at root and a bounded `frontend/` Bun package. Never share
  package-manager state or import source across the backend/frontend boundary.

Bun is also a `shared`-tier prerequisite in every shape, independent of the
application stack: it is the sole runtime for the agent hook scripts under
`.agents/guard/` (`tool-guardian.ts` for `PreToolUse`, `license-guardian.ts` for
`PostToolUse`, and `session-context.ts` for `SessionStart`), the same tier Python+uv already occupies for
`verify_agent_config.py` and the other portable guard scripts. A backend-only
project installs Bun for this reason alone, the same way a frontend-only
project already installs Python+uv for the agent-config guard.

Concrete ports, proxies, coverage thresholds, visual tokens, environment prefixes,
cloud identifiers, and deployment topology belong in `PROJECT.md` or normal
application configuration—not portable skills.

## Reference repositories reviewed

| Repository | Kept | Rejected |
| --- | --- | --- |
| `copier-fullstack-template` | feature-aware project shapes, layered frontend, rendered-template thinking | giant service locator, unsafe defaults, Copier/git mechanics outside a template repo |
| `ekko` | Bun/Vite/Biome configs, semantic Tailwind tokens, architecture-check concept | product-specific desktop/audio/GraphQL setup, unpinned remote installers |
| `claim_handler_v3` | cross-platform hook concept, namespaced full-stack tasks | stale inventories, Git/pip license hook, ORM-in-Core guidance |
| `kris_frontend` | shadcn aliases, Vitest/Playwright patterns, frontend agent focus | instruction discovery drift, mixed lockfiles, stale OpenSpec prompts, oversized tool lists |

This repository remains the canonical reference implementation for three-tree
skill parity, project overlays, uv-only Python, strict typing, stdlib logging,
configuration facets, and Clean Architecture boundaries.

## Frontend baseline

- Bun owns dependency state; commit `bun.lock` and use frozen installs in CI.
- Vite + React (Oxc) owns development/build; SWC is opt-in for a verified plugin
  or measured need. Project config owns ports and proxies.
- Biome owns formatting, linting, CSS, and import organization.
- TypeScript is strict; aliases agree across TypeScript, Vite, and shadcn.
- Tailwind CSS v4 uses the Vite plugin and semantic CSS variables.
- Vitest/Testing Library test behavior; Playwright tests isolated user journeys.
- shadcn primitives live in `presentation/components/ui`; application hooks and
  utilities keep their own aliases.
- Chrome DevTools MCP handles console/network/performance/memory diagnosis;
  Playwright remains the deterministic journey/test tool.
- Storybook (`@storybook/addon-mcp`) covers the component workbench and copies
  with the `frontend` profile's MCP set by default, but its endpoint only
  responds once the project installs Storybook, enables the addon, and runs a
  real dev-server task — see the `frontend/testing` skill for the exact steps.

## Backend baseline

- `main.py`/app factory assembles FastAPI, lifespan, middleware, exception handlers,
  routers, metrics, and request-state dependencies.
- `infrastructure/logging.py` owns idempotent stdlib logging and context filters.
- `presentation/api/middleware/rate_limiter.py` owns rate-limit policy and limiter.
- Configuration uses typed `*Settings` facets and consumer-owned `_XConfig`
  protocols; infrastructure never imports the aggregate app config.
- Postman MCP (minimal tool set) covers a project that owns a maintained
  Postman collection as a contract artifact. Wire it per project via
  `profiles.json`; never add one the project does not actually use.

## Copy procedure

The step-by-step copy checklist is owned by the `project-bootstrap` skill
(`.agents/skills/project-bootstrap/SKILL.md`) — do not duplicate it here; update
that skill if the procedure changes.

## Hook model

- Shared hook logic is dependency-light TypeScript executed directly by Bun.
- `.github/hooks/*.json` and `.claude/settings.json` mirror event-to-script
  wiring; the guard compares them and checks every target exists.
- VS Code loads only `.github/hooks`. Its default Claude-settings hook discovery
  is disabled because VS Code currently ignores Claude matchers and would run
  mirrored policies twice.
- Every hook validates JSON input and self-filters. `PreToolUse` is the only
  blocking policy point; `PostToolUse` reports completed dependency-policy
  failures but cannot undo the tool call.
- `SessionStart` performs bounded local file checks only—no Git, network,
  dependency installation, or full quality gate.

## Documentation sources

Current vendor guidance was checked for Agent Skills, VS Code/Claude hooks, Bun,
Biome, Vite, Vitest, Tailwind CSS v4, shadcn/ui, Storybook, and Playwright.
Context7 official-source indexes and vendor documentation were both consulted.
