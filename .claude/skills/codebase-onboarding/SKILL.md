---
name: codebase-onboarding
description: Build or refresh the durable context that agents need to understand an existing repository. Use when starting a new project, onboarding agents, recovering stale architecture knowledge, initializing PROJECT.md/OpenSpec/GitNexus, or deciding what belongs in memory versus documentation.
---

# Codebase onboarding for agents

Create the smallest durable context that lets a new agent answer: what is this
project, how is it built, where does behavior live, why was it designed this way,
and how is a safe change verified?

## 1. Discover before writing

- Read root policy files, lockfiles/manifests, Task/package scripts, source roots,
  tests, deployment/container config, env templates, and existing specs/docs.
- Identify the real project shape and package managers from files, not assumptions.
- Use code intelligence to trace representative entry points and execution flows.
- Do not create a document that duplicates an existing source of truth.

## 2. Refresh project facts

Create or update `PROJECT.md` with only stable project-specific facts:
identity/source roots, package managers, architecture layers, ubiquitous language,
spec/data locations, deployment/CI, and code-intelligence commands. Add explicit
agent-portability tokens used by the configuration guard.

## 3. Build code intelligence

- Discover the GitNexus repository/index and freshness state.
- Run the repository-owned graph/index task after new, renamed, or moved modules.
- Use process/context/impact queries to verify architecture claims; never describe
  a call flow from folder names alone.
- Record the refresh command in `PROJECT.md`, not generated graph inventories in
  human docs.

## 4. Specs and design decisions

- Use OpenSpec for behavioral capabilities and change decisions. Initialize it
  only when the project needs living specifications; do not manufacture specs for
  behavior that has not been verified.
- Derive baseline specs from tests, API contracts, and observed behavior, then
  review them with the user/domain owner.
- Preserve significant design decisions in OpenSpec design/archive artifacts.
  Add a separate ADR or architecture guide only when operators/developers need a
  stable explanation outside a change history.

## 5. Memory

When repository-scoped memory is available, store short verified facts and
recurring gotchas under `/memories/repo/`:

- toolchain commands and non-obvious environment constraints;
- proven debugging lessons and operational traps;
- terminology decisions that do not belong in always-on prompts.

Memory is not a substitute for committed contracts. Public behavior stays in
specs; project facts stay in `PROJECT.md`; setup stays in focused docs; temporary
work stays in session memory. Never store secrets or speculative conclusions.

## 6. Minimal documentation

README remains purpose + quick start + links. Create focused docs only for setup,
operations, architecture, or migration information that a fresh reader cannot
infer. Prefer one diagram/table over a directory dump; remove stale documents.

Add a root `llms.txt` (llms.txt standard) as the machine-readable entry index that
links to `AGENTS.md`, `PROJECT.md`, and the knowledge base. Keep it terse — links
and one-line descriptions, not content.

## 7. Verify onboarding context

- A fresh agent can locate entry points, layers, tests, configs, and validation.
- `PROJECT.md`, specs, code graph, and memory agree with current code.
- Agent configuration guard and relevant spec validation pass.
- No generated inventories, copied repository history, secrets, or AI filler were
  added.
