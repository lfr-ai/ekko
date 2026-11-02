# Framework and domain-type patterns

Loaded on demand from `python-conventions/SKILL.md` — read this only when the
task touches one of these specific topics.

## Domain Scalar Types

Pick the lightest tier that fits; shared types live in `core/types.py`. Each tier
has a fixed trigger:

```python
from typing import NewType, Self


# Tier 1 - validated value object: enforce a boundary invariant in __new__.
# The single value parameter is positional-only (/), mirroring the built-in
# int/str/float constructors this subclasses (see signature-patterns.md).
class MaxTokens(int):
    def __new__(cls, max_tokens: int, /) -> Self:
        if not 0 < max_tokens <= 1_000_000:
            raise ValueError("'max_tokens' must be in (0, 1_000_000]")
        return super().__new__(cls, max_tokens)


# Tier 2 - structural alias: a recurring compound shape, no scalar invariant.
type EmbeddingComponents = tuple[float, ...]
type JSONDict = dict[str, object]

# Tier 3 - decoupling alias: a core stand-in for an outer-layer enum value that
# core must not import (application/infrastructure use the concrete enum).
type ModelDeploymentName = str  # a ChatModel / EmbeddingModel value
type StrategyName = str  # a RagStrategy value

# Tier 4 - NewType: an opaque scalar id kept distinct for the checker, no invariant.
UserId = NewType("UserId", int)

# Tier 5 - bare primitive: local/measured/computed value, counts in arithmetic,
# free text; a containing value object validates it.
prompt_tokens: int
system_prompt: str
```

- A constrained **input** you set (a limit) is a value object (`MaxTokens`); a
  measured **output** you receive (a count) is a primitive validated by its
  container. That is why `MaxTokens` is a value object while token counts are not.
- Retrieval-specific application: `RetrievalQuery.max_context_tokens` is a
    constrained input budget and should use `MaxTokens`; diagnostics counters
    (`prompt_tokens`, `retrieved_chunks`) remain primitive `int` outputs.
- An internal knob sourced only from a validated module constant (e.g.
    `RAG_TOP_K: Final[int]`) does not cross a trust boundary and stays a bare
    primitive; `top_k`, `chunk_size`, `chunk_overlap` are `int`, not value objects.
- Never create a scalar type alias just for documentation (e.g.
  `PromptContent = str`) — use a primitive or promote to `NewType`/a value object.
- Add Pydantic hooks to a value object only when it is a model field (`Confidence`).
- `__new__`'s `Returns:` line is `Self: New validated <ClassName> instance.` when
  the stored value is unchanged after validation. Use a bespoke description only
  when `__new__` also transforms the input (a wrapper that strips separators
  from its argument reads `Self: Normalized <thing> in canonical form.`) — never
  reuse the generic wording once the return value's meaning has diverged from
  "the validated input, unchanged".

## Sync-to-Async Boundary

When the driver is synchronous (`psycopg2`, `pypdf`, an SDK with a blocking
poller), keep the repository/adapter synchronous and offload at the async call
site instead of forcing an async rewrite of the driver:

```python
import asyncio


async def get_entity(entity_id: int) -> Entity | None:
    """Retrieve entity by ID."""
    return await asyncio.to_thread(repository.get_by_id, entity_id)
```

Never call a blocking method directly inside `async def` — it blocks the event
loop for every other in-flight request. Prefer a library's native async client
(`httpx.AsyncClient`, `litellm.acompletion`) over wrapping a sync one. When a
loop awaits several independent calls, use `asyncio.gather(...)` instead of
sequential `await`s so they run concurrently:

```python
documents = await asyncio.gather(*(fetch(doc_id) for doc_id in document_ids))
```

## Concurrent Task Lifecycle

`asyncio.create_task` schedules a free-standing task with no automatic link to
the awaiting coroutine's own cancellation or error handling. If a sibling task
(`evaluation_task`) fails, or an outer `asyncio.wait_for`/`asyncio.timeout`
cancels the caller, tasks started with `create_task` and not yet awaited keep
running in the background — orphaned, still consuming I/O/API quota, and
liable to log "Task exception was never retrieved" once they finish. Guard
every multi-task fan-out with explicit cleanup:

```python
task_a = asyncio.create_task(handler_a.process(order))
task_b = asyncio.create_task(handler_b.process(order))
background_tasks = (task_a, task_b)

try:
    result_a = await task_a
    ...
    return _combine(result_a, await task_b)
except BaseException:
    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)
    raise
```

Prefer `asyncio.TaskGroup` (3.11+) for *new* fan-out code with no downstream
per-exception-type dispatch. Do **not** reach for it when the raised exception
must still be matched by concrete type further up the stack (for example a
FastAPI `exception_handler` keyed on `EmptyChatCompletionError`) —
`TaskGroup.__aexit__` wraps every propagated exception in an `ExceptionGroup`,
which no longer matches an `isinstance` check against the original type unless
every call site is migrated to `except*`. The manual try/except-cancel pattern
above preserves the original exception type while still avoiding orphaned tasks.

## Shared Async Client State

A client object shared across concurrent requests (bearer-token cache,
connection-pool warm-up, any other cached, lazily-refreshed field) must guard
its refresh with an `asyncio.Lock`, or concurrent callers (`asyncio.gather`)
each race to refresh it independently — a thundering herd of redundant
round-trips to the same upstream, and, without a lock, a data race across the
`await` points inside the refresh routine. Use double-checked locking so only
the first caller through pays the refresh cost and every other one reuses the
result once it lands:

```python
def _token_is_valid(self) -> bool:
    return (
        self._access_token is not None
        and self._token_expires_at is not None
        and datetime.now(UTC) < self._token_expires_at
    )


async def _ensure_token(self) -> None:
    if self._token_is_valid():
        return
    async with self._token_lock:
        if self._token_is_valid():  # re-check: another caller may have refreshed
            return
        ...  # fetch and cache the token + its expiry
```

## Production ASGI Runtime

Depend on `uvicorn[standard]` (not bare `uvicorn`) so `uvloop` and `httptools`
are installed automatically on Linux/macOS deployment targets — `uvloop` alone
is a 2-4x event-loop throughput improvement for an I/O-bound FastAPI app, at
zero code change since Uvicorn's `loop="auto"` (the default) picks it up when
present. The `standard` extra's own dependency markers already exclude
`uvloop` on Windows, so local dev on Windows installs cleanly without it.

## Async SQLAlchemy

Use async session and query patterns when the driver is async-native (e.g.
`asyncpg`). If the driver is sync (`psycopg2`), use the Sync-to-Async Boundary
pattern above instead of migrating the driver:

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select


async def get_entity(session: AsyncSession, entity_id: int) -> Entity | None:
    """Retrieve entity by ID."""
    stmt = select(Entity).where(Entity.id == entity_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_entity(session: AsyncSession, data: dict) -> Entity:
    """Create new entity."""
    entity = Entity(**data)
    session.add(entity)
    await session.commit()
    await session.refresh(entity)
    return entity
```

## Pydantic Models

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field


class ItemModel(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    description: Annotated[
        str | None,
        Field(
            default=None,
            min_length=1,
            max_length=500,
            description="Item description",
            examples=["Sample item"],
        ),
    ]
```

## Configuration & `from_config`

`*Settings` = an environment-sourced facet that *owns* a cohesive group of
prefixed env fields (e.g. `MYAPP_*`) — a `BaseSettings` subclass composed into
the app config. `*Config` = a complete, assembled configuration (`AppConfig`, the
environment classes) **or a consumer's structural view of it**.

A component built from configuration exposes `from_config(cls, config: _XConfig)`
where `_XConfig` is a private structural `Protocol` (same module) of only the
fields it reads. It never imports the app config — the config satisfies `_XConfig`
structurally (PEP 544).

```python
# Good: consumer owns a compact structural view named _<Component>Config
from typing import Protocol, Self


class _EmailClientConfig(Protocol):
    smtp_host: str
    smtp_password: SecretStr


class EmailClient:
    @classmethod
    def from_config(cls, config: _EmailClientConfig, /) -> Self:
        return cls(host=config.smtp_host, password=config.smtp_password)


# Bad: importing the concrete app config couples infrastructure to the config layer
from myapp.config import AppConfig


def from_config(cls, config: AppConfig, /) -> Self: ...


# Bad: naming the consumer view *Settings (reserved for field-owning facets)
class _EmailClientSettings(Protocol): ...
```

## Retry Policies

```python
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1.5, min=2, max=15),
    reraise=True,
)
def call_api() -> dict[str, object]: ...
```
