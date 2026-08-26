---
description: "Analyze the codebase, then align and repair the tests/ suite to the current source so ALL tests pass — without modifying any source. Exhaustive, plan-driven, convention-compliant cleanup."
agent: agent
---

Align the test suite to the current state of the source code.

**Scope (optional):** If the user provided a scope (e.g. `unit`, `integration`,
`property`, or a path under `tests/`), restrict the walkthrough to it. Otherwise
cover the entire `tests/` tree.

## Non-negotiable constraints

1. **Source is frozen.** Do NOT modify anything outside `tests/`. `src/`,
   `alembic/`, `scripts/`, `sql/`, config, and migrations are read-only. The
   only writable area is `tests/` (test modules, `conftest.py`, factories,
   fixtures, and test-only helpers).
2. **Never mask a real bug.** If a failing test reveals a genuine defect in the
   source (not stale test drift), do NOT rewrite the assertion to encode the
   buggy behavior. Keep the test expressing correct intent, mark it
   `@pytest.mark.xfail(reason=...)` referencing the defect, and record it under
   "Source defects (out of scope)". Never make a suite green by asserting wrong
   behavior.
3. **Toolchain: uv + Task only.** Use `task` and `uv run`. Never invoke `pdm`,
   `poetry`, `pipenv`, `conda`, `pip`, or bare `python`/`pytest`.
4. **No `git` commands.** All version-control actions are the user's.
5. **Follow existing conventions.** Match the repo's structure, naming, markers,
   typing rules (no `Any`, no `cast`, no quoted forward refs), logging import
   policy, and clean-architecture boundaries already in place.

## Phase 1 — Comprehensive codebase analysis & review

- Map the architecture layers (core, application, infrastructure, composition,
  presentation, main) and the dependency direction between them.
- Inventory the public surface the tests depend on: modules, classes, function
  and method signatures, value objects, enums, protocols/ports, DTOs, and routes.
- Identify drift signals: recently renamed, moved, removed, or re-signatured
  symbols; changed defaults; relocated constants; new/removed enums.
- Use `semantic_search`, `grep_search`, and `file_search`; if GitNexus is
  available, use it for call-graph and impact context.

## Phase 2 — Deep-dive the tests folder

- Establish the real baseline first:
  ```bash
  uv run pytest --collect-only -q   # surface import/collection errors
  uv run pytest -q                  # actual pass/fail baseline
  ```
- Inventory every test module, `conftest.py`, fixture, factory, and marker.
- Map each test to the source symbol/behavior it covers.
- Catalog every drift: imports of removed/renamed symbols, calls with outdated
  signatures, stale assertions, obsolete fixtures/factories, dead helpers, wrong
  or missing markers (`unit`/`integration`/`property`), and duplicated setup.

## Phase 3 — Research (web + documentation)

- Use Context7 (`mcp_context7_*`) for version-accurate library/framework docs:
  pytest, Hypothesis, FastAPI `TestClient`, Pydantic, SQLAlchemy, Alembic,
  testcontainers, factory-boy — whatever the suite touches.
- Fetch official docs / the web for anything version-specific or ambiguous.
  Prefer authoritative sources; cite them in the plan.

## Phase 4 — Extensive TODO / PLAN

- Produce a written, checkable plan BEFORE editing. Group by test type and
  module. For each planned change note: the drift found, the fix, and the risk.
- List "Source defects (out of scope)" separately — never fold them into fixes.
- Keep the plan as a living checklist and tick items off as you go.

## Phase 5 — Systematic walkthrough (execute)

Work file-by-file in dependency order (shared `conftest.py`/factories first).
For each module:

- Fix imports to current symbols and paths.
- Align calls/assertions to current signatures and behavior.
- Update fixtures/factories; remove obsolete ones.
- Correct markers; keep clear Arrange/Act/Assert structure.
- Remove dead/duplicated test code; extract shared setup into fixtures.
- Keep cognitive load low: readable, focused, one behavior per test.
- After each module (or logical group), run just that module to confirm green:
  ```bash
  uv run pytest <path/to/module> -q
  ```

## Phase 6 — Cleanup & consistency

- Enforce naming: `test_<module>.py`, `Test<ClassName>`,
  `test_<method>_<scenario>_<expected>`.
- Factory-based test data; no scattered literals.
- HTTP status assertions use `fastapi.status` constants, never numeric literals.
- Respect clean-architecture in tests: layer-appropriate tests do not reach
  across boundaries (e.g. core unit tests must not import infrastructure).
- Apply the repo typing and logging conventions to test code too.

## Phase 7 — Full validation (iterate until green)

```bash
task test                         # or: uv run pytest
uv run pytest --collect-only -q   # must be clean (no collection errors)
uv run pytest -m unit
uv run pytest -m integration      # needs Docker/testcontainers
uv run pytest -m property
```

- Integration tests require Docker. If it is unavailable, report exactly which
  tests were skipped and why — do not fake or stub them to force a pass.

## Definition of done

- Every test passes, or is explicitly `xfail`/`skip` with a documented reason
  tied to a source defect or a missing external dependency.
- Zero changes outside `tests/`.
- Tests accurately reflect the current source; the suite is clean, aligned,
  consistent, and convention-compliant.

## Final report

End with a concise summary:

- Per-file changes (what drifted, what was fixed).
- Source defects found (out of scope) with location and expected vs actual.
- Any `skip`/`xfail` entries and the reason for each.
- Final validation output (pass counts per marker).
