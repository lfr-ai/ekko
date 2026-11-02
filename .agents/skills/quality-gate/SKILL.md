---
name: quality-gate
description: Run full validation suite before finalizing any change. Use after implementing features or fixes.
---

# Quality gate

Run the repository-owned validation before claiming a change is complete. Read
`PROJECT.md`, lockfiles, manifests, task definitions, and CI first; never infer a
toolchain from globally installed commands or reconstruct checks by habit. See
[`references/toolchain-metafiles.md`](references/toolchain-metafiles.md) for
which file owns which category of tool config, and pre-commit hook conventions
for wiring a newly added tool into the gate.

## Workflow

1. Run the smallest formatter, linter, type check, and focused test that cover
	 the changed files while iterating. A project's `test:fast`/`test:path`-style
	 task (scoping pytest/`bun test` to the changed file or directory instead of
	 the whole suite) is dramatically cheaper than a full run — heavy test
	 fixtures/imports (a DB container, a browser, a full app client) are often
	 paid once per process regardless of how many tests run, so a full-suite run
	 costs far more than the sum of its "slow" tests would suggest; prefer the
	 narrowest command that still exercises the change.
2. Run every project-declared completion gate **in its fast tier**: tests,
	 lint/format checks, static analysis, build/package validation,
	 specification validation, and repository policy guards. A project's fast
	 tier excludes `slow`-marked tests and Docker/network-dependent tool
	 hooks — those still run in CI on every build (and in the manual/full tier
	 below), so skipping them locally does not weaken the gate.
3. Exercise environment-dependent integration/E2E checks when their declared
	 services are available. Report genuine unavailable prerequisites; never fake
	 a pass.
4. Fix failures caused by the change. Classify unrelated baseline failures with
	 exact evidence instead of hiding, skipping, or weakening them.
5. Re-run the complete gate after the final edit. Evidence must be fresh in the
	 completion message. Run the **full tier** (see below) instead of the fast
	 tier when the change touches integration-tested surfaces, a pre-commit
	 hook's own config, or before telling the user the change is CI-ready.
6. Reconcile `PROJECT.md`, specs, docs, and root `memories/`; update only artifacts
   made stale by the change and remove obsolete handoffs through reviewed edits.

## Fast tier vs. full tier

Slow checks (long-running/Docker-backed tests, network- or Docker-dependent
static-analysis hooks) cost real time and are not needed on every iteration —
CI runs them on every build regardless, so the fast tier never weakens the
gate a change actually has to pass before merge. A project using this pattern
typically exposes both tiers through its task runner, e.g. this repository:

| Tier | Tests | Repository policy hooks |
| --- | --- | --- |
| Fast (default) | `task test` (excludes `slow`) | `task check` (excludes Docker/network hooks) |
| Full (CI-equivalent) | `task test:all` | `task check:slow` |

Adapt the concrete task names to the repository's own Taskfile/`package.json`
scripts — the fast/full split is the pattern to apply, not a literal command
to copy.

## Diagnosing a slow gate

Do not assume test *count* is the bottleneck — measure before cutting tests.
This repository exposes `task test:collect-time` (isolates pytest collection
cost — heavy transitive imports — from execution) and `task test:durations`
(ranks the 25 slowest `call`/`setup` phases). A gate dominated by collection
time needs import/fixture hygiene fixes, not fewer tests; a gate with a handful
of multi-second `call` entries usually has a genuine unmocked sleep, retry
backoff, or per-example fixture rebuild (see the `testing-conventions` skill's
"Diagnosing slow tests" section) worth fixing directly.

## Toolchain selection

- Python/uv repositories use only their declared `uv run` or Task commands.
- Bun repositories use only the package's `bun run` scripts and frozen install;
	never substitute npm, pnpm, Yarn, or Bun's unrelated built-in test runner.
- Full-stack repositories run both bounded toolchains through existing root
	wrappers when available; do not invent wrappers during verification.
- Run pre-commit or equivalent repository guards when configured. Agents never
	run Git operations as part of validation.

## Failure handling

- Read the first causal error, reproduce it with the narrowest command, fix the
	root cause, then broaden validation.
- Do not auto-fix generated, migration, vendor, or snapshot files without first
	confirming their owning workflow.
- Do not lower coverage, lint, type, security, or test thresholds to obtain a
	green result.
- Treat the repository's coverage configuration and CI as the only policy
	sources; never duplicate numeric thresholds in this skill.

## Completion checklist

- [ ] Declared formatter/linter and static checks pass
- [ ] Unit, integration, property, component, and E2E suites relevant to the
			project shape pass or have an evidenced unavailable prerequisite
- [ ] Build/package and spec/contract checks pass
- [ ] Repository policy and agent-configuration guards pass
- [ ] Documentation and environment templates match changed behavior/config
- [ ] No secret, generated junk, or foreign package-manager state was introduced
- [ ] Shared memory contains only new verified outcomes/decisions/lessons; no
	transcripts, private reasoning, or duplicated source-of-truth content

## Verification script (Task-based repos)

`scripts/run_gate.py` is a thin orchestrator, not a new source of truth: it
shells out to this repository's own declared `task format|lint|typecheck|test|check`
in sequence and stops at the first failure. It carries zero hardcoded
thresholds. Adapt the step list before reusing this skill in a repo without a
Taskfile (e.g. substitute `bun run lint`/`bun test` for a Bun-only repo):

```shell
uv run python .agents/skills/quality-gate/scripts/run_gate.py [--skip-tests] [--full]
```

Default invocation runs the fast tier. Pass `--full` to run the complete tier
instead (`task test:all` + an added `check:slow` step).
