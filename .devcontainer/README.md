# Dev Container

VS Code Dev Container configuration for local development.

## Quick Start

1. Open the repository in VS Code.
2. When prompted, click **Reopen in Container** (or use the command palette:
   `Dev Containers: Reopen in Container`).
3. The container builds from `Containerfile.dev` (Python 3.14, Node 24, Bun
   1.4.2, uv 0.12.5, and Task 3.48.0). `post-create.zsh` installs project
   dependencies, the Playwright Chromium browser, and the pinned OpenSpec and
   GitNexus CLIs with Bun.
4. Start development tasks from inside the container.

## Forwarded Ports

| Port | Service |
| ---- | ------- |
| 8000 | Backend |
| 5173 | Frontend |
| 6006 | Storybook |

## Files

| File | Purpose |
| ------ | --------- |
| `devcontainer.json` | Dev container metadata, ports, extensions, and settings. |
| `compose.yml` | Compose service (`app`) for the dev container. |
| `Containerfile.dev` | Dev-specific Dockerfile. |
| `Containerfile.dev.dockerignore` | Build-context exclusions for the dev image. |
| `keybindings.json` | Container-only keybindings copied into the remote user's machine profile at startup. |
| `post-create.zsh` | One-time setup script (runs after the container is created). |
| `post-start.zsh` | Startup script (applies keybindings each time the container starts). |

## Environment

The dev container loads runtime values from the repository-root `.env` and
optional `.env.local` files (with `.env.local` taking precedence).
Host keybindings remain in VS Code user settings; the container's keybinding
file is applied only inside the remote container.
