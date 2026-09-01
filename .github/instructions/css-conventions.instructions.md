---
description: CSS and Tailwind CSS v4 conventions for semantic, accessible styling
applyTo: "**/*.css"
---

# CSS Conventions

- Use Tailwind CSS v4 through `@tailwindcss/vite` and one CSS-first entry with
  `@import "tailwindcss"`; do not add legacy Tailwind/PostCSS config by habit.
- Define project-owned semantic tokens as CSS variables (prefer OKLCH), then map
  utilities to those tokens. Components use semantic classes, not raw palette
  values or repeated arbitrary colors.
- Keep dark-mode tokens under one `.dark` variant and preserve contrast in both
  themes. Respect `prefers-reduced-motion` globally.
- Prefer Tailwind utilities and `cn()` for composition. Keep global CSS for tokens,
  base behavior, and genuinely shared custom utilities; avoid inline styles and
  CSS modules in this stack.
- Configure Biome's CSS formatter explicitly and enable
  `css.parser.tailwindDirectives`. Keep LF line endings and a trailing newline.
- Do not encode product fonts, colors, breakpoints, or animation timings in
  portable agent guidance; those belong to the project design system.
