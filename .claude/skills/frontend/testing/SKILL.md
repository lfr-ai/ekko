---
name: testing
description: Write and configure frontend unit, component, hook, and property tests with Vitest, Testing Library, user-event, and optional fast-check. Use when adding frontend tests, test setup, mocks, coverage, or debugging flaky React tests.
---

# Frontend testing (Vitest + Testing Library)

Test user-visible behavior and application contracts. Keep E2E journeys in the
`frontend/playwright` skill.

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

## Storybook (optional)

- Add Storybook only when the project needs an isolated component workbench,
  visual review surface, or executable component documentation. It is not a
  default dependency and does not replace Vitest or Playwright.
- Use the Vite integration and typed CSF stories (`Meta` and `StoryObj`). Keep a
  story beside the composed presentation component it documents; do not create
  stories for domain or application modules.
- Model meaningful states and accessibility semantics, not every prop
  permutation. Use interaction/play tests for component behavior and keep
  network state deterministic through the same boundary mocks used by tests.
- Run stories as component tests with the Storybook Vitest addon
  (`@storybook/addon-vitest`) so a story doubles as a test; add visual regression
  (Chromatic or Playwright snapshots) only when a real review workflow needs it.

### Wiring `@storybook/addon-mcp`

Enable the addon only for active agent-assisted story work; keep its local
endpoint out of production and expose no secrets or live customer data through
stories. All three steps must be done together — an MCP entry with no addon or
no running dev server just sits there erroring:

1. **Install and enable the addon** — `bun add -D @storybook/addon-mcp`, then add
   `"@storybook/addon-mcp"` to the `addons` array in `.storybook/main.ts`. Plain
   Storybook exposes no MCP endpoint; only this addon does.
2. **Add a real dev-server task** — `bun run storybook` (or a `frontend:storybook`
   Task target) serving on port 6006. The endpoint only responds while this
   process is running.
3. **Add the MCP entry** to `.mcp.json`, `.vscode/mcp.json`, and `.warp/.mcp.json`
   together (parity is enforced), pointing at the same port as step 2:

   ```json
   "storybook": { "type": "http", "url": "http://localhost:6006/mcp" }
   ```

Until the step 2 dev server is running, the connection shows as errored in the
MCP status UI — that is expected, not a misconfiguration. Restart or reload the
MCP connection after starting the dev server if it was already loaded without one.

Copyable Storybook 10 React-Vite starting points:

- [`assets/storybook-main.ts.template`](assets/storybook-main.ts.template)
- [`assets/storybook-preview.ts.template`](assets/storybook-preview.ts.template)

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
