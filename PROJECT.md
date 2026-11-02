# Project Facts — Ekko

Project-specific overlay for the portable agent configuration.

## Identity

- Project shape: `full-stack`
- Backend package/source root: `ekko` / `backend/src/ekko`
- Frontend package/source root: `frontend` / `frontend/src`
- Environment-variable prefix: `EKKO_`
- Agent portability tokens: `ekko`, `lfr-ai`

## Toolchain

- Backend package manager/task runner: `uv` + Task
- Frontend package manager: Bun (`frontend/package.json` pins the version)
- Main commands: `task dev`, `task test`, `task lint`, `task lint:api`,
  `task spec:validate`, `task typecheck`, `task check`

## Architecture

- Backend dependency flow: `config → core → {ai | infrastructure} → application → presentation → composition → cli`
- Frontend dependency flow: `domain → infrastructure → application → presentation → router`; `lib` is shared
- Composition roots: `ekko.composition.app_factory:create_app` and `frontend/src/main.tsx`
- Boundary contracts: `core/ports`, REST/OpenAPI, Strawberry GraphQL, and frontend GraphQL documents

## Ubiquitous language

- **Transcript** — timestamped speech-to-text text emitted by an audio source.
- **Conversation** — an ordered interaction containing messages and transcripts.
- **Prompt version** — immutable prompt content selected by the prompt registry.
- **PII policy** — profile controlling anonymization before text crosses an AI boundary.

## Specs, decisions, and code intelligence

- Specs: `openspec/specs/`
- Significant decisions: `openspec/changes/archive/` and focused documents under `docs/`
- Code graph/index: GitNexus repository `ekko`; refresh with `gitnexus analyze`
  (the Dev Container installs the pinned CLI with Bun). Resources:
  `gitnexus://repo/ekko/context`, `gitnexus://repo/ekko/clusters`, and
  `gitnexus://repo/ekko/processes`.

## Data and persistence

- Local persistence: SQLite configured by `DatabaseSettings`
- ORM and migrations: `backend/src/ekko/infrastructure/db/` and `backend/alembic/`

## CI and deployment

- CI: `.github/workflows/`
- Deployment: Azure Container Apps defined under `azure/iac/`; local desktop packaging uses PyInstaller

Keep procedures in skills, behavior in specs, operational detail in focused docs,
and transient discoveries in repository memory.
