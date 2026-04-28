# uv Migration Agent

Purpose: automated guidance & steps for migrating this repository from PDM to Astral 'uv'.

Checklist:
- Ensure local machine/CI can run `uv` (install via `astral-sh/setup-uv` or installer)
- Run `./scripts/migrate_to_uv.sh` to run `uv sync --all-extras` and create `uv.lock`
- Commit `uv.lock` to the repository
- Update CI cache keys to reference `uv.lock` where applicable
- Run `uvx pre-commit run --all-files` and fix any hook failures
- Remove `pdm.*` workflow steps once `uv.lock` is committed and CI proves green

Notes:
- Keep `pdm.lock` in the repo as an optional fallback for users who prefer PDM until migration is fully validated.
- This agent is informational — it does NOT change files itself; follow steps interactively.
