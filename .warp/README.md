# Warp Terminal Configuration

This directory contains shared [Warp](https://www.warp.dev/) terminal configuration for
the **Ekko** development team.

## Contents

| Path | Purpose |
|------|---------|
| `settings.toml` | Recommended team terminal settings |
| `themes/` | Custom project themes |
| `workflows/*.yaml` | Reusable command workflows in Warp command palette |
| `launch_configurations/ekko.yaml` | Launch profile for project context |
| `AGENTS.md` | Warp Agent Mode project rules |

## Install Team Configuration

Use the repository task:

- `task tools:warp:install`

This installs team launch/workflow/settings artifacts to your local Warp config directories.

## Ensure Warp runs with zsh + Oh My Zsh

### macOS / Linux

1. Install zsh and set it as your default login shell.
2. Install Oh My Zsh.
3. Restart Warp and verify with `echo $SHELL`.

### Windows (recommended via WSL)

1. Install WSL (Ubuntu recommended).
2. Inside WSL: install `zsh`, set it as default shell, then install Oh My Zsh.
3. In Warp, open a WSL session/profile and verify with `echo $SHELL`.

## Verify

From Warp, run:

- `task --list`
- `task dev`
- `task test`

If these work and your shell reports `zsh`, your Warp + zsh/OMZ setup is good.
