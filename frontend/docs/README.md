# Frontend Guide

## Purpose

This frontend is intentionally minimal: a stable shell, strict conventions, and clean boundaries that can scale without churn.

## Architecture

- `domain/`: shared UI data contracts and value types
- `application/`: hooks, state, and query orchestration
- `infrastructure/`: API clients and runtime environment wiring
- `presentation/`: pages and UI components only
- `router/`: route configuration and boundaries

## Conventions

- TypeScript strict mode and named exports
- Functional components with explicit return types
- Semantic Tailwind tokens only
- Keep logic shallow in components; move complexity to hooks/utilities
- No magic numbers in runtime logic; use named constants

## Quality Checks

Run these before merging:

- `bun run lint`
- `bun run test`
- `bun run build`

## Notes

- Bundle analyzer is opt-in: set `ANALYZE_BUNDLE=true` for build profiling.
- Keep docs short and current; remove stale details rather than expanding prose.
