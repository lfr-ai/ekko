---
name: frontend-react-stack
description: React 19, TypeScript, Vite, shadcn/ui, Tailwind CSS v4, Biome, Vitest conventions.
---

# Skill: Frontend React Stack

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 19 + TypeScript |
| Bundler | Vite 6 + SWC |
| UI Components | shadcn/ui (Radix primitives + Tailwind CSS v4) |
| Styling | Tailwind CSS v4 (oklch tokens, CSS variables) |
| State | Zustand |
| Forms | React Hook Form + Zod |
| Data Fetching | TanStack React Query |
| Routing | React Router v7 |
| Linting/Formatting | Biome |
| Unit Testing | Vitest + React Testing Library + fast-check |
| E2E Testing | Playwright |
| Toast | Sonner (via shadcn `sonner` component) |
| Icons | Lucide React |
| Runtime | Bun |

## Non-Goals

- Do NOT bypass shadcn primitives for shared controls without documented reason
- Do NOT use `styled-components`, Emotion, or CSS modules
- Do NOT use Prettier (Biome handles formatting)
- Do NOT use Jest (Vitest is the test runner)

## Architecture

```text
frontend/src/
  application/     # hooks, stores (zustand)
  domain/          # models, types, schemas (zod)
  infrastructure/  # api clients, config
  lib/             # utilities (cn helper)
  presentation/    # components, pages, features, styles
    components/
      ui/          # shadcn/ui primitives (button, card, dialog, etc.)
      common/      # shared composite components
      layout/      # shell, sidebar, header
    features/      # feature-scoped components
    pages/         # route-level page components
    styles/        # tailwind.css (theme tokens)
  router/          # React Router config
```

## shadcn/ui Standards

### Installation

Always use the shadcn CLI. Never copy-paste component source.

```bash
bun run shadcn add <component>    # Add a component
bun run shadcn search <query>     # Search available components
bun run shadcn docs <component>   # View component docs
bun run shadcn add --dry-run      # Preview without writing
bun run shadcn add --diff         # Show diff before applying
```

### Configuration

`components.json` maps shadcn output to project paths:

```json
{
  "aliases": {
    "components": "@/presentation/components",
    "ui": "@/presentation/components/ui",
    "hooks": "@/application/hooks",
    "lib": "@/lib",
    "utils": "@/lib/utils"
  }
}
```

### Styling Rules

- Use semantic colors only: `bg-primary`, `text-muted-foreground` — never `bg-blue-500`
- Use `cn()` from `@/lib/utils` for class merging
- Use `gap-*` for spacing between elements, not margins
- Use `size-*` for square dimensions
- Use `truncate` shorthand instead of manual overflow handling
- No manual `dark:` overrides — theme tokens handle dark mode
- No manual `z-index` — rely on component stacking context

### Composition Rules

- Full Card structure: `Card > CardHeader > CardTitle + CardDescription > CardContent > CardFooter`
- Dialog/Sheet always include accessible title (`DialogTitle` / `SheetTitle`)
- Items belong in Groups: `DropdownMenuGroup`, `CommandGroup`, etc.
- Tabs triggers go inside `TabsList`
- Avatar always has AvatarFallback
- Use `Separator` not `<hr>`
- Use `Skeleton` not custom `animate-pulse`
- Use `Badge` not custom styled spans
- Use `Alert` not custom styled divs
- Use `toast()` from sonner, not custom toasts

### MCP/Skills Workflow

Use the shadcn MCP server (configured in `.vscode/mcp.json`) for AI-assisted
component discovery:

```bash
shadcn docs <component>     # Read component documentation
shadcn search <query>       # Find components by description
shadcn add --dry-run        # Preview file changes
shadcn add --diff           # Show exact diff
```

## Forms

Use shadcn Form components with React Hook Form + Zod:

```tsx
<Form>
  <FormField control={form.control} name="email" render={({ field }) => (
    <FormItem>
      <FormLabel>Email</FormLabel>
      <FormControl><Input {...field} /></FormControl>
      <FormMessage />
    </FormItem>
  )} />
</Form>
```

## Testing

- Unit tests: `vitest` + `@testing-library/react` + `fast-check`
- E2E tests: Playwright
- Test files: `tests/unit/**/*.test.tsx` and `tests/e2e/**/*.spec.ts`
- Query by role/label/text, not CSS selectors
- Use `userEvent` over `fireEvent`
