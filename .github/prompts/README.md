# Copilot Prompt Organization

This directory contains GitHub Copilot prompt files.

## Domain subfolders

- `openspec/` — grouped OpenSpec workflow prompts (canonical grouped view)
- `gitnexus/` — grouped GitNexus analysis prompts

## Legacy compatibility

Flat `opsx-*.prompt.md` files are retained for backward compatibility.
Use `openspec/*.prompt.md` for new references.

## Maintenance

Run `uv run python .agents/sync_agentic_setup.py` after editing OpenSpec prompts
so grouped and neutral prompt topology stays aligned.
