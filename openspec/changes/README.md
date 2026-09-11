# OpenSpec Changes

Create one folder per in-flight change under this directory.

Example:

- `openspec/changes/add-feature-x/`
  - `proposal.md`
  - `design.md`
  - `review.md`
  - `tasks.md`
  - `specs/<domain>/spec.md` (delta specs)

Archive completed changes under `openspec/changes/archive/`.

## Current status

- In-flight changes: none
- Archived changes: see `openspec/changes/archive/README.md`

## Quality gate before archive

- Validate all artifacts in strict mode:
  - `npx --yes @fission-ai/openspec@latest validate --all --strict`
