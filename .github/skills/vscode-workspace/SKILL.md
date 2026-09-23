---
name: vscode-workspace
description: 'Conventions for the committed `.vscode/` workspace: settings vs personal preferences, standard tasks.json/launch.json entries, MCP manifest, and extension recommendations. Use when adding a VS Code task/launch config, scaffolding a new repo''s `.vscode/`, or reviewing editor-config drift.'
---

# VS Code Workspace Skill

`.vscode/` is committed, shared editor configuration — every file in it must be
portable across contributors and safe to run unattended by an agent. Personal
cosmetics never belong here.

## File roles

| File | Committed? | Purpose |
| --- | --- | --- |
| `settings.json` | Yes | Enforced, objective settings: formatters, linters, language-server/analysis, rulers, file/search excludes, chat/skill discovery. No machine paths, no secrets, no cosmetics. |
| `settings.example.jsonc` | Yes | Copy-paste template for personal preferences (theme, panel layout, terminal profile, Copilot ghost-text toggles). Never auto-applied. |
| `tasks.json` | Yes | Thin wrappers around `Taskfile.yml` targets (`command: "task <name>"`) plus a few directly-scoped dev-loop tasks (current file/test). Never duplicate Task's logic inline. |
| `launch.json` | Yes | Debug configurations for the app entrypoint, the active test file, the active file, and remote attach. |
| `mcp.json` | Yes | MCP server manifest for VS Code (mirrors `.claude/mcp.json` — see `agent-config` skill for parity rules). |
| `extensions.json` | Yes | Recommended extensions only, and only for tooling this repo actually uses; never `"unwantedRecommendations"` for personal taste. |
| `keybindings.json` | Yes | Only bindings the whole team should share (rare); personal bindings live in user keybindings. |

## Language servers & editor analysis

`settings.json` also owns the **language-server / editor-analysis** layer so
every contributor gets identical diagnostics, and the editor never fights what
CI owns:

- **One server per language, pinned and explicit.** Recommend it in
  `extensions.json` so everyone runs the same LSP, and make interpreter/root
  discovery deterministic (point at the project venv/root; run commands through
  the package manager) instead of trusting cwd auto-detection.
- **Python** — `ty` owns type diagnostics; Ruff's native language server is the
  single linter/formatter/import-organizer (`source.fixAll` +
  `source.organizeImports` on save). Do not run a second Python formatter beside it.
- **JS/TS/CSS** — Biome's language server is the single formatter/linter/import
  organizer (`quickfix.biome`, `source.organizeImports.biome` on save); the
  TypeScript server owns type diagnostics.
- **No duplicate checkers.** Never let two servers format the same file. No
  machine paths or secrets — use `${workspaceFolder}`-relative values.

## `tasks.json` — the "standard" set

Every backend (or full-stack) repo's `tasks.json` should cover these
categories, each a one-line wrapper around the matching Taskfile target so the
logic lives in exactly one place:

| Category | Label | Wraps |
| --- | --- | --- |
| Build/format | `format`, `lint`, `typecheck` | `task format`, `task lint`, `task typecheck` |
| Architecture | `architecture` | `task architecture` (see `clean-architecture` skill) |
| Quality gate | `check (pre-commit)` | `task pre-commit`, `task check` |
| Spec | `spec: validate` | `openspec validate --all` |
| Test | `test`, `test: current file` | `task test`, per-file pytest/vitest invocation |
| Run | `dev` | `task dev` (mark `isBackground: true`) |
| DB | `db: migrate`, `db: new revision` | `task db:migrate`, `task db:revision -- "..."` (use an `inputs` prompt for the message) |

Never inline a raw shell command that duplicates a Taskfile target — wrap the
task instead, so a change to the underlying command (e.g. swapping a flag)
only needs editing in one file. The few genuine exceptions are dev-loop tasks
scoped to the *active editor file* (`${file}`/`${relativeFile}`), which have
no fixed Taskfile equivalent by design.

Conventions:

- `group: "build"` for gate/quality tasks, `group: "test"` for test tasks —
  lets `Ctrl+Shift+B` / the Test Explorer run the right default.
- `presentation.panel: "shared"` for quick checks (format/lint/typecheck);
  `"dedicated"` for anything a developer watches output from end-to-end
  (test, db migration, `dev`).
- `isBackground: true` for anything that doesn't exit (`dev`, a dev server) —
  otherwise VS Code waits for exit before marking the task done.
- Empty `problemMatcher: []` is fine for tasks whose output is read by a
  human; attach `$python`/`$tsc` only when you want inline Problems-panel
  diagnostics from the task's own output.

## `launch.json` — the standard set

- **App entrypoint** — launch the actual app factory/dev server
  (`uvicorn <package>.composition.app_factory:create_app --factory --reload` for
  FastAPI, `bun run dev` + `chrome`/`msedge` request type for the Vite frontend).
- **Debug current test file** — `module: "pytest"`, `args: ["${relativeFile}",
  "-v"]` (Python) or a Vitest launch config scoped to `${relativeFile}` (frontend).
- **Debug current file** — `program: "${file}"` for a quick throwaway script.
- **Attach to running process** — remote-debugpy attach (`"request":
  "attach"`, a fixed `connect.port`) for a process started outside VS Code.

Every Python configuration sets `envFile` to the project's `.env` and adds
`PYTHONPATH` pointing at `backend/src` — otherwise imports resolve
differently under the debugger than under `uv run`.

## Adding a new task or launch config

1. Does a `Taskfile.yml`/`tasks/*.yml` target already exist? If not, add it
   there first (single source of truth) — see the `backend-structure` skill.
2. Add the `.vscode/tasks.json` entry as a thin wrapper.
3. Pick the right `group`/`presentation`/`problemMatcher` from the tables above.
4. Validate with `get_errors` on the JSON/JSONC file — VS Code's schema
   catches most authoring mistakes immediately.

## Verification

There is no dedicated guard script — `tasks.json`/`launch.json` are validated
structurally by VS Code's own JSON schema (surfaced through `get_errors`) and
functionally by actually running the task (`task <name>` in a terminal is the
same command the `.vscode/tasks.json` entry invokes).
