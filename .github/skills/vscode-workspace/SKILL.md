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
| `mcp.json` | Yes | MCP server manifest for VS Code (mirrors `.claude/settings.json`'s `allowedMcpServers`/`.mcp.json` — see `agent-config` skill for parity rules). |
| `extensions.json` | Yes | Recommended extensions only; never `"unwantedRecommendations"` for personal taste. |
| `keybindings.json` | Yes | Only bindings the whole team should share (rare); personal bindings live in user keybindings. |

## Language servers & editor analysis

`settings.json` also owns the **language-server / editor-analysis** layer so
every contributor and the dev container get identical diagnostics, and the
editor never fights what CI owns:

- **One server per language, pinned and explicit.** Recommend it in
  `extensions.json` so everyone runs the same LSP, and make interpreter/root
  discovery deterministic (point at the project venv/root; run commands through
  the package manager) instead of trusting cwd auto-detection.
- **Python** — the project's type checker and its server (e.g. Astral `ty`) own
  type diagnostics; Ruff's native language server is the single
  linter/formatter/import-organizer (`source.fixAll` + `source.organizeImports`
  on save). Do not run a second Python formatter beside it.
- **JS/TS/CSS** — Biome's language server is the single formatter/linter/import
  organizer (`quickfix.biome`, `source.organizeImports.biome` on save); the
  TypeScript server (`vtsls` or the built-in `tsserver`) owns type diagnostics.
- **No duplicate checkers.** Never let two servers format the same file, and
  scope redundant editor typechecking to open files when CI owns the whole
  project. No machine paths or secrets — use `${workspaceFolder}`-relative values.

## Agent, model & harness defaults

`settings.json` also owns the committed **chat/agent** layer: repository
instructions, hooks, MCP startup posture, the default-model seed, and harness
posture. Personal risk/ergonomics choices (permission default, notifications,
session cleanup) belong in **user** settings, kept consistent with these.

- **Prefer the Copilot Agent Host** harness: each session runs in its own
  process (not blocked by a busy extension) and unlocks worktree/Dev-Container
  isolation and background/parallel sessions — the fix for shared-extension-host
  stalls (see `parallel-agents`). The built-in **Local** harness is only for an
  extension-contributed tool or a VS Code-configured/BYOK model, and VS Code has
  marked it for removal ("the Local agent will be removed in a future release",
  AI settings reference) — don't build on it.
- **Startup:** `chat.mcp.autostart: "never"` disables VS Code's proactive MCP
  autostart pass — no startup storms or dead-server timeouts on the Local/
  extension-host side. It is inert for Agent Host sessions (they start their
  configured servers regardless; trim servers or scope tools per-agent to cut
  that cost). Do not reintroduce deprecated Local-harness discovery settings
  (`chat.promptFilesLocations`, `chat.agentSkillsLocations`); current VS Code
  and Agent Host discover the standard customization trees natively.
- **Context management:** keep auto-compaction on
  (`summarizeAgentConversationHistory.enabled: true`) so a long session
  summarizes earlier history and continues instead of erroring when the context
  window fills, and enable `chat.tools.compressOutput.enabled` (Preview) to
  shrink large terminal output before it reaches the model — both shared agent
  posture in `settings.json`; compact by hand with `/compact`. Session *cleanup*
  (auto-archiving merged-PR sessions after N days) is personal — user settings.
- **Provider toggles are deliberate:** disabling a harness (e.g.
  `claudeAgent.enabled: false`) or `useClaudeMdFile` removes a Session Target or
  dead context — document *why* inline.

## `tasks.json` — the "standard" set

Every backend (or full-stack) repo's `tasks.json` should cover these
categories, each a one-line wrapper around the matching Taskfile target so the
logic lives in exactly one place:

| Category | Label | Wraps |
| --- | --- | --- |
| Build/format | `format`, `lint`, `typecheck` | `task format`, `task lint`, `task typecheck` |
| Architecture | `architecture`, `ports: check` | `task architecture`, `task ports:check` (see `clean-architecture` skill) |
| Quality gate | `guard`, `check (pre-commit)` | `task guard`, `task check` |
| Spec | `spec: validate` | `task spec:validate` |
| Test | `test`, `test: current file` | `task test`, `task test:path -- "${relativeFile}"` |
| Run | `start`, `observability: docker` | `task start`, `task observability:docker` (mark `isBackground: true`) |
| DB | `db: migrate`, `db: new revision` | `task db:migrate`, `task db:revision -- "..."` (use an `inputs` prompt for the message) |

Never inline a raw shell command that duplicates a Taskfile target — wrap the
task instead, so a change to the underlying command (e.g. swapping a flag)
only needs editing in one file. The few genuine exceptions are dev-loop tasks
scoped to the *active editor file* (`${file}`/`${relativeFile}`), which have
no fixed Taskfile equivalent by design (e.g. `ruff: fix current file`).

Conventions:

- `group: "build"` for gate/quality tasks, `group: "test"` for test tasks —
  lets `Ctrl+Shift+B` / the Test Explorer run the right default.
- `presentation.panel: "shared"` for quick checks (format/lint/typecheck/
  guard); `"dedicated"` for anything a developer watches output from
  end-to-end (test, db migration, `start`).
- `isBackground: true` for anything that doesn't exit (`start`,
  `observability: docker`, a dev server) — otherwise VS Code waits for exit
  before marking the task done.
- Empty `problemMatcher: []` is fine for tasks whose output is read by a
  human; attach `$python`/`$tsc` only when you want inline Problems-panel
  diagnostics from the task's own output.

## `launch.json` — the standard set

- **App entrypoint** — launch the actual app factory/dev server
  (`uvicorn <pkg>.main:create_app --factory --reload` for FastAPI, `bun run
  dev` + `chrome`/`msedge` request type for a Vite frontend).
- **Debug current test file** — `module: "pytest"`, `args: ["${relativeFile}",
  "-v"]` (Python) or the framework's per-file invocation (frontend: a Vitest
  launch config scoped to `${relativeFile}`).
- **Debug current file** — `program: "${file}"` for a quick throwaway script.
- **Attach to running process** — remote-debugpy attach (`"request":
  "attach"`, a fixed `connect.port`) for a process started outside VS Code
  (a container, a background task).

Every Python configuration sets `envFile` to the project's `.env` and adds
`PYTHONPATH` pointing at `src` when the project uses a `src/` layout —
otherwise imports resolve differently under the debugger than under `uv run`.

## Adding a new task or launch config

1. Does a `Taskfile.yml`/`package.json` script target already exist? If not,
   add it there first (single source of truth) — see the `backend-structure`
   or `frontend-tooling` skill for the toolchain.
2. Add the `.vscode/tasks.json` entry as a thin wrapper.
3. Pick the right `group`/`presentation`/`problemMatcher` from the tables
   above.
4. Validate with `get_errors` on the JSON/JSONC file — VS Code's schema
   catches most authoring mistakes immediately.

## Scaffolding a new repository

`project-bootstrap` step 5 delegates the concrete `tasks.json`/`launch.json`
shape to this skill. Copy [`assets/tasks.json.template`](assets/tasks.json.template)
and [`assets/launch.json.template`](assets/launch.json.template), then delete
any task/config whose underlying tool the new project doesn't use (e.g. no
`db: migrate` without Alembic, no `observability: docker` without the
Prometheus/Grafana stack).

## Verification

There is no dedicated guard script — `tasks.json`/`launch.json` are validated
structurally by VS Code's own JSON schema (surfaced through `get_errors`) and
functionally by actually running the task (`task <name>` in a terminal is the
same command the `.vscode/tasks.json` entry invokes).
