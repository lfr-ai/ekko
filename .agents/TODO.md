# Agentic Topology TODO

Governance checklist for parity, tooling policy, MCP consistency, and
production-readiness criteria.

## Parity Enforcement

- [x] Skills parity across `.github/skills`, `.claude/skills`, `.agents/skills`
- [x] OpenSpec prompts synced to grouped `openspec/` subfolders
- [x] OpenSpec commands synced to grouped `openspec/` subfolders
- [x] GitNexus prompts and commands scaffolded in all surfaces
- [x] Agent profiles synced from `.claude/agents` to `.agents/agents`
- [x] `sync_agentic_setup.py` created and operational (0 drift on last run)

## Tooling Policy

- [x] `ruff` is the only linter/formatter
- [x] `ty` is the only type checker
- [x] `pyright` removed from all configurations and plugins
- [x] `ms-pyright.pyright` added to `unwantedRecommendations` in extensions.json
- [x] `astral-sh.ty` added to VS Code extension recommendations
- [x] Verify no `pyright` references remain in any config file
- [x] `pre-commit` hooks aligned with reference baseline

## MCP Consistency

- [x] `.vscode/mcp.json` defines authoritative workspace MCP servers
- [x] `.agents/mcp.servers.json` mirrors neutral baseline
- [x] `context7`, `gitnexus`, `playwright` present in all MCP configs
- [x] `shadcn` present (ekko-specific, frontend stack)

## Production Readiness

- [x] Clean Architecture boundaries enforced via pre-commit hook
- [x] Magic string checker operational
- [x] Module docstring checker operational
- [x] Architecture boundary checker operational
- [x] Dependency audit hook configured
- [x] jscpd copy-paste detection in pre-commit (single hook, no duplicates)
- [x] lychee link checking in pre-commit
- [x] xenon complexity gate configured
- [x] bandit security scanning configured
- [x] detect-secrets baseline maintained
- [x] Dependencies resolved with no conflicts (crewai + otel pinned)
- [x] Dev dependency versions aligned with reference baseline

## Skills Alignment with reference baseline

- [x] `clean-architecture/SKILL.md`
- [x] `ddd/SKILL.md`
- [x] `dry-refactoring/SKILL.md`
- [x] `gitnexus/SKILL.md` (flat — ekko uses single SKILL.md)
- [x] `jscpd/SKILL.md`
- [x] `openspec/SKILL.md` (plus individual subskills)
- [x] `python-conventions/SKILL.md`
- [x] `quality-gate/SKILL.md`
- [x] `sdd/SKILL.md`
- [x] `tdd/SKILL.md`
- [x] `testing-conventions/SKILL.md`

## Ekko-specific Additions (beyond reference baseline)

- [x] `frontend-react-stack/SKILL.md`
- [x] `naming-registry/SKILL.md`
- [x] `deploy-check/SKILL.md`
- [x] Frontend agents: `frontend-react.agent.md`, `frontend-reviewer.md`
- [x] Database agent: `database.agent.md`
- [x] Security agent: `security.agent.md`

## Validation Commands

Run these after any agentic/config change:

1. `uv run --project backend python .agents/sync_agentic_setup.py`
2. `uv run --project backend ruff check .agents/sync_agentic_setup.py`
3. `uv run --project backend pre-commit validate-config`
4. `uv lock` (in backend/)

## Exit Criteria (all met)

- [x] No references to pyright remain in project-controlled agentic config
- [x] Ty and Ruff are the only documented lint/type-check defaults
- [x] Grouped prompt/command structure is consistent across surfaces
- [x] MCP server set is consistent across VS Code, Claude, and neutral topology
- [x] Sync script can be run repeatedly with no unintended diffs
- [x] Dependency resolution clean (no conflicts)

---

## Exhaustive TODO — baseline parity + production hardening (2026-07-20)

### Phase 0 — Environment Integrity (blocking)

- [x] Stabilize Windows/OneDrive install workflow for `frontend/node_modules` (prevent `EBUSY`/`EPERM` lock churn)
- [ ] Rebuild frontend dependency tree with deterministic install (`bun ci`/frozen lock in clean state)
- [x] Verify frontend test runner integrity (`vitest`, `vite`, transitive packages such as `pathe`, `aria-hidden`)
- [x] Re-run frontend unit tests to green baseline

