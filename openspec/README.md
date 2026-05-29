# OpenSpec in Ekko

This repository uses OpenSpec for behavior-first planning of non-trivial work.

## Repository layout

- `openspec/specs/` — source-of-truth behavior specs
- `openspec/changes/` — in-flight changes (proposal/design/tasks/spec deltas)
- `openspec/changes/archive/` — completed and archived changes
- `openspec/config.yaml` — project-level OpenSpec defaults and rules

## Recommended flow (core profile)

1. `/opsx:explore` (optional)
2. `/opsx:propose <change-name>`
3. `/opsx:apply <change-name>`
4. `/opsx:sync <change-name>`
5. `/opsx:archive <change-name>`

## Expanded flow (optional)

If expanded commands are enabled in your OpenSpec profile:

1. `/opsx:new <change-name>`
2. `/opsx:continue` or `/opsx:ff`
3. `/opsx:apply <change-name>`
4. `/opsx:verify <change-name>`
5. `/opsx:archive <change-name>`

## Authoring standards

- Keep specs behavior-focused and testable.
- Use requirement deltas under `ADDED`, `MODIFIED`, and `REMOVED`.
- Keep implementation details in `design.md` and `tasks.md`.
- Keep each change focused to one logical unit of work.
