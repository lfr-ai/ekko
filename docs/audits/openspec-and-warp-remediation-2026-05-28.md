# OpenSpec + Warp Remediation Audit (2026-05-28)

## Scope

- Implement practical, repository-local OpenSpec usage.
- Remove Warp-specific workflow assets and references from active tooling/docs.
- Keep MCP and agent-governance alignment intact.

## Research basis

Validated against official OpenSpec documentation:

- `getting-started.md` (repo structure, artifact model)
- `commands.md` (core and expanded workflow commands)
- `workflows.md` (actions-not-phases model and best practices)
- `opsx.md` (OPSX profile behavior and project configuration)
- `concepts.md` (specs as source of truth, changes as deltas)

## Implemented changes

### 1) OpenSpec repository implementation

Added `openspec/` with concrete project artifacts:

- `openspec/config.yaml`
- `openspec/README.md`
- `openspec/specs/platform/spec.md`
- `openspec/changes/README.md`
- `openspec/changes/archive/README.md`

Behavioral expectations were established in baseline specs (local runtime,
PII scrubbing before model calls, and health visibility).

### 2) Governance and instruction alignment

Updated policy/instruction sources to enforce OpenSpec-first planning for
non-trivial work:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/skills/openspec/SKILL.md`

### 3) Task automation cleanup

Updated `Taskfile.yml`:

- Removed Warp install task and related setup/status references.
- Reworked `tools:openspec:validate` to validate actual OpenSpec scaffolding
  (`openspec/config.yaml`, `openspec/specs/`, `openspec/changes/`).

### 4) Warp removal

Removed all tracked Warp assets:

- Deleted `.warp/**` (all project Warp config/workflow files)
- Deleted `scripts/install/install-warp.zsh`
- Removed leftover `.warp` ignore reference in `docker/.dockerignore`
- Replaced/remediated Warp mentions in active docs (`README.md` and touched
  audit references)

## Validation snapshot

- Workspace text search shows no remaining `.warp` or Warp task references.
- Diagnostics run on changed files report no active errors after remediation.

## Notes

Historical audit documents may reference prior state by date. Where actively
touched in this remediation, references were updated to avoid presenting Warp as
an active project dependency.
