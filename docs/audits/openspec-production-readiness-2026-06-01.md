# OpenSpec Production Readiness Review (2026-06-01)

## Objective

Perform an exhaustive review of OpenSpec usage in the Ekko repository, benchmark
against current upstream OpenSpec guidance, and implement a production-ready
spec-driven development setup.

## Method

### Repository review

Inspected:

- OpenSpec artifacts (`openspec/config.yaml`, `openspec/specs`, `openspec/changes`)
- Governance docs (`AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `.github/copilot-instructions.md`)
- Automation (`Taskfile.yml`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`)
- Agent integration footprint (`.github/prompts`, `.github/skills`, `.claude`, `.codex`)

### External references (web)

Benchmarked against current OpenSpec upstream documentation:

- https://openspec.dev
- https://github.com/Fission-AI/OpenSpec
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/README.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/getting-started.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/commands.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/workflows.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/opsx.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/cli.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/customization.md
- https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/supported-tools.md

## Findings

### Strengths already present

1. OpenSpec repository scaffold existed and was coherent.
2. Baseline platform spec existed under `openspec/specs/platform/spec.md`.
3. Governance documents already emphasized OpenSpec-first planning.
4. Task automation already had scaffold validation.

### Gaps identified

1. Validation depth was scaffold-only (existence checks), not artifact/schema strictness.
2. CI pipeline had no OpenSpec validation gate.
3. No production-tailored schema with explicit pre-implementation quality gate.
4. Tool integration artifacts for Copilot/Claude/Codex were not generated.
5. Command syntax ambiguity existed for Copilot prompt syntax (`/opsx-...`) vs colon form (`/opsx:...`).

## Implemented remediation

### 1) Tool integrations generated

Executed non-interactive OpenSpec initialization for active tools:

- GitHub Copilot
- Claude Code
- Codex

Generated assets include:

- `.github/prompts/opsx-*.prompt.md`
- `.github/skills/openspec-*/SKILL.md`
- `.claude/commands/opsx/*`
- `.codex/skills/openspec-*/SKILL.md`

### 2) Production schema introduced

Added custom schema:

- `openspec/schemas/ekko-production/schema.yaml`
- `openspec/schemas/ekko-production/templates/{proposal,spec,design,review,tasks}.md`

Key enhancement: explicit `review` artifact before `tasks`, enforcing a
pre-implementation quality gate (security, architecture, testing,
performance/reliability, docs/operability).

### 3) Project config upgraded

Updated `openspec/config.yaml`:

- Default schema switched from `spec-driven` to `ekko-production`
- Rules strengthened for proposal/design/tasks
- New rules added for `review` artifact

### 4) Automation and CI hardened

`Taskfile.yml`:

- `tools:openspec:validate` now performs:
  - scaffold checks
  - strict OpenSpec artifact validation
  - schema validation for `ekko-production`
- Added:
  - `tools:openspec:init`
  - `tools:openspec:update`

`.github/workflows/ci.yml`:

- Added `openspec-validation` job running:
  - `validate --all --strict`
  - `schema validate ekko-production`
- Included the job in `all-green` requirements.

### 5) Documentation + governance alignment

Updated:

- `openspec/README.md`
- `openspec/changes/README.md`
- `README.md`
- `CONTRIBUTING.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`

Added:

- concrete bootstrap/update/validation commands
- schema expectations
- Copilot syntax note (`/opsx-...`)
- production workflow guidance

## Validation evidence

### Command validation

- `npx --yes @fission-ai/openspec@latest validate --all --strict` → passed

### Setup validation

- OpenSpec init completed for configured tools and generated expected artifacts.

## Residual risks and recommendations

1. **Generated prompt/skill drift**
   - Re-run `task tools:openspec:update` after OpenSpec CLI upgrades.
2. **Schema governance drift**
   - Validate schema changes in CI (already added).
3. **Adoption risk**
   - Enforce usage in PR reviews for non-trivial changes (process discipline).
4. **Legacy command ambiguity**
   - Prefer OPSX commands and document tool-specific command form in review templates.

## Suggested next increment

1. Add a lightweight PR checklist item requiring OpenSpec change links for
   non-trivial PRs.
2. Add optional periodic audit task to detect stale active changes
   (`openspec list --json` and age thresholds).
3. Add reference examples in `openspec/specs/` for 2–3 core domains beyond
   platform baseline.

## Conclusion

The repository is now significantly closer to a state-of-the-art,
production-ready OpenSpec setup:

- Tool integrations are active
- Workflow is codified for contributors
- Validation is automated locally and in CI
- Schema is customized for Ekko's quality bar
- Governance documentation is aligned with implementation
