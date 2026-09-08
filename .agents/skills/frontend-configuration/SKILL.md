---
name: frontend-configuration
description: Add or change frontend runtime configuration safely in Vite applications. Use when introducing environment variables, API URLs, feature flags, public build-time settings, import.meta.env typing, or boundary validation.
---

# Frontend configuration (Vite)

Frontend configuration is public, build-time input. Never place credentials,
private keys, connection strings, or server-only settings in the browser bundle.

## Add or change a value

1. Decide whether the browser truly needs it. Keep server-owned policy and secrets
   in the backend.
2. Add a descriptive prefixed variable to `.env.example`; per-environment values
   belong in the existing environment templates or deployment configuration.
3. Declare the variable in `vite-env.d.ts` (or the project's environment type
   declaration) so `ImportMetaEnv` is explicit and readonly.
4. Read and validate all values once in `infrastructure/config.ts` with Zod or an
   equally precise boundary validator. Export a frozen typed config object.
5. Inject that object through application/bootstrap boundaries; do not scatter
   `import.meta.env` reads through components or domain code.
6. Update deployment/build arguments, tests, and focused documentation in the
   same change-set.

## Rules

- Use Vite's public prefix intentionally (normally `VITE_`); every prefixed value
  is visible to users.
- Treat all values as strings until validated. Parse booleans, URLs, enums, and
  numbers explicitly and fail startup/build with a useful message.
- Domain and presentation modules never import Vite environment APIs.
- API base URLs are project facts; avoid hardcoded hosts and normalize trailing
  separators once.
- Feature flags represent temporary rollout/configuration, not authorization.
- Tests stub environment values through the test runner and restore them between
  tests; never mutate a developer's actual `.env` files.
