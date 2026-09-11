# Design: modernize-python314-typing-architecture-agentic

## Architecture Impact

- Impacted layers/modules:
  - `core`: custom-type taxonomy, removal of dead aliases, port contracts for readiness and typed runtime capabilities.
  - `application`: readiness orchestration that depends on an inward port rather than transport-owned SQL.
  - `infrastructure`: concrete database readiness probe and existing external adapters.
  - `composition`: the only concrete wiring location, including callback-aware speech-service construction.
  - `presentation`: thin GraphQL/REST adapters that consume application services and public core contracts only.
  - `frontend`: no product behavior change; architecture validation becomes part of standard local gates.
  - toolchain: Python 3.14 metadata, lock, lint/type/test targets, containers, CI, frozen packaging, and release smoke tests.
  - agent governance: canonical policy ownership, client-native agent metadata, scoped instructions, MCP parity, and customization validation.
- Clean Architecture boundary considerations:
  - The executable import-linter contracts remain authoritative for current dependency direction.
  - Presentation may use public application DTOs/services and public core contracts, but it may not import SQLAlchemy, infrastructure, AI-provider SDKs, or composition implementations.
  - The database readiness capability is represented as an inward protocol. Infrastructure implements it; application coordinates it; presentation renders it; composition wires it.
  - Concrete adapter selection remains in composition. Application code depends on ports even where current layer rules technically permit concrete inward imports.
  - AI and infrastructure remain independent sibling implementation layers.
  - Health endpoints that inspect transport runtime state may remain at the transport edge; only persistence probing moves inward.

## Technical Approach

### 1. Establish a trustworthy baseline

Repair deterministic failures before changing interpreter semantics:

1. Correct the prompt-registry test root calculation.
2. Reconcile the development prompt-version-set expectation with the declared environment policy.
3. Correct the frozen-app analysis data collection and remove nonexistent/undeclared package inputs.
4. Replace executable-file existence checking with process launch, bounded health polling, bundled-frontend verification, and cleanup.
5. Normalize the canonical health endpoint across container, compose, and frozen-app probes.
6. Run the complete Python 3.12 quality and packaging baseline and record any environment-only blockers.

This phase proves whether later failures are migration regressions or pre-existing defects.

### 2. Select Python 3.14 as one exact production line

Use standard GIL-enabled CPython 3.14 with `>=3.14,<3.15` rather than an open-ended `>=3.14` range. Python 3.14 is a stable bugfix release with a longer support runway than 3.13, current locked dependency versions install and import under it, and the frozen-app toolchain supports it.

Change atomically:

- root and backend `.python-version`;
- `requires-python` and seeded `uv.lock` refresh;
- Ruff `py314` target and newly enabled modernization fixes;
- explicit ty and tox Python targets;
- pre-commit interpreter;
- all backend GitHub Actions jobs;
- production/development container bases;
- active developer and agent documentation.

Do not invoke uv's broad upgrade mode. The existing lock is a preference set; package-version changes require an explicit compatibility note.

### 3. Adopt a semantic custom-type taxonomy

Use this decision order:

1. **Validated value object/class** when invalid runtime values must be impossible at construction.
2. **`NewType`** when two opaque identities share a runtime primitive but accidental interchange must fail static checking.
3. **PEP 695 `type` alias** for recurring compound shapes or architecture-decoupling names that remain transparent.
4. **`TypedDict`** for fixed dictionary keys at serialization boundaries.
5. **Frozen dataclass/Pydantic model** for named data with behavior, validation, or evolution needs.
6. **Protocol/ABC** for behavioral structure.
7. **Abstract collection (`Mapping`, `Sequence`, `Iterable`)** for read-only input capabilities.
8. **Bare primitive/container** when a custom name adds no semantic or readability value.

Audit decisions:

