# Playwright Skill

Use this skill for end-to-end testing, UI flows, accessibility assertions, and trace-driven debugging in `frontend/tests/`.

## Conventions
- Prefer role/label/text locators over test IDs.
- Keep tests deterministic; avoid brittle timing assumptions.
- Use Playwright traces/snapshots for flaky test diagnosis.

## Baseline Commands
- `bun run test:e2e`
- `bun run test:e2e:ui`
- `bun run test:e2e -- --trace on`
