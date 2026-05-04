---
paths:
  - "**/*.{sh,ps1}"
---

# Shell Script Conventions

- Bash: always `set -euo pipefail`
- Quote all variables: `"$var"` not `$var`
- Keep `.sh` and `.ps1` behavior aligned when both variants exist
- Use `"$CLAUDE_PROJECT_DIR"` for portable project-root paths in hooks
- Hook scripts must output valid JSON to stdout for Claude/Copilot integration
- Use `exit 0` for success, `exit 2` for blocking errors
