---
description: Prompt template file conventions for versioned, filesystem-backed prompt registries
applyTo: "src/**/prompts/**/*.md"
---

# Prompt Template Instructions

Prompt bodies are versioned content files (markdown/plain text), not Python
source — never type-check or f-string-escape them.

## Structure

- One file per logical prompt: `<name>.prompt.md`.
- Leading version marker comment: `<!-- vX.Y | YYYY-MM-DD -->`.
- Markdown headers: role, input contract, validation rules, output format.
- Variables use plain `{placeholder}` markers substituted by the loader —
  never Python f-string/`.format()` syntax.

## Versioning workflow

- Iterate freely in `templates/`; editing content never touches the version
  header, `versions/`, or the registry manifest.
- Never hand-edit a published/immutable snapshot or the registry manifest
  directly — publish only through the repo's designated prompt-publish tool,
  the single sanctioned way version pins change.
- The publish tool copies the working copy once (byte-identical) into its
  versioned snapshot directory, pins the requested set(s), and advances the
  header — atomically, refusing to touch an existing (even empty) snapshot
  directory. No orphaned or intermediate snapshots outside the registry.
- Inspect current registry state anytime with the repo's read-only registry
  status command (template header, latest archive, and set pins per prompt) —
  it never writes anything.

## Best Practices

- Explicit, unambiguous output format (exact schema, not "JSON-ish").
- Document the input contract and failure behavior for malformed input.
- Shared fragments (e.g. rules injected into several prompts) live in one
  template referenced by a placeholder marker, never copy-pasted.

## Testing

- Test that a template renders given representative input.
- Test that the registry resolves every version-set entry to an existing file.
- Run integration/backtests when behavior-affecting content changes.
- The repo's immutability guard (pre-commit + CI) fails a commit/PR that
  modifies, deletes, renames, or copies any file under `versions/`.

For this repository's concrete publishing commands, see the project-scoped
`prompt-registry` skill.