- Keep `ModelDeploymentName` as a transparent architecture-decoupling alias unless a dedicated nominal migration proves that arbitrary strings must be rejected statically.
- Remove `PromptContent` if reference analysis confirms no public consumer.
- Retain `MaxTokens`, `Temperature`, and `Confidence` as validated runtime classes; adopt `Confidence` in production only where the domain invariant is intended and serialization behavior is verified.
- Resolve `BaseDict` and `JSONDict` duplication by defining one open-shape contract or by introducing precise boundary structures where keys are known. Do not create a recursive JSON union solely for aesthetic precision if frameworks cannot consume it cleanly.
- Improve the retry decorator signature with PEP 695 `ParamSpec` only if ty and Ruff preserve call signatures without casts or ignores.
- Remove the stale Ruff exception around the already-modern response alias.

### 4. Tighten executable architecture

Introduce a readiness port and application service rather than a generic “health framework.” Keep the module deep: one simple readiness result outward, persistence details hidden in infrastructure.

Add explicit import-linter protection preventing presentation from importing persistence/provider SDKs. Add contract tests so future config edits cannot silently drop the boundary.

Centralize callback-aware speech adapter construction in `Container` through a factory method or explicit builder. Avoid mutating cached singleton semantics when callbacks differ; a builder method is preferable to parameterizing a cached property.

Expose `PIIAnonymizerPort` from composition. Add a typed stream-controller dependency shared by REST and GraphQL transport paths instead of repeated untyped `app.state` access.

Wire backend and frontend architecture validation into `task check`, `ci:local`, and appropriate pre-commit scopes.

### 5. Repair agent governance before de-duplication

Use one canonical source per concern:

- universal hard rules: `AGENTS.md`;
- runtime and dependencies: `backend/pyproject.toml`, `backend/uv.lock`, `.python-version`;
- architecture: import-linter contracts plus tests;
- portable shared skills: `.github/skills`;
- Copilot agents/instructions/prompts: `.github`;
- Claude agents/rules/commands: `.claude`, using Claude-native metadata;
- MCP inventory: root `.mcp.json`, with a generated or validated VS Code adapter;
- hook implementations: root `hooks/scripts`;
- behavior requirements: `openspec/specs` and change deltas.

Sequence:

1. Make all active Claude agents loadable with valid names/tools and restore least privilege.
2. Add missing skill frontmatter and correct stale runtime/type/architecture/spec/test guidance in the canonical skill tree.
3. Align MCP declarations with an explicit supported baseline. Prefer configuring the required frontend servers only if they have reproducible commands and are actively used; otherwise narrow baseline claims.
4. Remove prohibited Git-command guidance and replace it with IDE SCM context or GitNexus/workspace change detection.
5. Fix test/spec instruction globs and narrow Keploy guidance to relevant requests/assets.
6. Prevent duplicate hook discovery and ensure PowerShell is guarded.
7. Add a customization validator covering metadata, tool vocabulary, duplicate identities, stale paths, MCP capability references, canonical/mirror drift, and prohibited command guidance.
8. Only after validation passes, stop VS Code from discovering Claude mirrors and remove unmanaged duplicate skill roots/legacy aliases that no supported client needs.
9. Shorten always-loaded documents by moving volatile inventories to generated documentation.

### 6. Keep changes independently reversible

Each phase changes one class of risk and ends with a quality gate. Runtime files and Python 3.13+-only generic simplifications form one atomic rollback unit. Architecture moves introduce no schema changes. Agent duplicate removal occurs only after replacement discovery is proven.

## Data and Contract Changes

- API/GraphQL contract updates:
  - Readiness response shape and public endpoint behavior remain unchanged.
  - Health probes converge on one existing canonical endpoint.
  - No intentional REST, GraphQL schema, or WebSocket contract break is planned.
  - GraphQL schema hash/contract tests MUST demonstrate no unintended schema change.
- Persistence/migration changes:
  - None. The readiness probe moves behind a port but executes an equivalent connectivity check.
  - No Alembic revision and no data migration are expected.
- Event/message format changes:
  - None. Audio callbacks and transcript payloads remain behaviorally identical.
- Typing contracts:
  - Removing an unused exported alias is a source-level API cleanup and requires reference validation.
  - Nominalizing any currently transparent alias is explicitly deferred unless separately reviewed because it changes accepted static call sites.
