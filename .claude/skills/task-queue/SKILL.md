---
name: task-queue
description: Run background and scheduled work with Celery and Redis — broker/result-backend setup, idempotent task design, retries/backoff, Beat scheduling, and the FastAPI-BackgroundTasks-vs-Celery decision. Use when adding asynchronous jobs, workers, or periodic tasks to a backend.
---

# Task queue (Celery + Redis)

Move slow, retryable, or scheduled work off the request path. Keep task bodies
thin: they orchestrate application use cases and never embed business rules or
transport concerns (mirror the `backend-structure` boundaries).

Do not add Celery/Redis to a project that does not need out-of-process work. For
a single in-process "fire and forget" after the response, FastAPI's own
`BackgroundTasks` is enough. Reach for Celery when you need durability across
restarts, retries, scheduling, fan-out, or a separately scaled worker pool.

## When Celery, when not

| Need | Use |
| --- | --- |
| Run after the response, same process, best-effort, no durability | FastAPI `BackgroundTasks` |
| Durable, retryable, or scheduled work; separate worker scaling | Celery + Redis |
| CPU-bound parallelism only, no queue | `asyncio.to_thread` / a process pool |

## App and broker

- One `Celery(...)` app in a dedicated module (`myapp/tasks/app.py`), built from
  config through a `from_config` view (Hard Rule 20) — never read env directly.
- Redis serves as broker (`broker_url`) and, when results are needed, result
  backend (`result_backend`). Set `result_expires` so results self-evict; set
  `task_ignore_result=True` for fire-and-forget tasks that never read a result.
- Pin serialization to JSON (`task_serializer`, `result_serializer`,
  `accept_content=["json"]`) — never `pickle` for untrusted or cross-service
  messages. Set `enable_utc=True` and an explicit `timezone`.
- `task_acks_late=True`, `task_reject_on_worker_lost=True`, a bounded
  `worker_prefetch_multiplier` (1 for long tasks), and
  `broker_connection_retry_on_startup=True` so a crash redelivers work.

## Task design

- Name tasks explicitly (`@shared_task(name="myapp.ingest.document")`); use
  `shared_task` so tasks import safely without the app instance.
- Pass identifiers, never ORM objects or large payloads — re-fetch inside the
  task to avoid acting on a stale snapshot.
- Enqueue only after the DB commit: Celery 5.4+ `Task.delay_on_commit(...)` (or
  `transaction.on_commit`), so a rolled-back transaction never leaves a task
  pointing at a row that does not exist.
- Make tasks idempotent (a natural key, an upsert, or a processed-marker) —
  `acks_late` means a task can run more than once. Add a timeout to every
  network/IO call; never block a worker indefinitely.
- Prefer many small tasks and Canvas primitives (`chain`, `group`, `chord`) over
  one long task; never call `.get()` on a subtask inside a task (deadlock).

## Reliability and retries

- Declarative retries: `@shared_task(bind=True, autoretry_for=(TransientError,),
  retry_backoff=True, retry_backoff_max=600, retry_jitter=True, max_retries=5)`.
  Exclude non-retryable errors with `dont_autoretry_for`.
- Raise `self.retry(exc=...)` for conditional retries; raise `Reject`/`Ignore`
  for poison messages and route them to a dead-letter queue.
- Redact secrets in monitoring with `argsrepr`/`kwargsrepr` at call sites; never
  put credentials in task arguments.

## Scheduling

- Periodic work uses Celery Beat (`beat_schedule` or a database scheduler). Run
  Beat as a single process — two schedulers double-fire. Keep scheduled tasks
  idempotent and short; hand off to normal tasks for real work.

## Observability and ops

- `logging.getLogger(__name__)` (stdlib, Hard Rule 15) inside tasks; enable
  `task_track_started` for long jobs. Export worker/queue metrics to Prometheus
  (`observability-stack`): queue depth, task latency, failure rate.
- Route long-running and short tasks to dedicated queues/workers; set soft and
  hard `time_limit`s to bound stragglers.

## Guardrails

- Workers and clients must run identical code (the task registry is name-based).
- No business logic in a task body — call an application use case.
- One broker; do not mix Redis and RabbitMQ semantics in one app without reason.

Copy-and-rename starting point:
[`assets/celery_app.py.template`](assets/celery_app.py.template).
