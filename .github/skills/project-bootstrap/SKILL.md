---
name: project-bootstrap
description: Bootstrap a backend-only, frontend-only, or full-stack repository using the portable agent setup, Clean Architecture, uv and Task for Python, or Bun/Vite/Biome for React. Use when creating a new project, converting a repository into the standard structure, or copying this agent configuration elsewhere.
---

# Project bootstrap

Choose the project shape before creating files. Do not install dormant runtimes,
MCP servers, dependencies, ports, or container services.

Read `.agents/agentic-setup/profiles.json` and resolve the selected profile's
`extends` chain. It is the machine-readable shared/backend/frontend/full-stack/
project capability map; standard skill locations stay unchanged for tool
discovery.

## 1. Choose the shape

| Shape | Python | Frontend | Package ownership |
| --- | --- | --- | --- |
| Backend-only | `src/<pkg>/` | none | uv + Task at root |
| Frontend-only | none | repository root | Bun at root |
| Full-stack | `src/<pkg>/` | `frontend/` | uv at root; Bun only in `frontend/` |

Create `PROJECT.md` from `.agents/agentic-setup/PROJECT.template.md`, then record
package names, environment prefix, source roots, ports, CI/deployment, and
ubiquitous language. Portable skills read facts from that overlay rather than
embedding them.

Bun is required in every shape regardless of the table above: it is the sole
runtime for the shared Tool Guardian hook (`.agents/guard/tool-guardian.ts`),
the same tooling-only tier Python+uv already occupies for the agent-config
guard. A backend-only or frontend-only project installs it for this reason
even when the shape's own stack doesn't otherwise need it.

## 2. Copy the agent setup

Copy `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.github/`, `.claude/`, and the
configured MCP manifests.

Then:

1. Delete every `skills/project/` directory copied from the source repository.
2. Rewrite `PROJECT.md`, including explicit agent-portability tokens; rewrite
  `llms.txt` from `.agents/agentic-setup/llms.template.txt` alongside it.
3. Copy only capabilities resolved from `profiles.json`; add the `project`
  profile only after replacing source-project overlays with target-project ones.
4. Remove extensions and runtime settings that the selected shape cannot use;
  keep mirrored runtime inventories aligned.
5. Run the agent-config guard before scaffolding application code.

For repeatable scaffolding across many repos, turn this setup into a
[Copier](https://copier.readthedocs.io/) template: `copier.yml` questions for
package name, env prefix, and shape; a `.jinja` suffix on templated files; and a
recorded answers file. `copier copy` generates a new repo and `copier update`
pulls later template improvements into existing ones — the automated equivalent
of the manual copy above. Keep this manual path as the source of truth; the
template is a convenience, not a second config surface.

Copyable safe starting points:

- [`assets/copier.yml.template`](assets/copier.yml.template) — typed shape,
  package, and environment-prefix questions with `StrictUndefined`.
- [`assets/copier-answers.yml.jinja.template`](assets/copier-answers.yml.jinja.template)
  — generated update metadata; place it in the template subdirectory with the
  rendered name `{{ _copier_conf.answers_file }}.jinja`.

The starter intentionally has no `_tasks`, `_migrations`, or third-party Jinja
extensions: those execute code and force Copier's trust/unsafe mode. Add them
only for a reviewed, unavoidable migration workflow.

## 3. Scaffold application layers

- Backend: apply `backend-structure`, `configuration`, `clean-architecture`, and
  `testing-conventions`. Follow `assets/backend/README.md` for the copy checklist.
- Frontend: apply `frontend/react-stack`, `frontend/structure`, `frontend/shadcn`,
  `frontend/runtime-config`, `frontend/browser-debugging`, `frontend/testing`,
  `frontend/accessibility`, and `frontend/playwright`. Follow
  `assets/frontend/README.md` for the
  copy checklist; wire only the MCP servers listed for the `frontend` profile in
  `profiles.json` that the project actually uses.
- Full-stack: keep backend and frontend dependency graphs separate. Shared
  contracts are generated artifacts or transport schemas, never cross-layer
  source imports.

## 4. Tooling and tasks

- Backend commands use `uv run`; never add another Python package manager.
- Frontend commands use `bun run`; never create npm/Yarn/pnpm lockfiles.
- In full-stack projects, namespace Task targets (`backend:*`, `frontend:*`) and
  provide small aggregate `start`, `test`, `check`, and `build` tasks.
- Add Renovate managers only for package ecosystems actually present.

## 5. Editor, MCP, container, and deployment

- `.vscode/settings.json` contains shared correctness settings only; personal
  cosmetics stay in user settings or an example file. `tasks.json`/
  `launch.json`'s standard entries and thin-wrapper convention are the
  `vscode-workspace` skill's job — copy its `assets/tasks.json.template` and
  `assets/launch.json.template`, then delete whatever the project doesn't use.
- Keep Context7/code intelligence as baseline MCP. Add shadcn, Playwright, and
  Chrome DevTools for frontend work; the `storybook` entry copies with the
  `frontend` profile too, but only connects once the project installs
  Storybook, enables `@storybook/addon-mcp`, and runs its dev server — see the
  `frontend/testing` skill.
- Devcontainers install only selected runtimes, cache each package manager, run
  frozen dependency sync on create, and forward documented project ports.
- Use independent multi-stage backend/frontend images, frozen lockfiles, non-root
  runtime users, health checks, and explicit Compose dependencies.

## 6. Completion checklist

- Agent guard passes; no project tokens leak into portable skills.
- Each package has one package manager and one lockfile family.
- Architecture boundaries, environment templates, Task commands, editor settings,
  containers, and CI agree with `PROJECT.md`.
- Focused tests and each selected package's build/check commands pass.
- README stays a quick start plus links to focused guides.
- Run `codebase-onboarding` so `PROJECT.md`, OpenSpec, repository memory,
  GitNexus, and minimal architecture/decision docs reflect the generated project.
