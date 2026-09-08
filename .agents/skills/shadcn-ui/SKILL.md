---
name: shadcn-ui
description: Use shadcn/ui consistently in layered React applications. Use when initializing components.json, adding registry components, configuring aliases, composing Radix primitives, defining CVA variants, or reviewing component accessibility and styling.
---

# shadcn/ui Conventions

## Purpose

Enforce consistent usage of shadcn/ui components following the new-york style
variant with Tailwind CSS v4 and Radix UI primitives.

## Component Location

All shadcn/ui primitives live in `src/presentation/components/ui/`.
Application-specific composed components live in `src/presentation/components/`.

## Adding components

```bash
bunx --bun shadcn add button card dialog
```

Run from the frontend package root. In a monorepo, pass the component workspace
with `-c`. Task wrappers are optional and must delegate to this package command.

## Composition Patterns

### Basic Usage

```typescript
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";
```

### Conditional Classes with cn()

```typescript
import { cn } from "@/lib/utils";

<Button className={cn("w-full", isLoading && "opacity-50")} disabled={isLoading}>
  {isLoading ? "Loading..." : "Submit"}
</Button>
```

### Variant Props

Use `class-variance-authority` (CVA) for component variants:

```typescript
import { cva, type VariantProps } from "class-variance-authority";

const badgeVariants = cva("inline-flex items-center rounded-md", {
  variants: {
    variant: {
      default: "bg-primary text-primary-foreground",
      destructive: "bg-destructive text-destructive-foreground",
    },
  },
  defaultVariants: { variant: "default" },
});
```

## Style Rules

- **No inline styles** — use Tailwind utility classes exclusively.
- **No CSS modules** — compose with `cn()` utility.
- **Dark mode** — use CSS variables defined in `tailwind.css`.
- **Responsive** — use Tailwind breakpoint prefixes (`sm:`, `md:`, `lg:`).
- **Spacing** — use consistent Tailwind spacing scale.

## Accessibility

- All interactive elements must have accessible names.
- Use Radix UI primitives (Dialog, Popover, etc.) for keyboard/screen reader support.
- Ensure color contrast ratios meet WCAG 2.1 AA (4.5:1 text, 3:1 UI).
- Always provide `aria-label` or visible label for icon-only buttons.
- Preserve generated primitives unless a project-wide design-system change
  requires an intentional update; compose application behavior outside `ui/`.

## Configuration

`components.json` defines:

- Style: `new-york`
- CSS path: `src/presentation/styles/tailwind.css`
- Aliases: components, ui, hooks, lib, utils
- Icon library: `lucide`
- Hooks: `@/application/hooks`
- Utilities: `@/lib/utils`

## Common Components

| Component | Use For |
|-----------|---------|
| Button | Actions, submissions |
| Card | Content containers |
| Input / Label | Form fields |
| Select | Dropdown selections |
| Badge | Status indicators |
| Separator | Visual dividers |
| Switch | Toggle settings |
| Sonner (toast) | Notifications |