### Phase 1 — Structural Parity vs reference baseline

- [x] Produce file-level parity matrix for root/tooling/config/governance files
- [ ] Validate and reconcile `.vscode` parity intent (keep ekko-specific files only when justified)
- [ ] Validate and reconcile `.github` parity intent (retain additional templates/workflows with explicit rationale)
- [ ] Validate and reconcile `.claude`/`.agents`/`.github` agent-surface parity and drift
- [ ] Validate OpenSpec layout parity (`openspec/config.yaml`, schemas, change artifact paths)

### Phase 2 — Clean Architecture Enforcement

- [x] Run architecture boundary checks across backend source and tests
- [ ] Inspect and remediate dependency-direction violations (inward-only policy)
- [ ] Ensure controllers/routes remain thin and orchestration stays in application layer
- [ ] Ensure domain/core remains framework-agnostic and free from outer-layer leakage
- [ ] Verify prompt/AI modules respect declared layering and portability constraints

### Phase 2b — GraphQL-first migration (REST parity-safe)

- [x] Make GraphQL stream control mutation call real controller behavior (start/pause parity with REST)
- [x] Ensure GraphQL mutation flow applies PII anonymization for message payloads
- [x] Add regression tests proving stream controller invocation from GraphQL
- [x] Normalize canonical endpoint usage to `/graphql` across backend tests, frontend clients/tests, Storybook, Playwright, and Postman
- [x] Keep backward-compatible `/graphql/graphql` routing during transition
- [x] Disable REST stream endpoints by default (`EKKO_REST_STREAM_ENDPOINTS_ENABLED=false`) to enforce GraphQL-first stream control
- [x] Replace placeholder GraphQL subscriptions with app-state queue-backed runtime behavior + PII-safe transcript emission
- [x] Externalize GraphQL abuse limiter settings (depth/aliases/tokens) and wire schema to settings
- [x] Prefer `graphql-transport-ws` with production default disabling legacy `graphql-ws` protocol
- [x] Add explicit REST deprecation headers and OpenAPI deprecation metadata for `/start_stream` and `/pause_stream`
- [x] Add CI GraphQL schema governance check (contract fingerprint drift detection)

### Phase 3 — Production Readiness & Security

- [x] Re-validate pre-commit gate completeness (lint/type/test/security/docs sync)
- [x] Remove local quality-gate soft passes (`|| true`) for shell/spelling/duplication checks
- [x] Make workflow lint validation strict by requiring local `actionlint`
- [ ] Reconcile dependency update strategy (`renovate.json`, automerge/schedule/risk controls)
- [x] Re-run security scanning baseline alignment (`bandit`, `detect-secrets`, dependency audit)
- [ ] Verify container + reverse proxy hardening posture (Docker/Caddy health, restarts, exposure)
- [ ] Verify Azure IaC baseline for HA/observability/security settings and documented parameters

### Phase 4 — Frontend Stack Conformance

- [x] Re-validate React/Vite/shadcn conventions and folder boundaries
- [x] Ensure Storybook/Playwright/Vitest integration is consistent and runnable
- [ ] Remove stale frontend artifacts and duplicated lock/tool outputs
- [ ] Confirm accessibility/testing conventions in changed components

### Phase 5 — Documentation, Drift Control, and Proof

- [x] Update audit docs with parity deltas, decisions, and exceptions
- [x] Add deep-dive hardening report with strictness decisions and rollout backlog
- [ ] Record intentional divergence items with rationale
- [x] Re-run quality gates end-to-end and capture evidence summary
- [ ] Final consistency sweep: naming/structure/config coherence across all surfaces
- [x] Record GraphQL-first migration evidence and validations in audit docs

### Hygiene cleanup pass (2026-07-20)

- [x] Remove stale backend artifact marker files
- [x] Remove stale backend transient Keploy log artifact

### Completion Criteria for this campaign

- [x] Frontend/backend tests pass from clean dependency state
- [x] Lint/type checks pass
- [ ] Security checks pass (current blocker: dependency CVEs from `pip-audit`)
- [x] Architecture boundaries pass with no unresolved violations
- [ ] Parity matrix completed and all non-parity items explained/accepted
- [ ] Docs updated to reflect final operational state
