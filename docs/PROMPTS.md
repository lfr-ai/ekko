# Prompts and Templates

This document describes the canonical prompt templates used by Ekko.

Location

- `src/voice/prompts/prompt.txt` – primary canonical prompt and RAG instructions
- `src/voice/prompts/system.txt` – small system prompt template
- `src/voice/prompts/user_template.txt` – user-facing template with placeholders

Guidelines

- Keep the system prompt concise and stable — changes here affect model behavior
  globally.
- Store additional example/shot files in the `src/voice/prompts/` folder for
  versioning.
- Use placeholders (`{CONTEXT}`, `{USER_QUERY}`) and programmatically
  substitute them at runtime.

RAG Integration

- When assembling messages for the model, put the RAG context into the system
  message or as the first assistant message prefixed with `RAG CONTEXT:`.

Output contract

- Prefer machine-readable JSON when clients opt-in; otherwise provide
  human-readable text with a trailing JSON METADATA block.
