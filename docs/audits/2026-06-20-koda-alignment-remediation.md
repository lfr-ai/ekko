# 2026-06-20 — koda_automation Alignment Remediation (Pass 1)

## Scope

This pass focused on high-confidence, low-risk alignment and production-readiness fixes based on:

- Direct comparison with available `koda_automation` baselines
- Existing in-repo baseline: `docs/audits/koda/README.md`
- Current diagnostics, task behavior, and test/lint/typecheck outcomes

## Key Findings Addressed

### 1) Windows backend task instability (uv auto-sync lock contention)

**Symptom**

- Backend VS Code tasks intermittently failed with:
  - `Access is denied (os error 5)`
  - lock on `backend/.venv/Scripts/ruff.exe`

**Remediation**

- Added `UV_NO_SYNC=1` to backend task environments in `.vscode/tasks.json`.
- Verified backend task suite executes successfully afterward.

### 2) Task command drift vs canonical backend taskfile

**Symptom**

- VS Code backend dev task used non-factory app target.
- VS Code backend typecheck task scanned `src` instead of `src/ekko`.

**Remediation**

- Updated `.vscode/tasks.json`:
  - `uvicorn ekko.composition.app_factory:create_app --factory`
  - `ty check src/ekko`

### 3) PowerShell pipeline verifier drift

**Symptom**

- `scripts/verify-pipeline.ps1` used direct `pip-audit` call.
- Architecture script path was outdated.

**Remediation**

- Switched to project wrapper:
  - `uv run python ../scripts/security/dependency_audit.py`
- Fixed architecture check path:
  - `uv run python tools/security/check_architecture_boundaries.py`

### 4) MCP config consistency drift

**Symptom**

- `.claude/mcp.json` diverged from workspace MCP defaults.

**Remediation**

- Updated `.claude/mcp.json` to align with workspace conventions:
  - Added `-y` for `npx` invocations
  - Added Playwright flags `--isolated --headless`
  - Added `storybook` MCP server entry

### 5) Frontend diagnostics and submit reliability

**Symptom**

- TS deprecation warning on `baseUrl` in `frontend/tsconfig.json`
- Claim intake form test regression after intermediate accessibility cleanup

**Remediation**

- Removed deprecated `baseUrl` from `frontend/tsconfig.json`.
- Hardened insurance condition select state updates in claim intake form:
  - `setValue(..., { shouldDirty: true, shouldValidate: true })`
- Kept improved semantic output usage for feedback/status.

### 6) Documentation/security contact staleness

**Symptom**

- README referenced outdated type checker (`mypy`) and stale model phrasing.
- README listed `gitleaks` in hooks while not present in pre-commit config.
- SECURITY contact used placeholder address.

**Remediation**

- Updated README references:
  - `mypy` → `ty`
  - model wording made environment-neutral
  - removed inaccurate `gitleaks` hook mention
- Updated `SECURITY.md` disclosure email to `lfr@tik-ai.dk`.

## Files Changed

- `.vscode/tasks.json`
- `scripts/verify-pipeline.ps1`
- `.claude/mcp.json`
- `frontend/tsconfig.json`
- `frontend/src/presentation/features/claim-intake/claim-intake-form.tsx`
- `README.md`
- `SECURITY.md`

## Verification Evidence

### Backend

- **Lint**: pass
- **Typecheck**: pass
- **Tests**: pass (`226 passed, 1 skipped`)

### Frontend

- **Lint**: pass
- **Tests**: pass (`123 passed, 1 skipped`)

### Compound gate

- **Quality: Run All Checks**: pass

## Remaining Follow-up (next pass)

1. Dependency modernization sweep (safe upgrade plan with lockfile/regression checks).
2. CI parity enhancement (`xenon`, `jscpd`, optional `tox` job policy).
3. Optional additional MCP parity/documented intentional deviations.
4. Broader non-blocking diagnostics cleanup unrelated to this remediation scope.

## Modernization Snapshot (Outdated Dependencies)

Dependency update backlog was captured with live commands:

- Backend: `uv pip list --outdated`
- Frontend: `bun outdated`

### Backend highlights

- Routine patch/minor updates available for core stack (`fastapi`, `sqlalchemy`, `ruff`, `ty`, `pytest`, `openai`, `langchain*`).
- Significant major-version jumps exist and should be staged carefully:
  - `protobuf` 5.x → 7.x
  - `websockets` 15.x → 16.x
  - `wrapt` 1.x → 2.x
  - multiple OpenTelemetry packages 1.34.x → 1.42.x

### Frontend highlights

- Safe patch/minor updates available (`@playwright/test`, `@tailwindcss/vite`, `tailwindcss`, `@biomejs/biome`).
- Major-version updates require a compatibility migration plan:
  - `typescript` 5.x → 6.x
  - `vite` 6.x → 8.x
  - `vitest` 3.x → 4.x
  - `storybook` 8.x → 10.x
  - `zod` 3.x → 4.x
  - `react-router` 7.x → 8.x

Recommendation: apply patch/minor updates first in small batches with full
`task check` + frontend test runs between each batch, then schedule major
upgrades as dedicated migration changes.
