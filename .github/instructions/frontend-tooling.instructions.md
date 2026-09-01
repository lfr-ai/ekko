---
description: Bun, Vite, Biome, TypeScript, Vitest, Playwright, and shadcn configuration standards
applyTo: "**/package.json, **/bunfig.toml, **/biome.json, **/biome.jsonc, **/components.json, **/tsconfig*.json, **/vite.config.*, **/vitest.config.*, **/playwright.config.*"
---

# Frontend Tooling

- A JavaScript package uses **Bun only**: exact `packageManager`, committed text
  `bun.lock`, and `bun install --frozen-lockfile` in CI. No foreign lockfiles.
- Keep Bun-specific settings in local `bunfig.toml`; disable auto-install when
  deterministic dependency resolution matters. Do not restate Bun defaults.
- Use Vite with the React SWC and Tailwind CSS v4 plugins. Project-owned config
  supplies ports, proxies, browser targets, and environment-variable prefixes.
- Use strict TypeScript with `noUncheckedIndexedAccess`,
  `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, `noImplicitReturns`, and
  matching `@/*` aliases in TypeScript and Vite.
- Biome is the only formatter/linter. Use its schema, stable recommended preset,
  accessibility/correctness/security rules, assist import organization, LF, and
  force-ignore generated output. Enable CSS formatting and Tailwind directives.
- Vitest is a local dev dependency. Run it via `bun run test` (`vitest run`),
  never `bun test`; isolate tests, restore mocks, and declare meaningful
  project-owned coverage thresholds.
- Playwright uses a controlled `webServer`, web-first assertions, first-retry
  traces, failure screenshots, and only browsers required by the support matrix.
- `components.json` maps shadcn primitives to `presentation/components/ui`, hooks
  to `application/hooks`, and utilities to `lib`; keep aliases consistent with
  TypeScript and Vite.
- Task commands may wrap package scripts only after the frontend package exists.
