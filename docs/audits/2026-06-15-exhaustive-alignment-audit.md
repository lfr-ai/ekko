# Exhaustive Alignment & Production-Readiness Audit (2026-06-15)

## Scope

- Primary repo audited: `ekko`
- Benchmark repo compared: `koda_automation`
- Focus areas:
  - Clean Architecture boundary compliance
  - Structure/tooling/config alignment
  - Build/test/lint operability on Windows
  - Dependency hygiene and update posture
  - Production-readiness baseline

## Key Implemented Fixes (this session)

1. **Windows task reliability fixed**
   - Updated `.vscode/tasks.json` backend tasks to use `options.env.UV_LINK_MODE=copy` instead of POSIX inline env assignment (`UV_LINK_MODE=copy ...`).
   - This unblocks task execution in PowerShell.

2. **Dependency audit flow hardened**
   - Removed `pip-audit` from backend default development dependency group to avoid resolver deadlock with `crewai` (`tomli` constraint conflict).
   - Kept vulnerability auditing via `scripts/security/dependency_audit.py` using `uv tool run --from pip-audit`.
   - Updated invocations in:
     - `tasks/backend.yml`
     - `.github/workflows/ci.yml`
     - `.github/agents/security.agent.md`
     - `.github/agents/devops.agent.md`
     - `README.md`

3. **MCP policy consistency**
   - Updated `.vscode/settings.json` to set `chat.mcp.discovery.enabled` to boolean `false` (policy-consistent).

4. **Shell instruction scope consistency**
   - Expanded shell instruction globs to include `.zsh` files:
     - `.github/instructions/shell.instructions.md`
     - `.claude/rules/shell.md`

5. **Low-risk backend lint debt reduction**
   - Fixed unused argument violations in:
     - `backend/src/ekko/presentation/api/exception_handlers.py`
     - `backend/src/ekko/presentation/api/middleware/cors.py`
   - Performed targeted cleanup across GraphQL/application/infrastructure modules to clear lint/type debt while preserving API compatibility.

6. **GraphQL compatibility hardening**
   - Restored runtime typing imports required by Strawberry schema evaluation.
   - Added dual endpoint support for both existing GraphQL paths:
     - `/graphql`
     - `/graphql/graphql`

## Verified Results

- **Clean Architecture boundary checker**: ✅ passes (`tools/security/check_architecture_boundaries.py`)
- **Frontend lint/tests**: ✅ pass
- **Backend lint**: ✅ passes (`ruff check src`)
- **Backend type checks**: ✅ passes (`ty check src`)
- **Backend tests**: ✅ passes (`218 passed, 9 skipped`)

## Cross-Repo Alignment Findings (`ekko` vs `koda_automation`)

### Strong alignment already present

- Shared governance files and conventions (`AGENTS.md`, `CLAUDE.md`, `.github/instructions`, `.claude/rules`)
- Taskfile-based automation with includes and environment layering
- MCP baseline (`context7`, `gitnexus`, `playwright`; `shadcn` additionally in `ekko` frontend)
- Security and quality hooks in pre-commit and CI

### Meaningful deltas retained intentionally

- `ekko` uses monorepo split (`backend/`, `frontend/`), while `koda_automation` is primarily single Python project (`src/` root package)
- `ekko` includes additional AI + frontend scaffolding and OpenSpec orchestration layers
- These are functional/architectural differences, not anti-patterns

## Open High-Priority Backlog (must complete for production-quality gate)

### P0 — Resolve local Ruff binary lock contention on Windows

Observed `os error 5` due locked `ruff.exe` under `.venv` while tools/extensions run concurrently.
Mitigation:
- Prefer serial backend checks in a clean terminal session
- Ensure no concurrent `uv run`/task invocations mutate env simultaneously

### P1 — Dependency update program

Outdated packages identified (representative):
- Backend: `fastapi`, `starlette`, `pydantic`, `langchain*`, `opentelemetry*`, `ruff`, etc.
- Frontend: `@biomejs/biome`, `tailwindcss`, `esbuild` (patch/minor), plus major updates (`storybook`, `vite`, `vitest`, `zod`) requiring migration plans.

Recommended rollout:
1. Patch/minor safe updates first
2. Run full `task check` + integration tests
3. Separate major-version migrations into isolated changes

## Production-Readiness Checklist Status

- [x] Architecture boundary enforcement script in place and passing
- [x] Security audit path resilient to dependency conflicts
- [x] Windows VS Code task operability fixed
- [x] MCP discovery/autostart policy aligned
- [x] Backend lint debt fully cleared (current session scope)
- [x] Full quality gate green on backend (`lint`, `typecheck`, `tests`)
- [ ] Staged dependency modernization completed and verified

## Recommended Next Execution Batch

1. Execute patch/minor dependency upgrades (backend + frontend), one toolchain group at a time.
2. Re-run backend/frontend quality gates after each upgrade batch.
3. Plan major-version migrations separately (`vite`, `vitest`, `storybook`, `zod`, selected backend stacks).

## References Consulted

- Task docs: `https://taskfile.dev/docs/guide`
- uv dependency groups and resolver behavior: `https://docs.astral.sh/uv/concepts/projects/dependencies/`
- FastAPI deployment guidance: `https://fastapi.tiangolo.com/deployment/`
- Pydantic latest docs: `https://pydantic.dev/docs/validation/latest/get-started/`
