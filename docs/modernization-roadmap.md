# Roadmap

Ekko is a local desktop tool today, not a hardened public service. This page
tracks what's shipped, what's in progress, and what's deliberately out of
scope.

**Scope decision:** Ekko targets single-user desktop use only. There is no
planned public-server product, so there is no OIDC/cloud-identity workstream —
see [SECURITY.md](../SECURITY.md) for why the API must stay off untrusted
networks. The Docker/Azure assets under `docker/` and `azure/` are kept for
local container testing and are not a supported release target.

## Done

- Backend and CI on Python 3.14, dependency versions unchanged.
- Full-scope lint (`ruff`) and type checking (`ty`) pass across production
  code, tests, tools, and migrations — no suppressions.
- Clean Architecture enforced on both backend (import-linter) and frontend
  (a dependency checker).
- Frontend on a single Bun lockfile with reproducible installs; strict
  TypeScript, Vitest, and the production build all pass.
- Storybook accessibility checks (Axe) run in CI.
- GraphQL trimmed to one read-only query; unused REST/subscription endpoints
  removed instead of left dormant.
- Agent/skill configs (Copilot, Claude, MCP) validated for schema and parity.
- `POST /summarize` activates the previously dormant summarizer: every chunk
  is anonymized before it reaches the LLM gateway, and a policy violation
  fails closed instead of leaking raw text (see [SECURITY.md](../SECURITY.md)).
- Tag-triggered release pipeline (`.github/workflows/release.yml`) builds the
  Windows EXE, publishes SHA256 checksums, an SPDX SBOM, and a SLSA build
  provenance attestation alongside the GitHub Release.

## In progress

- **Persistence** — the Alembic migration matches the ORM (just a `users`
  table); there's no conversation/message schema and no engine wired into
  production yet. `/summarize` is intentionally stateless in the meantime.
  Needs a durable conversation/message model end to end.
- **Frontend** — one real flow ships: paste transcript text, get an
  anonymized LLM summary back. Not yet wired to *live* captured audio/
  transcripts, and there's no conversation history (nothing is persisted).
- **Tests** — `backend/tests/` and root `tests/` overlap and run as two
  separate pytest invocations; these need to merge into one suite.

## Planned

- Dependency upgrades in small batches (Vite, Storybook, TypeScript, React
  Router, Vitest), each reviewed and gated on its own.
- Code-signing (Authenticode/EV certificate) for the Windows EXE release —
  needs a purchased certificate; `release.yml` documents the exact plug-in
  point for it.
- Ongoing removal of dormant code as each area is touched.

## Design principles

Ekko aims for the smallest system that's honest about its limits, not maximum
abstraction. No CQRS, no unit-of-work until a real multi-repository
transaction needs one, no domain wrapper around every string, no
cache/retry/circuit breaker around every call, and no custom framework where
the standard library already does the job.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for conventions and `AGENTS.md` /
`CLAUDE.md` for the agent operating policy.
