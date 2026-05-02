---
description: Investigate errors systematically using project-aware debugging.
---

Debug the reported error or unexpected behavior systematically.

## Investigation steps

### 1. Reproduce and isolate

- Identify the exact error message, traceback, or unexpected output.
- Determine which layer the error originates from (`core/`, `infrastructure/`, `application/`, `presentation/`).
- Check if the error is in production code or test code.

### 2. Trace the call chain

- Follow the dependency direction: `presentation -> application -> infrastructure/ai -> core`.
- Identify which service, handler, or adapter is involved.
- Check the `Container` wiring in `composition/` for misconfigured dependencies.

### 3. Common root causes

Check these frequent issues in order:

- **Import errors** -- circular imports or layer boundary violations.
- **DI misconfiguration** -- missing `@cached_property` in `Container`, wrong protocol binding.
- **Async issues** -- missing `await`, mixing sync/async, wrong event loop.
- **Type mismatches** -- wrong DTO mapping, missing field in dataclass.
- **Database issues** -- missing migration, stale SQLite file (try `task db:reset`).
- **Config issues** -- missing `EKKO_` env var, wrong settings class loaded.

### 4. Verify with project tools

```bash
task typecheck     # Type errors across the codebase
task lint          # Import and style violations
task test:unit     # Verify unit tests still pass
task db:migrate    # Ensure DB schema is current
```

### 5. Check recent changes

- Review `git diff` and `git log` for recent changes near the error site.
- Check if a recent refactor broke a protocol contract or moved a dependency.

## Output

Provide:
- **Root cause** -- what is actually wrong and why.
- **Fix** -- concrete code change with file paths.
- **Verification** -- which `task` commands to run to confirm the fix.
