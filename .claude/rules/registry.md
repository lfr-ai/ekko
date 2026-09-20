---
paths:
  - "registry/**"
---

# Naming Registry Conventions

The naming registry (`registry/naming_registry.json`) is the single source of truth for
shared constants across backend and frontend.

## Workflow

1. Edit `registry/naming_registry.json` — add/modify entries
2. Run `task registry:generate` — regenerates the backend package's
   `core/registry_constants.py` (see `PROJECT.md` for the exact path)
3. Import generated constants in backend code

## Rules

- All user-facing strings come from the registry
- Backend enums reference registry keys
- Never hardcode strings that exist in the registry
- Run `task registry:generate` after every registry edit
- Import from `<package>.core.registry_constants` (see `PROJECT.md` for
  `<package>`) — never duplicate values
