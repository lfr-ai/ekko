# OpenSpec in Ekko

This repository uses OpenSpec for behavior-first planning of non-trivial work.

## Repository layout

- `openspec/specs/` — source-of-truth behavior specs
- `openspec/changes/` — in-flight changes (proposal/design/tasks/spec deltas)
- `openspec/changes/archive/` — completed and archived changes
- `openspec/config.yaml` — project-level OpenSpec defaults and rules
- `openspec/schemas/ekko-production/` — production schema and templates

## Runtime and setup

OpenSpec can be used without a global installation:

- `npx --yes @fission-ai/openspec@latest validate --all --strict`

To (re)generate OpenSpec tool integrations for this repository:

- `npx --yes @fission-ai/openspec@latest init . --tools github-copilot,claude,codex --profile core --force`

## Command syntax by tool

- Claude/Codex style: `/opsx:propose`, `/opsx:apply`, `/opsx:archive`
- GitHub Copilot prompt files: `/opsx-propose`, `/opsx-apply`, `/opsx-archive`

## Recommended flow (core profile)

1. `/opsx:explore` (optional)
2. `/opsx:propose <change-name>`
3. `/opsx:apply <change-name>`
4. `/opsx:sync <change-name>`
5. `/opsx:archive <change-name>`

## Expanded flow (optional)

If expanded commands are enabled in your OpenSpec profile:

1. `/opsx:new <change-name>`
2. `/opsx:continue` or `/opsx:ff`
3. `/opsx:apply <change-name>`
4. `/opsx:verify <change-name>`
5. `/opsx:archive <change-name>`

## Ekko production schema

`ekko-production` extends the default spec-driven workflow with an explicit
`review.md` gate before tasks are finalized.

Artifact flow:

`proposal -> specs -> design -> review -> tasks -> apply`

Review focuses on:

- Security and trust boundaries
- Architecture boundary compliance
- Testing strategy and regression coverage
- Performance/reliability and operability impacts

## Authoring standards

- Keep specs behavior-focused and testable.
- Use requirement deltas under `ADDED`, `MODIFIED`, and `REMOVED`.
- Keep implementation details in `design.md` and `tasks.md`.
- Keep each change focused to one logical unit of work.

## Validation standard

Before archive (and in CI), validate OpenSpec artifacts with strict mode:

- `npx --yes @fission-ai/openspec@latest validate --all --strict`
- `npx --yes @fission-ai/openspec@latest schema validate ekko-production`
