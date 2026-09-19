---
paths:
  - ".github/workflows/*.yml"
  - ".github/workflows/*.yaml"
---

# CI/CD pipeline conventions

This repo's CI is GitHub Actions under `.github/workflows/` (`ci.yml`,
`security.yml`, `codeql-analysis.yml`, `playwright.yml`, `scorecard.yml`,
`deploy-container-apps-acr.yml`). Keep workflow YAML minimal, pinned, and
aligned with the local Taskfile gates.

## Alignment with local gates

- A workflow runs the same checks the local loop runs (`task check`) — do not
  invent a CI-only lint/test path. Mirror the declared Taskfile targets (tests,
  lint/format, type-check, architecture) so a green local run means a green CI run.
- When you add or rename a local check (a Taskfile target or a pre-commit
  hook), update the workflow that runs it in the same change-set.

## Safety

- Never inline a secret, token, or connection string. Use GitHub Actions
  secrets/environments and reference them via `${{ secrets.NAME }}`.
- Grant least privilege: scope the workflow/job `permissions:` block to what
  the job needs; do not request `write` scope for a read-only job.
- Pin third-party actions to a major version or a commit SHA, never a floating
  `@main`/`@master`, so a build stays reproducible.
- Restrict what runs for external contributions (`pull_request_target` needs
  extra care); never expose secrets to fork-triggered runs.

## Structure

- Factor repeated steps into a reusable/composite workflow instead of
  copy-pasting across jobs.
- Keep tunable values (tool versions, thresholds, cache dirs) in one place
  (workflow `env:` or a shared step), not scattered inline across jobs.
- Cache dependency downloads keyed by lockfile hash (`uv.lock`, `bun.lock`);
  keep independent jobs parallel and let each fail fast with an obvious
  failing gate.

## Before finishing

- Validate workflow YAML (`actionlint` or the editor's schema) before
  committing.
- Confirm the workflow's job graph matches what actually needs to run for the
  changed paths (`paths:`/`paths-ignore:` filters).
