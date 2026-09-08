---
name: ui-ux-frontend
description: UI/UX review for frontend flows — usability, visual hierarchy, interaction behavior, and accessibility. Use when implementing or reviewing frontend UX and accessibility details.
---

# UI/UX Frontend Skill

Use this skill when implementing or reviewing frontend UX flows, visual hierarchy,
interaction behavior, and accessibility details in this repository.

## Scope

- Form usability (labels, hints, validation feedback, focus management)
- Information hierarchy and progressive disclosure
- Responsive behavior across common breakpoints
- Keyboard navigation and screen reader compatibility
- Empty/loading/error/success state clarity

## Working Rules

1. Keep components thin: presentation only, delegate side effects to application hooks.
2. Favor existing shadcn/ui primitives before introducing custom components.
3. Prefer `getByRole` and semantic HTML patterns for testability and accessibility.
4. Keep cognitive load low: short components, named conditionals, early returns.
5. Preserve clean architecture import boundaries.

## Validation Checklist

- Visual and interaction behavior matches expected user journey
- WCAG 2.1 AA critical checks pass (focus order, labels, contrast-sensitive states)
- Unit/integration tests cover important interaction states
- `task check` passes
