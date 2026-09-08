---
name: frontend-testing
description: Write and configure frontend unit, component, hook, and property tests with Vitest, Testing Library, user-event, and optional fast-check. Use when adding frontend tests, test setup, mocks, coverage, or debugging flaky React tests.
---

# Frontend testing (Vitest + Testing Library)

Test user-visible behavior and application contracts. Keep E2E journeys in the
`playwright` skill.

## Configuration

- Install Vitest locally and invoke it through package scripts: `bun run test`
  runs `vitest run`; never use `bun test`, which selects Bun's test runner.
- Use `happy-dom` for ordinary component tests; choose `jsdom` only when a needed
  browser API is materially better supported there.
- Add one setup file for `@testing-library/jest-dom`, deterministic browser API
  shims, and cleanup. Enable `clearMocks`, `restoreMocks`, and `unstubEnvs`.
- Use V8 coverage, explicit source/test globs, generated-file exclusions, and
  project-owned thresholds that can only increase.

## Test boundaries

- Domain: pure unit and property tests without React.
- Application hooks/stores: `renderHook`, controlled providers, and mocked ports.
- Presentation: render through a small provider wrapper and interact through the
  accessible UI.
- Infrastructure: test boundary parsing and request construction separately;
  mock network behavior at the transport boundary (MSW or equivalent).

## Interaction pattern

```typescript
const user = userEvent.setup();
render(<ExampleForm />);

await user.type(screen.getByLabelText("Name"), "Ada");
await user.click(screen.getByRole("button", { name: "Submit" }));

expect(await screen.findByRole("status")).toHaveTextContent("Saved");
```

Prefer role → label → text → placeholder → test ID. Use `findBy*` for elements
that appear asynchronously and `waitFor` only for assertions that genuinely
need retries.

## Guardrails

- Assert outcomes, accessibility state, and port calls—not internal state,
  component instances, CSS classes, or implementation-specific hook calls.
- Do not snapshot large component trees. Small stable semantic snapshots are
  acceptable when they communicate a real contract.
- Keep tests isolated; never depend on test order or leaked timers, mocks, cache,
  local storage, or query clients.
- Add property tests only for invariant-rich pure logic; do not force them onto UI
  rendering.
- A regression test must fail for the original defect before the fix.
