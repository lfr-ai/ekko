---
description: Clean Architecture boundaries for Python source files
applyTo: "backend/src/ekko/**/*.py"
---

# Architecture Instructions

- Keep dependency direction inward — source-code deps always point **toward core**.
- **core/** must not import from `application`, `infrastructure`, `presentation`, or `ai`.
- **application/** must not import from `infrastructure` or `presentation`.
- **ai/** must not import from `infrastructure` or `presentation`.
- **presentation/** must not import from `infrastructure` (use DI via `composition/`).
- The **composition/** root (`container.py`, `app_factory.py`) is the only place that wires concrete implementations — it may import from any layer.
- Domain logic must never live in adapters or transport layers.
- Enums live in `core/enums/` (split by domain). Import via `from ekko.core.enums import X`.
- Concurrency primitives (`QueueManager`, `ThreadManager`) live in `infrastructure/concurrency/`.
- All dataclasses use `frozen=True, slots=True` (except `Container` which needs `cached_property`).
- Constants use `Final[type]` annotations.
