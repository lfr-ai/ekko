---
name: quick-reference
description: >
  Quick-reference card for all Ponytail modes, skills, and commands. One-shot
  display, not a persistent mode. Trigger when the user says "ponytail help",
  "what ponytail commands", or "how do I use ponytail". Invoke as
  `/ponytail-quick-reference` in Copilot or `/ponytail:quick-reference` in Claude.
---

# Ponytail Quick Reference

Display this reference card when invoked. One-shot, do NOT change mode,
write flag files, or persist anything.

## Levels

| Level | Natural trigger | What changes |
|-------|-----------------|--------------|
| **Lite** | `ponytail lite` | Build what's asked, name the lazier alternative in one line. |
| **Full** | `ponytail full` | Enforce YAGNI → stdlib → native → one line → minimum. Default. |
| **Ultra** | `ponytail ultra` | Prefer deletion and challenge requirements before building. |

Level sticks until changed or session end. Command users pass the level to the
minimalism command: `/ponytail-minimalism <level>` in Copilot or
`/ponytail:minimalism <level>` in Claude.

## Family commands

| Skill ID | Copilot | Claude | What it does |
|----------|---------|--------|--------------|
| `ponytail/minimalism` | `/ponytail-minimalism` | `/ponytail:minimalism` | Persistent lazy mode. |
| `ponytail/audit` | `/ponytail-audit` | `/ponytail:audit` | Repo-wide over-engineering audit. |
| `ponytail/debt` | `/ponytail-debt` | `/ponytail:debt` | Harvest `ponytail:` debt markers. |
| `ponytail/quick-reference` | `/ponytail-quick-reference` | `/ponytail:quick-reference` | This card. |
| `ponytail/overengineering-review` | `/ponytail-overengineering-review` | `/ponytail:overengineering-review` | Diff-focused complexity review. |

Natural-language triggers in each skill description work without a command.

## Deactivate

Say "stop ponytail" or "normal mode". Resume by saying "ponytail full" or by
invoking the minimalism command above.

## Configure Default Mode

Default mode = `full`, auto-active every session. Change it:

**Environment variable** (highest priority):
```bash
export PONYTAIL_DEFAULT_MODE=ultra
```

**Config file** (`~/.config/ponytail/config.json`, Windows: `%APPDATA%\ponytail\config.json`):
```json
{ "defaultMode": "lite" }
```

Set `"off"` to disable auto-activation on session start, then activate manually
with the minimalism command.

Resolution: env var > config file > `full`.

## Update

Enable auto-update once: open `/plugin`, go to Marketplaces, pick ponytail, Enable auto-update. Claude Code then pulls new versions at startup (run `/reload-plugins` when it prompts). Manual refresh: `/plugin marketplace update ponytail` then `/reload-plugins`.

If `/plugin` is not recognized, update Claude Code through the installation
method already used on that machine, then restart it. Other hosts use their own
update flow.

## More

Full docs + examples: https://github.com/DietrichGebert/ponytail