- Agent/developer contracts:
  - Python 3.14 becomes required.
  - Client customization identities and available MCP capabilities become validated rather than aspirational.

## Testing Strategy

- Unit:
  - Custom scalar validation and static typing fixtures.
  - Readiness application service behavior for ready, unavailable, and exceptional probes.
  - Database probe adapter behavior.
  - Container protocol annotations and builder behavior.
  - Architecture manifest/contract presence.
  - Customization metadata and canonical-policy validation.
  - Frozen build script helper behavior where practical.
- Integration:
  - REST health/readiness behavior with available and unavailable database connections.
  - Full backend suite on Python 3.14.
  - Prompt registry/environment behavior.
  - SQLite startup/migrations and SSE transcript streaming.
  - Container health behavior.
- End-to-end:
  - Windows frozen application build, launch, health, frontend asset response, and termination.
  - Full-stack frontend/backend smoke.
  - Representative Windows loopback/microphone and Azure Speech release checklist.
- Regression focus:
  - Locked dependency versions, native wheel selection, generated GraphQL schema, callback delivery, lifespan shutdown, frozen resource paths, MCP discovery, duplicate hooks, and instructions applied to wrong paths.

## Operability and Observability

- Logging/metrics/tracing changes:
  - Readiness failures retain structured diagnostics at the adapter/application boundary without exposing persistence details in responses.
  - Frozen-app smoke emits explicit build, launch, probe, timeout, and cleanup steps with nonzero failure exits.
  - No new external telemetry service is required.
- Alerting/diagnostics impact:
  - CI gains a Windows frozen-build smoke job and deterministic customization validation.
  - Local `task check` reports architecture violations directly.
  - Runtime mismatch and stale lock failures occur before tests rather than during packaging.
  - Agent configuration failures identify the invalid client surface instead of silently dropping tools.

## Rollout and Rollback

- Rollout approach:
  1. Phase A: capture and repair the Python 3.12 behavioral/packaging baseline.
  2. Phase B: run a disposable Python 3.14 canary using exact locked versions and focused/full tests without changing committed runtime policy.
  3. Phase C: atomically cut committed runtime/toolchain declarations to 3.14 and regenerate the lock without upgrades.
  4. Phase D: migrate typing semantics and architecture in small tested slices.
  5. Phase E: repair agent customizations, add validation, then de-duplicate discovery.
  6. Phase F: validate Linux container, Windows frozen app, full stack, native audio, speech provider, and all quality gates.
- Rollback trigger:
  - A locked native dependency cannot install/import on supported platforms.
  - Frozen app cannot build, launch, serve bundled resources, or shut down reliably.
  - Native audio or speech release smoke regresses.
  - Public API/GraphQL behavior changes unintentionally.
  - Customization cleanup removes a required client capability without a functioning replacement.
- Rollback method:
  - Restore Python pins, metadata, lockfile, Ruff/ty/tox/pre-commit, CI/container declarations, and defaulted-generator syntax as one runtime unit.
  - Deploy the last verified Python 3.12 container digest and desktop artifact.
  - Revert readiness wiring independently; no persistence rollback is needed.
  - Restore a removed customization root/discovery entry independently if client diagnostics regress.
  - Keep old artifacts until the Python 3.14 release candidate completes all promotion gates.

## Open Questions

- Whether the supported repository MCP baseline should remain `context7` plus `gitnexus`, or whether reproducible Playwright, shadcn, and Storybook server definitions should be restored for applicable clients.
- Whether `ModelDeploymentName` should become nominal in a later change; current usage supports keeping it transparent for this migration.
- Whether `Confidence` should replace all production confidence `float` annotations or remain a construction helper until serialization boundaries are redesigned.
- Whether the application layer should be mechanically forbidden from all AI/infrastructure imports now or in a separate inversion change; current source appears compatible, but the policy change affects future design.
- Whether release policy requires Python 3.13 as a temporary compatibility canary or permits direct 3.12-to-3.14 promotion after disposable validation.
