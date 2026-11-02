---
paths:
  - ".azuredevops/**/*.yml"
  - ".azuredevops/**/*.yaml"
  - ".github/workflows/*.yml"
  - ".github/workflows/*.yaml"
  - "**/azure-pipelines*.yml"
---

# CI/CD pipeline conventions

Read the active CI system from `PROJECT.md` (this repo: Azure DevOps under
`.azuredevops/` — see its `README.md`). Keep pipeline YAML minimal, pinned, and
aligned with the local task gates.

## Alignment with local gates

- A pipeline runs the same checks the local loop runs — do not invent a CI-only
  lint/test path. Mirror the declared task-runner targets (tests, lint/format,
  type-check, pre-commit) so a green local run means a green CI run.
- When you add or rename a local check (a task-runner target or a pre-commit
  hook), update the pipeline that runs it in the same change-set.

## Safety

- Never inline a secret, token, PAT, or connection string. Use the CI system's
  secret store / service connection and reference it by name.
- Grant least privilege: scope tokens and job permissions to what the job needs;
  do not request write scope for a read-only job.
- Pin third-party actions/tasks and tool versions (a major version or a commit
  SHA), never a floating `latest`, so a build stays reproducible.
- Restrict what runs for external contributions; never expose secrets to
  fork-triggered runs.

## Structure

- Factor repeated steps into reusable templates (`.azuredevops/templates/`, or a
  composite/reusable workflow) instead of copy-pasting across jobs.
- Keep tunable values (versions, thresholds, cache dirs) in one shared variables
  file, not scattered inline.
- Cache dependency downloads keyed by lockfile hash; keep independent jobs
  parallel and let each fail fast with an obvious failing gate.

## Before finishing

- Validate the YAML (the repo's `yamllint` / pipeline schema) and re-check that
  every gate a reviewer relies on still runs. Update `.azuredevops/README.md`
  (or the workflow's own doc) when you change the gate set.
