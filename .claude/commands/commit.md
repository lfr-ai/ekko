Review the current git diff and create a well-structured conventional commit.

Steps:

1. Run `git diff --staged` to see staged changes (or `git diff` if nothing staged)
2. Analyze the nature of changes: feat/fix/refactor/docs/test/chore
3. Determine the scope: backend/frontend/infra/registry/scripts/config/ai/deps/ddd/sdd/tdd
4. Write a concise commit message following Conventional Commits format:
   - Subject: `type(scope): imperative description` (max 72 chars)
   - Body: explain WHY, not WHAT (wrap at 88 chars)
   - Footer: reference issues if applicable

Rules:

- Never combine unrelated changes in one commit
- Use `feat` only for new user-visible functionality
- Use `fix` only for bug fixes
- Use `refactor` for code restructuring without behavior change
- Use `!` suffix for breaking changes: `feat(backend)!: description`
- Do NOT add `--no-verify` or skip hooks
- Verify `.env.example` is updated if new env vars were added
- Verify `registry/naming_registry.json` is updated if new field names were added
- Verify `backend/src/ekko/core/registry_constants.py` is regenerated after registry changes
