# Dev Container

VS Code Dev Container configuration for local development.

## Quick Start

1. Open the repository in VS Code.
2. Run **Dev Containers: Reopen in Container**.
3. Dependencies are installed using `uv sync --all-extras`.
4. Run the app with `task dev` inside the container.

## Files

| File | Purpose |
| --- | --- |
| `devcontainer.json` | Dev container metadata and VS Code settings. |
| `compose.yml` | Container service wiring for development. |
| `Containerfile.dev` | Development image definition. |
| `Containerfile.dev.dockerignore` | Build context exclusions. |
| `extensions.json` | Recommended VS Code extensions in container. |
| `keybindings.json` | Optional keybindings for container workflows. |
| `post-start.zsh` | Post-start lifecycle script. |
