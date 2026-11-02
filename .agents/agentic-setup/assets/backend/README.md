# Backend blueprint (agent-facing)

> LLM/agent asset. Not product docs. Copy checklist for standing up the backend
> agentic setup in a new **backend** or **full-stack** repository. Capability
> names below resolve against [`profiles.json`](../../profiles.json) (profile
> `backend`, plus `shared`). This blueprint **references** the canonical skills
> and this repo's real files as exemplars — it does not duplicate them.

## Copy order

1. **Shared core first** — copy the `shared` profile capabilities (see
   [`assets/agent-knowledge-base`](../agent-knowledge-base/README.md) and the
   `shared` entry in [`profiles.json`](../../profiles.json)).
2. **Backend capabilities** — copy every item listed for the `backend` profile.
3. **Full-stack** — also copy the `frontend` profile; `fullstack` extends both.

## What to copy (backend profile)

| Kind | Items | Runtime location(s) |
| --- | --- | --- |
| Skills | `api-contracts`, `backend-structure`, `configuration`, `database-migrations`, `ddd`, `jinja2`, `litellm`, `observability-stack`, `pyinstaller`, `python-conventions`, `rag`, `task-queue`, `testing-conventions` | `.github/skills/`, `.claude/skills/`, `.agents/skills/` (byte-identical) |
| Agents | `ddd`, `sdd`, `tdd`, `testing` | `.github/agents/*.agent.md`, `.claude/agents/*.md` |
| Instructions/rules | `api-contracts`, `python-conventions`, `cognitive-load`, `database`, `ddd`, `jinja2`, `prompt`, `pyinstaller`, `tdd`, `testing` | `.github/instructions/*.instructions.md` + paired `.claude/rules/*.md` |
| Active MCP | `context7`, `gitnexus`, `microsoft-learn`, `github` (from `shared`), `postman` | root `.mcp.json` + `.vscode/mcp.json` + `.warp/.mcp.json` |

Copy the whole skill/instruction/rule/agent **set together**; the guard
(`.agents/guard/verify_agent_config.py`) enforces three-runtime parity and
instruction/rule pairing.

## Layered `src/<package>/` structure (Clean Architecture)

Enforced by the `backend-structure` and `clean-architecture` skills:

```text
src/<package>/
  core/            # domain: entities, value objects, ports (stdlib-only)
  application/     # use cases, orchestration, DTOs
  infrastructure/  # adapters: persistence, http clients, external services
  presentation/    # api: routers, middleware, lifespan, exception handlers
  composition/     # DI container wiring adapters to ports
  configs/         # *Settings facets composed into *Config
  main.py          # app factory: FastAPI(lifespan=create_lifespan(...))
```

Dependencies flow inward (`core` → `application` → `infrastructure`/`presentation`
→ `composition` → `main`). Core never imports outward. See Hard Rules 9 and 18 in
`AGENTS.md`.

## Toolchain baseline

uv (`uv.lock`) + Task (`Taskfile.yml`) · Ruff (lint + format) · ty (types) ·
pytest (+ coverage) · pre-commit · Alembic (migrations). Commit `uv.lock`; use
frozen sync in CI. Never add another Python package manager (Hard Rule 19).
Details live in `python-conventions`, `configuration`, `testing-conventions`, and
`database-migrations` — do not duplicate them here.

## Loggers

Stdlib `logging` only (Hard Rule 15): `import logging`; module logger is
`_logger = logging.getLogger(__name__)`; module-qualified members
(`logging.getLogger`, `logging.handlers.TimedRotatingFileHandler`). Configure once
at composition/startup; never `print()`.

## FastAPI app pattern

- App factory builds `FastAPI(...)` and passes
  `lifespan=create_lifespan(container_factory=lambda: Container(config=config))`
  — a **factory**, so importing the app opens no DB/clients at import time.
- Config facets are `*Settings`; a component consumes `from_config(cls, config:
  _XConfig)` with a private structural `Protocol` (Hard Rule 20).
- Routers/middleware/exception handlers register in the presentation layer.

## Editor, MCP, container

- `.vscode/settings.json` holds shared correctness settings only; personal
  cosmetics go to user settings or `settings.example.jsonc`.
- `.vscode/extensions.json` — curate the recommended set for the stack (Python,
  Ruff, ty, Even Better TOML, YAML, Task, containers, DB, spell check). Use this
  repo's file as the exemplar.
- `.vscode/tasks.json` / `launch.json` — start from the portable
  [`tasks.json.template`](../../../skills/vscode-workspace/assets/tasks.json.template)
  and
  [`launch.json.template`](../../../skills/vscode-workspace/assets/launch.json.template),
  then remove entries the destination shape does not use. Keybindings are user
  preferences and are never copied as repository policy.
- Baseline MCP: Context7, GitNexus, Microsoft Learn. Devcontainers install only
  selected runtimes, cache the package manager, and run frozen sync on create.

## Template sources & token substitution

The exemplar for every file is this repo itself; copy the real file and replace
the portability tokens (recorded in the target `PROJECT.md`):

| Token | Meaning | Example |
| --- | --- | --- |
| `{{package}}` | Python package / source root | `myapp` → `src/myapp/` |
| `{{PREFIX}}` | Environment-variable prefix | `MYAPP_` |
| `{{ProjectTitle}}` | Human/display name | `MyApp` |

| Target file | Exemplar / owner |
| --- | --- |
| `PROJECT.md` | [`../../PROJECT.template.md`](../../PROJECT.template.md) |
| `pyproject.toml`, `ruff.toml`, `ty.toml`, `pytest.ini`, `tox.ini` | repo root (dev-tool config) |
| `.importlinter` | repo root — `clean-architecture` skill's layers contract (kept out of `pyproject.toml`; the only config format `import-linter` needs) |
| `docs/dependency-license-policy.md` | repo root — rationale for `pyproject.toml`'s `[tool.pip-licenses]` table (that table itself cannot move: `pip-licenses` only reads `pyproject.toml`) |
| `Taskfile.yml`, `.pre-commit-config.yaml` | repo root (`python-conventions`, `quality-gate`) |
| `alembic.ini`, `alembic/` | `database-migrations` skill |
| `src/{{package}}/main.py`, `presentation/api/lifespan.py`, `configs/` | `backend-structure`, `configuration` |
| `.vscode/tasks.json`, `.vscode/launch.json` | `vscode-workspace` skill assets linked above |

## Verify after copying

Run the destination repository's agent-config guard through its declared
toolchain, then `task check` and `task test`. Green output means skills, agents,
instruction/rule pairs, MCP declarations, and this profile/catalog wiring are
aligned across all runtimes.
