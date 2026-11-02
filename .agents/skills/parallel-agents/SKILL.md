---
name: parallel-agents
description: 'Run multiple agent sessions against the same repository concurrently without collisions — isolated git worktrees, derived port/Compose/DB overrides, and shared-file contention. Use when starting a second agent session on the same repo, planning to run agents in parallel, or debugging a port/container-name/log-lock collision between two sessions.'
---

# Parallel Agents Skill

Two different kinds of "parallel agents" need two different answers — pick
the right one before reaching for either:

| Scenario | Answer |
| --- | --- |
| One session, one plan, many mostly-independent tasks fanned out to fresh subagents | `subagent-driven-development` skill — in-process, no worktree, no extra ports |
| Two (or more) independent agent **sessions** working the same repo **at the same time** | This skill — each session needs its own working directory and isolated runtime resources |

This skill covers the second case. It never runs `git` itself — `AGENTS.md`
Hard Rule 11 forbids agents from executing `git`; the operator (human) creates
and removes every worktree.

## Choose the isolation that matches the work

Code isolation (where file edits land) and runtime isolation (which ports,
containers, and databases a running stack uses) are separate concerns:

| Mechanism | Isolates | Reach for it when |
| --- | --- | --- |
| **Native worktree session** (VS Code Agents window → New Worktree) | Working files + branch, in a dedicated agent-host process | Independent code tasks run in parallel on a runtime that supports it — the default |
| **Dev Container session** | Files + OS-level dependencies/tools; the agent runs inside the container | You also need runtime/tool isolation or command sandboxing |
| **Manual git worktree + `new_agent_worktree.py`** | Working files + derived port/Compose/DB env | Any runtime (e.g. a CLI harness), or when parallel stacks must actually *run* |
| **Separate session, same folder** | Conversation only (not files) | Read-only investigation alongside one editing session |

Native worktrees and the runtime-env script **compose**: the worktree isolates
files; the script isolates the running stack.

## Native worktree sessions (agent host)

