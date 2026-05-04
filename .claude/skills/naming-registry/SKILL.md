---
name: naming-registry
description: Registry-first constant generation workflow. Use when adding routes, API fields, ORM fields, or status enums that must be shared between backend and frontend.
disable-model-invocation: true
argument-hint: "[category] [key] [value]"
allowed-tools:
  - Bash(task registry:*)
  - Read
  - Edit
---

# Naming Registry

The naming registry is the single source of truth for shared constants.

## Workflow

1. Edit `registry/naming_registry.json` — add/modify entries
2. Run `task registry:generate` — regenerates `backend/src/ekko/core/registry_constants.py`
3. Import generated constants in your code

## When to Use

- Adding a new API route path
- Adding a new ORM field name
- Adding a new status enum value
- Any string that appears in both backend and frontend

## Example

```json
// registry/naming_registry.json
{
  "routes": {
    "HEALTH": "/api/health",
    "TRANSCRIPTIONS": "/api/transcriptions"
  },
  "fields": {
    "USER_ID": "user_id",
    "CREATED_AT": "created_at"
  }
}
```

Then use: `from ekko.core.registry_constants import ROUTE_HEALTH, FIELD_USER_ID`
