# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Docker production setup with multi-stage Containerfile.
- Caddy reverse proxy configuration with snippet architecture.
- Standalone config files (pytest.ini, tox.ini, ty.toml, .coveragerc).
- Backend-scoped bandit.toml for security scanning.
- Claude Code CLI instructions (CLAUDE.md).
- Local CI quality gate via `task ci:local`.
- Hadolint configuration for Dockerfile linting.
- DevContainer compose-based setup with Containerfile.dev.

### Changed

- Cleaned pyproject.toml to contain only uv/project settings.
- Replaced mypy with ty for type checking.
- Updated pre-commit hooks (added hadolint, removed gitleaks redundancy).
- Consolidated GitHub Actions workflows.
- Updated devcontainer to compose-based architecture.

### Fixed

- Clean Architecture boundary validation.
- Dependency management (Renovate only, no Dependabot).
- GitHub Actions using correct uv run commands.

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
