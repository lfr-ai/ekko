# Proposal: modernize-python314-typing-architecture-agentic

## Intent

Modernize Ekko from a Python 3.12-only baseline to a single, reproducible Python 3.14 production runtime while preserving behavior and strengthening the repository's type semantics, Clean Architecture enforcement, packaging reliability, and agent governance. The change addresses contradictory runtime declarations, stale type-alias guidance, an unverified Windows frozen-app path, transport-layer persistence leakage, and duplicated or invalid agent customizations that can cause different tools to apply incompatible rules.

The modernization must prefer executable policy over prose, semantic type choices over mechanical alias conversion, and small rollback-friendly phases over a repository-wide big-bang rewrite.

## Scope

### In scope

- Repair deterministic test and PyInstaller baseline defects before changing the runtime.
- Move the backend runtime, resolver metadata, lockfile, static-analysis targets, test runners, CI, containers, development container, packaging, and active documentation to Python 3.14.
- Preserve locked dependency versions during the runtime migration unless a version change is required for Python 3.14 compatibility and is separately justified.
- Define and enforce a custom-type taxonomy covering bare primitives, PEP 695 transparent aliases, `NewType` opaque identifiers, validated value objects, `TypedDict`, dataclasses, protocols, and abstract collection interfaces.
- Audit every production alias and remove only aliases proven dead or semantically redundant.
- Tighten Clean Architecture where executable evidence identifies leakage, including the GraphQL readiness database probe, DI construction paths, protocol-facing container types, and local quality-gate coverage.
- Align backend and frontend architecture checks with local tasks, pre-commit, tests, and CI.
- Repair agent definitions, instruction scopes, skills, MCP declarations, hook registration, OpenSpec claims, and runtime/type/architecture guidance so each supported client receives one coherent policy.
- Add tests or validators for runtime declarations, architecture contracts, typing policy, customization metadata, and packaging behavior.
- Update active documentation and behavior specifications together with code and configuration.

### Out of scope

- Free-threaded CPython.
- Python 3.15 prereleases.
- Broad dependency upgrades unrelated to Python 3.14 compatibility.
- Mechanical conversion of ordinary primitives to `NewType`.
- Replacing validated scalar classes with aliases or `NewType`.
- Database schema changes or implementation of deferred repository adapters.
- New product features, authentication redesign, or UI redesign.
- Depending on external comparison repositories at runtime or documenting comparison provenance in repository artifacts.

## Success Criteria

- All active runtime declarations resolve to standard GIL-enabled Python 3.14 with `requires-python = ">=3.14,<3.15"` and a lockfile valid for that range.
- The resolved locked package versions do not change except where an explicitly documented compatibility requirement makes a change unavoidable.
- Ruff targets `py314`, ty and tox use an explicit Python 3.14 environment, and no stale Python 3.12 compatibility exceptions remain.
- Every production custom type is classified and justified; transparent aliases use PEP 695 syntax, opaque identifiers use `NewType` only when interchange must be rejected statically, and runtime invariants use validated classes/value objects.
- Backend import-linter contracts, frontend dependency checks, local quality tasks, pre-commit, and CI all enforce the documented dependency direction.
- Presentation code no longer imports SQLAlchemy or performs direct database probing.
- Infrastructure construction is centralized in composition, and public container annotations expose ports where ports exist.
- Supported agent clients load valid, non-contradictory agent/skill/instruction metadata with declared MCP capabilities matching actual configuration and one hook registration per event/client.
- The Windows frozen application builds, launches, serves its health endpoint and bundled frontend, and shuts down cleanly under Python 3.14.
- Backend tests, architecture checks, lint, formatting, type checking, convention tests, OpenSpec validation, frontend architecture/lint/type/test/build checks, container build/health smoke, and pre-commit all pass after the final change.
- Native audio capture and Azure Speech release smokes are documented and executed before a production release claim.

## Risks and Constraints

- Overall risk is high because the runtime, native Windows audio dependencies, frozen packaging, CI, architecture boundaries, and agent governance change in one modernization program.
- The runtime cutover must be atomic: Python pins, package metadata, lockfile, Ruff/ty/tox, CI, containers, and documentation move together.
- The current 3.12 artifact remains the operational rollback point until Python 3.14 frozen-app, container, audio, and provider smokes pass.
- Database schemas and persisted data formats must remain unchanged so rollback does not require data migration.
- `NewType` is static-only and must never be presented as runtime validation.
- Existing behavior-preserving aliases must not be made nominal without call-site impact analysis and type-checker evidence.
- Agent customization cleanup must restore loadability before deleting duplicate surfaces; discovery changes require client diagnostics before removal.
- Repository policy prohibits agent-run Git commands; verification uses workspace tools, tasks, and change detection instead.

## Affected Areas

- Backend: core types and ports, application health orchestration, infrastructure database probe, composition container/lifespan, presentation GraphQL and REST dependencies, tests, packaging specification.
- Frontend: architecture-check integration and quality-gate coverage; no product behavior changes are planned.
- Infrastructure/CI: Python pins, uv lock, Ruff/ty/tox/pre-commit, GitHub Actions, containers, development container, Windows PyInstaller build and smoke validation.
- Docs/Developer workflow: root/backend READMEs, contribution guidance, runtime and architecture documentation, OpenSpec platform requirements, agent definitions, skills, instructions, prompts, MCP manifests, hooks, VS Code/Claude discovery settings, and modernization roadmap.
