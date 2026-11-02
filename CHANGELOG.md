# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Validation-only Terraform/HCL mirror of the Azure Bicep topology, with
  per-environment OIDC backend examples and path-scoped TFLint checks.
- Configurable LiteLLM deployments and fallbacks with provider-neutral errors
  and opt-in token/cost telemetry through the Core metrics port.
- `POST /summarize` REST endpoint: summarizes submitted transcript chunks via
  the existing LLM gateway. This activates the previously dormant summarizer
  service behind a real, mounted use case.
- Frontend: a "Summarize a transcript" page wired to `/summarize`, the first
  real user flow in the UI (paste transcript, get an anonymized summary).
- README: CI, CodeQL, coverage, and license badges.
- Added `CODE_OF_CONDUCT.md`, `.github/PULL_REQUEST_TEMPLATE.md`, and GitHub
  issue forms (bug report, feature request) to complete the repository's
  community-standards checklist.
- Added `SUPPORT.md` and an issue-chooser link to it.

### Fixed

- `tools/conventions/check_magic_strings.py` contained two Python 2-only
  `except A, B:` clauses (invalid Python 3 syntax), so the script raised a
  `SyntaxError` under plain CPython even though ruff/ty's parsers tolerated
  it silently. The CI `magic-strings` job masked this via
  `continue-on-error: true`. Split both into separate `except` blocks per
  exception type (ruff's formatter was found to actively strip the
  syntactically-required parentheses back off a tupled `except (A, B):`
  form, re-corrupting it) and removed `continue-on-error` so the job is now
  a real blocking gate.
- `tools/generate_openapi.py`: moved a type-only `yaml.nodes.ScalarNode`
  import behind `TYPE_CHECKING` (ruff `TC002`).

### Security

- PII anonymization is now mandatory before any text reaches the LLM gateway.
  `SummarizerService` runs every chunk through the PII policy first and fails
  closed (`PIIPolicyViolationError`, HTTP 422) instead of ever forwarding raw
  text.
- Bumped the transitive `aiohttp` dependency to 3.14.3, resolving three known
  advisories (PYSEC-2026-3545/3546/3547).
- Pinned every third-party GitHub Action across all workflows to an immutable
  commit SHA (with a version comment), closing a supply-chain tag-mutation gap.
- Fixed `deploy-container-apps-acr.yml` watching the `main` branch while the
  repository's actual branch is `master`, so the workflow could never trigger.
- Added a tag-triggered `release.yml` workflow that builds the Windows EXE and
  publishes SHA256 checksums, an SPDX SBOM, and a GitHub build provenance
  attestation (SLSA, via Sigstore/OIDC) alongside the GitHub Release. Code
  signing is intentionally not wired up yet (no certificate available); the
  workflow documents the exact plug-in point for one.

### Changed

- Migrated the backend runtime and toolchain to Python 3.14 while preserving all
  locked dependency versions.
- Standardized transparent aliases on PEP 695 syntax and documented when to use
  aliases, `NewType`, validated value objects, typed mappings, and protocols.
- Moved GraphQL database readiness behind a core port and application service;
  presentation no longer imports SQLAlchemy.
- Added backend and frontend architecture checks to local quality gates and
  strengthened presentation framework-import enforcement.
- Repaired and automated the Windows frozen-app launch, health, bundled-UI, and
  cleanup smoke test.
- Strengthened agent customization validation for runtime, typing, architecture,
  MCP transport, and prohibited command-policy drift.
- Replaced mypy with ty for type checking.
- Consolidated quality gates (`task check`, `task verify`).
- Updated pre-commit hooks (hadolint, architecture boundary validation).
- Standardized on `fastapi.status` constants for HTTP codes.
- Rewrote `docs/modernization-roadmap.md` as a concise, human-readable roadmap.

### Removed

- Dead handler/DTO code (unused conversation placeholders).
- Stale docs references.
- Unused `DeploymentTarget`/`FeatureFlag` enums, the unused
  `PathSettings.interaction_dir_path`, and the stray root
  `TERRAFORM_VALIDATION_FINAL.txt` report.

## [0.1.0] - 2026-05-02

### Added

- Initial project setup.
- Clean Architecture implementation (core, application, infrastructure, presentation).
- AI components (CrewAI HMAS, PII anonymization, LangChain, OpenAI).
- Backend stack (FastAPI, Strawberry GraphQL, SQLAlchemy + SQLite, Alembic).
- Frontend stack (React 19, TypeScript, Vite 6, shadcn/ui, Tailwind CSS v4, Zustand, TanStack Query).
- Testing infrastructure (pytest, Hypothesis, Vitest, React Testing Library, Playwright).
- Development tools (Taskfile, uv, Bun, pre-commit hooks).
- Documentation (architecture overview, contributing guidelines, security policy).
