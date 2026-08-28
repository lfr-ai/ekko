---
name: frontend-debugging
description: Diagnose frontend runtime, rendering, network, accessibility, and performance problems with browser evidence. Use when a React/Vite UI fails, behaves inconsistently, leaks memory, has slow interactions, or needs console/network/trace analysis.
---

# Frontend debugging

Reproduce first and gather browser evidence before changing code. Use Playwright
for deterministic journeys and Chrome DevTools MCP for runtime diagnostics.

## Workflow

1. Confirm the running URL, build mode, browser, viewport, and exact reproduction.
2. Check the browser console and failed source-mapped stack traces.
3. Inspect network requests: URL, method, status, timing, CORS, payload shape, and
   response headers. Compare against the API contract rather than guessing.
4. Inspect React-visible state and rendering only after transport/configuration is
   ruled out. Look for stale query keys, duplicated effects, unstable references,
   hydration/Strict Mode assumptions, and leaked listeners/timers.
5. For slowness, capture a performance trace and identify the relevant LCP/INP/CLS,
   long task, network waterfall, render, or layout-shift evidence.
6. For suspected leaks, compare isolated heap snapshots after a repeatable
   interaction; do not infer leaks from one growing development-session profile.
7. Implement the smallest root-cause fix and add a Vitest or Playwright regression.

## Tool boundaries

- Playwright: user journey, locator/actionability, assertions, cross-browser proof.
- Chrome DevTools: console, network, Lighthouse/performance, source maps, memory.
- React DevTools: component ownership and render/profiler evidence when available.

## Safety

- Use isolated browser profiles. Never expose personal sessions, production data,
  credentials, or sensitive request headers to browser MCP tools.
- Keep usage statistics and CrUX lookups disabled unless the project explicitly
  opts in.
- Do not fix symptoms with sleeps, arbitrary retries, disabled lint rules, or
  swallowed errors.
