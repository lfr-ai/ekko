---
name: release-management
description: Prepare and verify a SemVer release with Commitizen, Conventional Commits, and Keep a Changelog. Use when choosing a version bump, updating release notes, or preparing a tag while keeping Git operations manual.
---

# Release management

## Workflow

1. Read the manifest version provider, Commitizen configuration (`.cz.toml`/
   `pyproject.toml [tool.commitizen]`), `CHANGELOG.md`, and CI release rules.
   Never infer the release mechanism from installed CLIs.
2. Classify the public impact using SemVer:
   - patch: backward-compatible fix;
   - minor: backward-compatible capability;
   - major: breaking public contract or required migration.
3. Confirm Conventional Commit history supports the intended bump. Do not hide a
   breaking change behind a patch/minor label.
4. Update `[Unreleased]` in `CHANGELOG.md` using terse Added/Changed/Fixed/Removed
   entries. Include migrations or operator actions.
5. Use `task bump-cz` / `task changelog-cz` (Commitizen). Verify all declared
   version files stay synchronized and generated changelog changes are reviewed.
6. Run the full quality gate (`task check`) and build validation before handing off.
7. Report the proposed version, artifacts, migration notes, and exact manual Git
   steps without executing Git (AGENTS.md Hard Rule 11: no `git` commands by agents).

## Guardrails

- Agents never branch, commit, tag, push, or rewrite history.
- Do not publish from an unverified or dirty working state.
- Never edit old release entries to conceal a regression; add a corrective entry.
- Keep release automation credentials outside the repository.
- One authoritative version provider; no duplicated hand-maintained versions.
