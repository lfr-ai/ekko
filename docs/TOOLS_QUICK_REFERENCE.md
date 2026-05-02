# Development Tools Quick Reference

## Quick health check

- `task tools:status`
- `task tools:setup`
- `task verify`

## Tool map

| Tool | Purpose | Main config |
| --- | --- | --- |
| CodeRabbit | PR review automation | `.coderabbit.yaml` |
| GitNexus | Knowledge graph + MCP context | `.gitnexus/config.json` |
| OpenSpec | Spec-driven planning workflow | `.github/skills/openspec/SKILL.md` + `.spectral.yaml` |
| Warp | Team workflows + terminal UX | `.warp/` |
| Copilot + Claude | AI coding assistant in VS Code | `.vscode/settings.json` |
| MCP servers | Tool integrations in chat | `.vscode/mcp.json` |

## Copilot + Claude verification

1. Open Copilot Chat.
2. Select a Claude model in the model picker.
3. Ask: `What model are you using?`
4. Confirm instruction files are referenced in responses.

See: `docs/VERIFY_COPILOT_INTEGRATION.md`.

## GitNexus quick commands

- `gitnexus analyze`
- `gitnexus status`
- `gitnexus mcp`
- `gitnexus analyze --incremental`

## Warp quick commands

- `task tools:warp:install`
- `task dev`
- `task test`
- `task check`

For zsh/OMZ setup, use:

- `scripts/install/install-zsh.zsh`
- `scripts/install/install-warp.zsh`

## OpenSpec quick use

- Use the `openspec` skill when planning non-trivial features.
- Draft requirements + scenarios before implementation.
- Keep specs testable and map code changes to spec deltas.

## CI workflow validation

- `task tools:actionlint:validate`
- GitHub workflow `actionlint.yml` validates workflow syntax on PR/push changes.

## TL;DR

If these pass, your setup is healthy:

- `task tools:setup`
- `task check`
- `task verify`
