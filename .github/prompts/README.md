# Copilot Prompt Registry

GitHub Copilot prompt files (`*.prompt.md`), discovered via
`chat.promptFilesLocations` in `.vscode/settings.json`.

## Layout

| Location | Prompts |
|----------|---------|
| `opsx/` | OpenSpec workflow: `/propose`, `/explore`, `/apply`, `/continue`, `/ff`, `/new`, `/onboard`, `/sync`, `/update`, `/verify`, `/archive`, `/bulk-archive` |
| `gitnexus/` | GitNexus analysis: `/debug`, `/impact` |
| _(top level)_ | Task prompts: `review`, `test`, `refactor`, `debug` |

## Parity

The OpenSpec and GitNexus workflows are mirrored across platforms:

- Claude Code slash commands — `.claude/commands/{opsx,gitnexus}/`
- Agent Skills — `{.github,.claude,.agents}/skills/{opsx,gitnexus}/`

The three skill trees are kept identical; `.github/skills` is canonical.