On a runtime with built-in worktree sessions (VS Code's Agents window), this is
the fastest, safest default — no manual `git`, no babysitting:

- Start each parallel task as its own session with **New Worktree** selected;
  each runs in a **dedicated agent-host process**, so one session can't block
  another. Sessions on the legacy shared extension host contend for one
  process — a common cause of a session "stalling" while another is busy.
- Worktree sessions apply changes to a separate branch and working directory
  and run with tool approvals pre-granted, so a background session runs to
  completion without pausing for confirmation.
- A fresh worktree starts from committed state and does **not** carry
  git-ignored files (env files, installed dependencies). Set
  `git.worktreeIncludeFiles` to globs VS Code copies into every new worktree — a
  file is copied only when it matches **and** is git-ignored (e.g.
  `[".env", "node_modules/**"]`) — or run onboarding inside the worktree. Scope
  it to what the session can safely access: carry the local dev `.env`, never an
  environment-specific production-secret file.
- Integrate by reviewing each session's branch on its own, then merging back.

## Why a shared checkout isn't enough

Two sessions in the **same working directory** collide on:

- **Uncommitted changes** — one session's in-progress edit is another's
  "unexpected diff".
- **The dev server port** — a fixed application port means the second `task
  start` either fails to bind or silently talks to the first session's process.
- **The Compose project** — a fixed Compose `name:` shares containers, volumes,
  and networks, so two stacks stomp on each other's database state.
- **Log/lock files** — anything written to a fixed path interleaves between
  sessions.

A worktree solves the first collision; the other three need explicit runtime
isolation.

## Setting up a session on any runtime

1. **The operator** (never the agent) creates the worktree and its isolated
   environment overrides in one step:

   ```shell
   uv run python .agents/skills/parallel-agents/scripts/new_agent_worktree.py \
     <branch-name> --port-env-var APP_PORT --db-name-env-var POSTGRES_DB
   ```

   This creates `../<repo>-<branch-slug>/` as a new worktree and writes a
   `.env.local` inside it with:
   - `COMPOSE_PROJECT_NAME=<branch-slug>` — a distinct Compose project, so
     containers/volumes/networks never collide with the primary worktree.
   - `<port-env-var>=<derived port>` — a stable, deterministic port derived
     from the branch name (never the primary worktree's port).
   - `<db-name-env-var>=<branch-slug-with-underscores>` — a distinct database
     name so migrations/tests never touch the primary worktree's data.

   Adjust `--port-env-var`/`--db-name-env-var` to the project's actual
   environment variable names (see `.env.example`); defaults are generic
   (`APP_PORT`/`POSTGRES_DB`) for reuse in other projects. A native worktree
   session can run the script afterward to add the runtime-env overrides.

2. In the new worktree, run the project's normal onboarding (`task onboard`
   or equivalent) to fill in secrets `.env.local` doesn't carry, then
   `uv sync` (or the frontend equivalent) — a worktree does **not** share a
   virtual environment or `node_modules` with the primary checkout.
3. Point the second agent session's working directory at the new worktree.
   From here it behaves like any single-session repo — its own `.venv`, its
   own port, its own Compose stack.

## Keep parallel sessions fast and stall-free

Independent of isolation, these keep concurrent sessions responsive:

- **Prefer an agent-host session over the legacy shared extension host** — a
  dedicated per-session process is not blocked by a busy extension or a sibling
  session's tool call.
- **Don't eagerly connect MCP servers.** A large always-on server set multiplies
  process-startup cost per session and can stall a turn *before the first file
  edit* — especially a server pointed at a dev endpoint that isn't running (a
  connection timeout). Start servers lazily (VS Code: `chat.mcp.autostart:
  never`) and scope each agent profile's `tools:` to the servers it needs, so a
  session stays under the tool-catalog ceiling.
- **Work off a cloud-synced folder.** A checkout under OneDrive/Dropbox/iCloud
  pays sync + antivirus I/O on every cold dependency spawn and can mutate the
  worktree mid-session; a plain local path is markedly faster and avoids
  transient false-positive failures.

## What still needs care even with isolated worktrees

- **Shared remote state** — both sessions push to the same remote and can
  still open conflicting PRs against the same base branch; that coordination
  is a human decision, not something environment isolation solves.
- **Shared external resources** — a shared cloud dev database, a shared cloud
  resource, or a shared MCP server session are outside worktree isolation
  entirely; coordinate, or provision a second instance.
- **Guards run per-worktree** — each worktree has its own code-graph index and
  guard state; run the analyze/guard steps independently in each — they are
  read-only/local and never collide across worktrees.
- **Merging back** — the operator merges each worktree's branch normally;
  removing the worktree afterward (`git worktree remove <path>`) is also
  operator-only.

## References

- [Choose and use an agent harness](https://code.visualstudio.com/docs/agents/run/agent-harnesses) — native worktree vs folder isolation and the permission level each uses.
- [Delegate two tasks without mixing their changes](https://code.visualstudio.com/docs/agents/guides/delegate-two-tasks) — the end-to-end two-worktree parallel workflow.
- [VS Code Agent Host](https://code.visualstudio.com/docs/agents/concepts/agent-host) — why a dedicated per-session process isn't blocked by busy extensions.
- [Git worktree documentation](https://git-scm.com/docs/git-worktree) — the underlying primitive the script wraps.
- [Git branches and worktrees in VS Code](https://code.visualstudio.com/docs/sourcecontrol/branches-worktrees) — the `git.worktreeIncludeFiles` / `git.detectWorktrees` settings and the Create / Migrate / Remove Worktree commands.
- [Docker Compose project name](https://docs.docker.com/compose/how-tos/project-name/) — why `COMPOSE_PROJECT_NAME` isolation is required per worktree.
