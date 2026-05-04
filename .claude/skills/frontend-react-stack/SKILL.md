---
name: frontend-react-stack
description: React 19 + TypeScript + Vite + shadcn/ui + Tailwind CSS v4 conventions. Use when writing or reviewing frontend code.
when_to_use: When creating React components, writing TypeScript interfaces, adding Zustand stores, configuring TanStack Query hooks, using shadcn/ui components, styling with Tailwind CSS v4, or running Biome/Vitest.
paths:
  - "frontend/src/**/*.{ts,tsx}"
---

# Frontend React Stack

## Stack

- React 19, TypeScript strict, Vite 6 + SWC
- shadcn/ui components (`presentation/components/ui/`)
- Tailwind CSS v4 (no CSS modules, no styled-components)
- Zustand for global state, TanStack React Query for server state
- React Hook Form + Zod for form validation
- Biome for format/lint (not Prettier, not ESLint)
- Vitest + React Testing Library for unit tests
- Playwright for E2E

## Rules

- Named exports only. No default exports.
- Functional components with explicit return types
- Use `cn()` helper from `lib/utils` for conditional classes
- Domain models/schemas in `domain/`, API clients in `infrastructure/`
- State hooks in `application/`, UI in `presentation/`
