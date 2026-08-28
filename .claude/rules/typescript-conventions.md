---
paths:
	- "**/*.{js,jsx,mjs,cjs,ts,tsx,mts,cts}"
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

## Naming

- Use kebab-case for file names.
- Use PascalCase for types and interfaces.
- Use SCREAMING_SNAKE_CASE for constants.
- Prefix internal constants with `_`.
- Use camelCase for functions, methods, variables, and event handlers.
