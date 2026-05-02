# Verify Copilot + Claude + MCP Integration

This checklist verifies that Ekko's agent customizations, GitHub Copilot setup,
MCP servers, and Warp workflows are correctly wired.

## 1) Verify GitHub Copilot and model selection

1. Confirm GitHub Copilot and GitHub Copilot Chat extensions are installed.
2. Open Copilot Chat in VS Code.
3. Use the model picker and select a Claude model available to your account.
4. Ask: `What model are you using?`

Expected:

- Response confirms a Claude model.
- Chat works without authentication or entitlement errors.

## 2) Verify repository instructions are loaded

Ekko uses all three repository customization layers:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md` (plus `CLAUDE.md` compatibility)

Checks:

1. Open chat from this repository context.
2. Ask: `What architecture rules must be followed in this repo?`
3. In chat references, confirm instruction files are cited.
4. Open Chat diagnostics and verify no instruction-file parse errors.

Expected:

- Response cites Clean Architecture boundaries and project conventions.
- Diagnostics show instruction files loaded successfully.

## 3) Verify custom agents and skills discovery

Checks:

1. In chat, open the agent picker and confirm workspace agents appear from `.github/agents`.
2. Confirm skills are discovered from `.github/skills`, including `gitnexus` and `openspec`.
3. Ask role-focused prompts like:
   - `As a backend-python agent, outline changes for a repository refactor.`
   - `Use gitnexus skill to describe blast radius analysis steps.`

Expected:

- Custom agents are selectable.
- Skills are discoverable and can be invoked by relevance/slash command.

## 4) Verify MCP server wiring

MCP servers are configured in `.vscode/mcp.json`.

Checks:

1. Open MCP server list in VS Code and verify these entries:
   - `context7`
   - `shadcn`
   - `gitnexus`
2. Start servers and trust prompts as needed.
3. Verify tool availability in chat tool picker.

Expected:

- Servers start cleanly.
- No MCP configuration errors in logs.
- Tools are available to chat.

## 5) Verify GitNexus knowledge graph readiness

Checks:

1. Confirm `.gitnexus/config.json` exists.
2. Run GitNexus index command from terminal (`gitnexus analyze`) if CLI is installed.
3. Check status (`gitnexus status`).

Expected:

- Index initializes successfully.
- Status reports healthy/ready graph state.

## 6) Verify Warp + zsh + Oh My Zsh workflow

Checks:

1. Run `task tools:warp:install`.
2. Open Warp and launch project profile.
3. Confirm shell with `echo $SHELL` reports zsh (macOS/Linux/WSL).
4. Run Warp workflows (e.g., `task dev`, `task test`, `task check`).

Expected:

- Warp loads project workflows.
- zsh environment is active and stable.

## 7) Verify CodeRabbit configuration

Checks:

1. Confirm `.coderabbit.yaml` exists.
2. Open file and validate core sections (`reviews`, `path_instructions`, filters).
3. In PR flow, ensure CodeRabbit is installed and active for repository reviews.

Expected:

- Config file is valid and repository-specific.
- PR reviews can be triggered/received in GitHub.

## Fast pass criteria (TL;DR)

You are fully integrated when all are true:

- Copilot chat uses Claude model successfully.
- Instruction files are loaded and referenced in responses.
- Custom agents/skills are discovered.
- MCP servers start and tools appear in chat.
- GitNexus config is present and indexing is healthy.
- Warp workflows run with zsh/OMZ shell setup.
- CodeRabbit config is valid and active for PR review.
