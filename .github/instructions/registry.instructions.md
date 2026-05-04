---
description: Naming registry conventions for constant generation and shared identifiers
applyTo: "registry/**"
---

# Registry Conventions

The naming registry (`registry/naming_registry.json`) is the single source of truth for
shared constants across backend and frontend.

## Workflow

1. Edit `registry/naming_registry.json` — add/modify entries
2. Run `task registry:generate` — regenerates `backend/src/ekko/core/registry_constants.py`
3. Import generated constants in backend code

## Rules

- All user-facing strings come from the registry
- Backend enums reference registry keys
- Never hardcode strings that exist in the registry
- Run `task registry:generate` after every registry edit
- Import from `ekko.core.registry_constants` — never duplicate values
