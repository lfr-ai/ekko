---
name: naming-registry
description: Canonical naming definitions shared between backend and frontend.
disable-model-invocation: true
---

# Skill: Naming Registry

## Purpose

The naming registry provides a single source of truth for canonical names,
labels, and identifiers used across the full stack. It prevents naming drift
between backend enums, frontend display strings, and documentation.

## Files

| File | Purpose |
|------|---------|
| `registry/naming_registry.json` | Canonical definitions |
| `registry/generate_registry.py` | Code generator |
| `backend/src/ekko/core/registry_constants.py` | Generated Python constants |

## Workflow

1. Edit `registry/naming_registry.json` to add/modify names
2. Run `task registry:generate` (or `python registry/generate_registry.py`)
3. Generated constants are written to `backend/src/ekko/core/registry_constants.py`
4. Import from `ekko.core.registry_constants` in backend code

## Schema

```json
{
  "environments": {
    "local": { "label": "Local", "description": "Local development" },
    "dev": { "label": "Development", "description": "Shared dev environment" }
  },
  "llm_providers": {
    "openai": { "label": "OpenAI", "description": "OpenAI API" },
    "azure_openai": { "label": "Azure OpenAI", "description": "Azure-hosted OpenAI" }
  }
}
```

## Rules

- All user-facing strings come from the registry
- Backend enums reference registry keys
- Frontend display labels are derived from registry values
- Never hardcode display names in components or templates
