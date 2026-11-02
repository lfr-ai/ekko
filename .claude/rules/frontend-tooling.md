---
paths:
  - "**/package.json"
  - "**/bunfig.toml"
  - "**/biome.json"
  - "**/biome.jsonc"
  - "**/components.json"
  - "**/tsconfig*.json"
  - "**/vite.config.*"
  - "**/vitest.config.*"
  - "**/playwright.config.*"
  - "**/.storybook/**"
  - "**/*.stories.*"
---

# Frontend Tooling

- A JavaScript package uses **Bun only**: exact `packageManager`, committed text
  `bun.lock`, and `bun install --frozen-lockfile` in CI. No foreign lockfiles.
- Keep Bun-specific settings in local `bunfig.toml`; disable auto-install when
  deterministic dependency resolution matters. Do not restate Bun defaults.
- Use Vite with the default React (Oxc) and Tailwind CSS v4 plugins. Choose the
  SWC React plugin only for a verified SWC-plugin or measured performance need.
  Project-owned config supplies ports, proxies, targets, and env prefixes.
- Use strict TypeScript with `noUncheckedIndexedAccess`,
  `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, `noImplicitReturns`, and
  matching `@/*` aliases in TypeScript and Vite.
- Biome is the only formatter/linter. Use its schema, stable recommended preset,
  accessibility/correctness/security rules, assist import organization, LF, and
  force-ignore generated output. Enable CSS formatting and Tailwind directives.
  Permit default exports only where a framework contract requires one, including
  Vite config and Storybook CSF metadata; use a narrow story-file override.
- Vitest is a local dev dependency. Run it via `bun run test` (`vitest run`),
  never `bun test`; isolate tests, restore mocks, and declare meaningful
  project-owned coverage thresholds.
- Playwright uses a controlled `webServer`, web-first assertions, first-retry
  traces, failure screenshots, and only browsers required by the support matrix.
- Storybook is optional. When adopted, use React-Vite, typed CSF stories,
  accessibility + Vitest addons, deterministic mocks, and no production secrets;
  enable `@storybook/addon-mcp` only with a local dev-server workflow.
- `components.json` maps shadcn primitives to `presentation/components/ui`, hooks
  to `application/hooks`, and utilities to `lib`; keep aliases consistent with
  TypeScript and Vite.
- Task commands may wrap package scripts only after the frontend package exists.
