# Toolchain metafiles — what reads what

Loaded on demand from `quality-gate/SKILL.md`. A repository's root is full of
small, single-purpose config files that each own exactly one tool's behavior.
Read the relevant file before changing behavior in prose (a skill, an
instruction, or a docstring) — never restate or duplicate a threshold,
version pin, or rule list that already lives in one of these, since the two
copies will drift the moment only one of them is edited.

## Common categories and their file

| Category | Typical file(s) | Owns |
| --- | --- | --- |
| Package + tool manifest | `pyproject.toml` / `package.json` | Dependencies, build metadata, and often nested tool config (`[tool.*]` tables) |
| Lockfile | `uv.lock`, `poetry.lock`, `bun.lock`, `package-lock.json` | Exact resolved dependency versions — never hand-edited |
| Linter / formatter | `ruff.toml`, `.eslintrc*`, `biome.json` | Rule selection, per-file ignores, target version |
| Type checker | `ty.toml`, `mypy.ini`, `tsconfig.json` | Strictness, included paths, target Python/TS version |
| Security / dependency scan | `bandit.toml`, `.trivyignore`, `renovate.json` | Static-analysis rule selection; automated dependency-update policy |
| Spell check | `cspell.json` | Project-specific word allowlist for prose/docs linting |
| Duplication detection | `jscpd.json` | Clone-detection thresholds and ignore globs (see the `jscpd` skill) |
| Task runner | `Taskfile.yml`, `Makefile`, npm `scripts` | Named commands that wrap the real tool invocations — the single source of truth for "how do I run X" |
| Test runner config | `pytest.ini`, `tox.ini`, `vitest.config.*` | Test discovery, markers, coverage thresholds |
| Pre-commit orchestration | `.pre-commit-config.yaml` | Which hooks run, in what order, on which file patterns, and at which git stage |
| Migration tool | `alembic.ini` + `alembic/env.py` | Migration-runner wiring (script location, URL resolution) — the migrations themselves live under `alembic/versions/` |
| Container build | `Containerfile` / `Dockerfile`, `.dockerignore` | Build stages, base image, and what is excluded from the build context |
| Container orchestration | `compose.yaml` + overrides | Local multi-service wiring, profiles, and environment inputs |
| Reverse proxy | `Caddyfile` (or `nginx.conf`) | Routing, TLS termination, security headers |
| CI/CD | `.github/workflows/*.yml`, `azure-pipelines.yml` | Pipeline triggers, stages, and required gates |

## Adding a new tool

1. Add its config file at the repo root (or the tool's documented location) —
   do not inline its settings into a skill, instruction, or script.
2. Wire it into the task runner (`Taskfile.yml` entry) and, if it should block
   a commit, `.pre-commit-config.yaml` — so `task check` / `pre-commit run`
   stays the single entry point `quality-gate` already assumes.
3. Update this table with the new category/file pair only if the tool
   introduces a genuinely new category; do not duplicate its rule set here.

## Pre-commit hook conventions

- One hook per tool; `id` matches the tool name, not a generic label.
- Prefer the tool's own `language: system`/`repo: local` entry when the
  project already depends on it (via `uv`/`bun`) over a mirrored pre-commit-hooks
  fork, so there is one installed version, not two.
- Scope a hook with `files`/`types` instead of running it repo-wide when it
  only applies to one file family (e.g. a markdown linter should not run over
  `.py` files).
- A hook that needs network access (e.g. a link checker, or an on-demand
  `bunx`-based linter) is a candidate for a manual Task target instead of an
  always-on pre-commit stage — keep the committed gate fast and offline-safe.
