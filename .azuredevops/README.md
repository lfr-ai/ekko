# Azure DevOps policy and pipeline governance

This folder provides an Azure DevOps-ready CI and Renovate baseline for a
frontend-first TypeScript repository.

## Goals

- Enforce consistent quality gates before merge.
- Keep dependency automation aligned with `renovate.json`.
- Keep policy files versioned as code.

## Files

| Path | Purpose |
| --- | --- |
| `pipelines/ci.yml` | Frontend CI (lint, typecheck, unit tests, build, optional Storybook checks) |
| `pipelines/renovate.yml` | Scheduled Renovate execution |
| `variables/ci.yml` | Shared CI variables |
| `variables/renovate.yml` | Shared Renovate variables |
| `templates/steps/setup-node.yml` | Node.js setup |
| `templates/steps/install-frontend.yml` | Bun installation + dependency install |
| `templates/steps/frontend-quality.yml` | Frontend quality gate step group |
| `policies/build-validation-main.json` | Build validation policy template for `main` |
| `policies/required-reviewer-main.json` | Required reviewer policy template for `main` |

## Notes

- Policy JSON files contain placeholders and must be updated with real IDs before applying.
- `ci.yml` is intentionally frontend-focused and can be extended with backend jobs when needed.
- Keep this folder project-agnostic (no repository-specific hardcoded names/IDs).
