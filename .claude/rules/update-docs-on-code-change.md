---
description: Keep documentation in lockstep with code changes
paths:
  - "**/*.md"
  - "**/*.py"
  - "**/*.yml"
  - "**/*.yaml"
  - "**/*.json"
---

# Documentation Updates

Update affected documentation in the **same change-set** when behavior,
interfaces, configuration, dependencies, or setup changes.

## What to update

- Features or setup → README quick start or the linked focused guide.
- API endpoints or signatures → API docs and maintained examples.
- CLI commands or flags → command reference and examples.
- Environment variables → `.env.example` and relevant environment templates.
- Deployment or dependency changes → the owning operational guide.
- Breaking changes → a short migration note.

## Keep it lean

- Link to one source of truth instead of duplicating it.
- Keep README introductory; move operational detail to focused docs.
- Update `CHANGELOG.md` only for notable user- or operator-visible changes.
- Verify examples when practical; remove stale examples and broken links.
- Never document speculative behavior or add filler, exhaustive inventories, or
  AI-generated prose that readers will skip.
