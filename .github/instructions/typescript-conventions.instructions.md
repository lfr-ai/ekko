---
description: JavaScript and TypeScript module conventions and type-safety standards
applyTo: "**/*.{js,jsx,mjs,cjs,ts,tsx,mts,cts}"
---

# JavaScript & TypeScript Conventions

- Prefer TypeScript for application source. JavaScript is acceptable for tool
  configuration or an external compatibility requirement and follows the same
  module, naming, and formatter rules.

## Type safety

- Enable strict TypeScript settings.
- Do not use `any`; use `unknown`, unions, narrowing, or generics.
- Prefer `readonly` for immutable contracts.
- Use discriminated unions for multi-state logic.
- Use `never` exhaustiveness checks in `switch` statements.

## Compiler baseline

- Keep `strict`, `strictNullChecks`, and `noImplicitAny` enabled.
- Keep `noUncheckedIndexedAccess` enabled.
- Prefer `useUnknownInCatchVariables`.
- Prefer `noImplicitReturns` and `noFallthroughCasesInSwitch`.
- Prefer explicit type/value imports where supported.

## Modules and exports

- Use named exports only.
- Keep module surfaces explicit and stable.
- Avoid wildcard exports (`export *`) for core modules.

## Declarations (`.d.ts`)

- Use `.d.ts` files only for ambient types: an untyped third-party module, Vite's
  `import.meta.env` (`vite-env.d.ts`), non-code asset imports, or a global
  augmentation — never for runtime code.
- Prefer module augmentation (`declare module "x" { ... }`) over `declare global`;
  keep any globals minimal and colocated (e.g. `src/types/`).
- Do not hand-write `.d.ts` for your own source — let `tsc`/the bundler emit
  declarations (`declaration: true`) when publishing a library.

## Naming

- Use kebab-case for file names.
- Use PascalCase for types and interfaces.
- Use SCREAMING_SNAKE_CASE for constants.
- Prefix internal constants with `_`.
- Use camelCase for functions, methods, variables, and event handlers.
