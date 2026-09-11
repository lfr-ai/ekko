# Proposal: Minimal platform tooling baseline

## Why

Platform configuration quality is currently strong, but exhaustive structural
review revealed concrete gaps in coverage gating,
commitizen tracking, prompt registry structure, agent policy depth, and
pre-commit hook surface. These gaps must be closed to reach production-ready
parity.

## What changes

1. Add diff-cover gate to tox coverage environment and dev dependencies.
2. Add `version_files` to `.cz.toml` commitizen configuration.
3. Confirm prompt registry experimental-mode architecture is coherent.
4. Expand AGENTS.md hard rules to the approved policy depth and explicitness.
5. Align pre-commit local hook naming with repository conventions.
6. Define minimal Codecov policy expectations as behavior requirements.
7. Define minimal CodeRabbit policy expectations with architecture/security focus.
8. Confirm Keploy usage via stable task wrappers.
9. Confirm minimal observability stack behavior (Prometheus/Grafana/OTel).
10. Define the `.env.example` inclusion/exclusion policy.
11. Confirm agentic/MCP parity contract for `.mcp.json` and `.vscode/mcp.json`.
12. Confirm GitNexus index-readiness precondition for graph workflows.
13. Confirm Clean Architecture boundary enforcement tooling.
14. Ensure documentation is minimal, professional, emoji-free.

## Scope

- Config, tooling, and documentation alignment.
- OpenSpec spec artifacts.
- No domain/application/infrastructure code changes.

## Non-goals

- Refactoring product code or domain logic.
- Introducing tools not present in either baseline.
- Renaming packages (e.g. `config/` to `configs/`) without explicit decision.

## Success criteria

- All new requirements have concrete, testable scenarios.
- Tox coverage env includes diff-cover with explicit threshold.
- `.cz.toml` includes `version_files`.
- AGENTS.md hard rules match the approved policy depth.
- Pre-commit hook naming is consistent.
- Platform standard is implementable via a separate `/opsx-apply` change.
