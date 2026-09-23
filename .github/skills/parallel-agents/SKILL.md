---
name: parallel-agents
description: 'Run multiple agent sessions against the same repository concurrently without collisions — isolated git worktrees and derived port/env overrides. Use when starting a second agent session on the same repo, planning to run agents in parallel, or debugging a port/log-lock collision between two sessions.'
---

# Parallel Agents Skill

Two different kinds of "parallel agents" need two different answers — pick
the right one before reaching for either:

| Scenario | Answer |
| --- | --- |
| One session, one plan, many mostly-independent tasks fanned out to fresh subagents | `subagent-driven-development` skill — in-process, no worktree, no extra ports |
| Two (or more) independent agent **sessions** (two Copilot/Claude windows, or a human plus an agent) working on the same repo **at the same time** | This skill — each session needs its own git worktree and its own isolated runtime resources |

This skill covers the second case only. It never runs `git` itself — AGENTS.md
Hard Rule 11 forbids agents from executing `git`; every worktree is created by
the operator (human).

## Why a shared checkout isn't enough

Two agent sessions in the **same working directory** collide on:

- **Uncommitted changes** — one session's in-progress edit is another
  session's "unexpected diff"; neither has isolation from the other's file
  writes.
- **The dev server ports** — fixed backend (`8000`) / frontend (`5173`) ports
  mean the second `task dev` either fails to bind or silently talks to the
  first session's process.
- **The local database file** (e.g. a SQLite file such as `backend/<project>.db`)
  — two sessions running
  Alembic migrations or tests against the same file corrupt each other's state.
- **Log/lock files** — anything written to a fixed path (e.g.
  `logs/copilot/tool-guardian/guard.log`) interleaves between sessions.

A git worktree solves the first problem (each session gets its own working
directory, same repository, no branch-switch conflicts) but not the other two
by itself — those need explicit environment isolation.

## Setting up a second session (operator steps)

1. **The operator** (never the agent) creates a new worktree:
   `git worktree add ../<repo>-<branch-slug> <branch-name>`.
2. In the new worktree, copy `.env.local` and override the isolation-sensitive
   variables: a distinct backend/frontend dev port pair, and a distinct
   database path (e.g. `backend/<repo>-<branch-slug>.db`, see `PROJECT.md`
   for the exact env var names) so migrations
   and tests never touch the primary worktree's data.
3. Run `task install` in the new worktree — a worktree does **not** share a
   virtual environment or `node_modules` with the primary checkout.
4. Point the second agent session's working directory at the new worktree.
   From here it behaves like any single-session repo — its own `.venv`, its
   own ports, its own database file.

## What still needs care even with isolated worktrees

- **Shared remote state** — both sessions push to the same remote and can
  still open conflicting PRs against the same base branch; that coordination
  is a human decision, not something environment isolation solves.
- **GitNexus/agent-config checks run per-worktree** — each worktree has its
  own `.gitnexus/` index; refresh it (`gitnexus analyze`) in each if the graph
  is used — these are read-only/local and never collide across worktrees.
- **Merging back** — the operator merges each worktree's branch normally;
  removing the worktree afterward (`git worktree remove <path>`) is also
  operator-only.

## References

- [Git worktree documentation](https://git-scm.com/docs/git-worktree) — official reference for the underlying primitive this skill wraps.
