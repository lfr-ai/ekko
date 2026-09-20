---
paths:
  - ".gitattributes"
  - "**/.gitattributes"
  - ".editorconfig"
  - "**/.editorconfig"
  - ".gitignore"
  - "**/.gitignore"
  - "**/.gitkeep"
  - "renovate.json"
  - "renovate.json5"
  - ".renovaterc.json"
  - "**/renovate.json"
  - "**/renovate.json5"
  - "llms.txt"
  - "**/*.xml"
---

# Repository files

- `.gitattributes` owns cross-platform text normalization: default text to LF,
  mark binary formats explicitly, and add format-specific exceptions only when a
  tool requires them. Do not duplicate ignore rules there.
- `.editorconfig` owns editor-agnostic whitespace and charset defaults
  (`root = true`, `charset`, `end_of_line = lf`, final newline, per-glob
  `indent_*`/`max_line_length`). Keep it aligned with the formatters rather than
  contradicting them — it governs the editor, `.gitattributes` governs Git.
- `.gitignore` excludes generated/local state, never source templates. Keep a
  directory with `.gitkeep` only when the empty directory itself is required;
  the placeholder must be empty and removed once a real tracked file exists.
- Keep `llms.txt` a terse machine-readable index of relative, existing sources of
  truth. Link rather than duplicate policy, architecture, or setup prose.
- Renovate config (`renovate.json`) references its `$schema`, prefers shared
  `extends` presets over inlined rules, scopes `packageRules` narrowly, and
  never embeds registry credentials — private-feed auth comes from
  runtime-injected secrets, not the committed file.
- XML must be well-formed, UTF-8, and schema-validated when an XSD or tool schema
  exists. Disable external entity resolution for untrusted input and preserve the
  owning tool's element/attribute order when it is significant.
- Generated manifests (`core/registry_constants.py`, `openapi.json`) are changed
  through their owning generator, not by hand.
