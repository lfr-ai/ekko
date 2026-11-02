# Prompt Templates

LLM prompt templates for Ekko AI orchestration services.

## Structure

- **Working copies** are authored under `templates/` (`*.prompt.md`)
- **Immutable versions** live under `versions/{prompt_name}/{version}/`
- **Registry artifacts** live under `registry/`
  - `registry/prompt_registry.json` defines version sets (named groups of pinned versions)
  - `registry/prompt_registry_schema.json` defines JSON schema

## Rules

- Extension: `.prompt.md`
- Published versions are immutable — never modify files under `versions/`
- Version format: `v{major}.{minor}`
- Use `experimental` version set for direct template reads during rapid iteration
