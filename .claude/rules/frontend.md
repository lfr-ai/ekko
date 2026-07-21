---
paths:
  - "frontend/src/**/*.{ts,tsx}"
---

# Frontend React Conventions

- React 19, TypeScript strict mode, Vite 6 + SWC
- shadcn/ui components from `presentation/components/ui/`
- Tailwind CSS v4 for styling. No CSS modules, no styled-components.
- Zustand for global state, TanStack React Query for server state
- React Hook Form + Zod for form validation
- Biome for formatting and linting (not Prettier, not ESLint)
- Vitest + React Testing Library for unit tests, Playwright for E2E
- Named exports only. No default exports.
- Functional components with explicit return types
- Use `cn()` helper from `lib/utils` for conditional classes
- Use semantic colors only: `bg-primary`, `text-muted-foreground` — never `bg-blue-500`
- Always install shadcn components via CLI, never copy-paste
