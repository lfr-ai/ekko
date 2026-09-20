---
name: litellm
description: 'Use LiteLLM as the unified client behind the core ChatPort — provider routing, retries/fallbacks, structured output, streaming, and cost/token tracking. Use when adding or changing an LLM client, provider deployment, or completion call.'
---

# LiteLLM Skill

LiteLLM gives one call shape (`litellm.acompletion`) across OpenAI, Azure
OpenAI, Anthropic, and other providers — the reason to reach for it instead of
a provider SDK directly is provider-swap without touching call sites. This
This repo's adapter lives at `infrastructure/clients/chat.py`, implementing
the `core/ports/` `ChatPort`.

## Port boundary

Define the capability as a core port (`ChatPort`, a `Protocol`); the
Infrastructure adapter is the only place that imports `litellm`. Never let a
`litellm` type (its message dict shape, its response object, its exception
classes) cross into core or application — translate to/from domain types at
the adapter boundary, matching the `clean-architecture` skill's ports
convention.

```python
# core/ports/chat.py — core, stdlib-only
class ChatPort(Protocol):
    async def achat(self, *, messages: Sequence[ChatMessage]) -> ChatCompletion: ...

# infrastructure/clients/chat.py — the only module that imports litellm
class ChatClient(ChatPort):
    """Chat client implementing ChatPort via LiteLLM."""
```

## Provider and deployment naming

Use a decoupling `type` alias (see the `python-conventions` skill's Hard Rule
16 guidance, e.g. `ModelDeploymentName`) for the outer-layer provider/deployment
string (e.g. `"azure/gpt-4o"`) instead of a bare `str` at every call site — it
documents intent without adding a validated value object for a value core
never branches on.

## Retries, timeouts, and fallbacks

- Pass `num_retries` and `timeout`/`request_timeout` on every `acompletion`
  call — a hung upstream provider should not hang the request indefinitely.
- Use `litellm.Router` (not a hand-rolled retry loop) when a call should fall
  back across multiple deployments (e.g. two Azure regions of the same
  model) — it already implements cooldown-aware fallback and load balancing.
- Catch LiteLLM's typed exceptions (`litellm.exceptions.*`) at the adapter
  boundary only, and re-raise as a core-defined exception the application
  layer can depend on without importing `litellm`.

## Structured output

Prefer the provider's native structured-output/JSON-schema mode
(`response_format`) over prompt-engineered JSON — validate the parsed result
against a Pydantic model in the adapter before it crosses back into core, and
raise a core-defined validation error on mismatch rather than passing a
partially-validated dict inward.

## Cost and token tracking

- Read `response.usage` (prompt/completion/total tokens) instead of counting
  tokens client-side — it reflects what the provider actually billed.
- For cross-provider cost estimates use `litellm.completion_cost(response)`
  rather than hand-maintained per-provider price tables that drift stale.
- Record token/cost figures through a metrics port boundary (see the
  `observability-stack` skill) — never a raw `prometheus_client` call from
  the adapter that already implements `ChatPort`.

## Noise control

Set `litellm.suppress_debug_info = True` at process start and route its own
`"LiteLLM"`-named logger through the app's stdlib logging configuration
(silence or downgrade it explicitly) — left at default verbosity it emits
provider-internal debug lines on every call.

## Testing

- Unit/property tests mock `ChatPort` at the application boundary — never
  call a real provider from a fast test tier.
- An integration test that must exercise the real adapter records a fixture
  response once and replays it (or hits a local/sandboxed provider), instead
  of making a live network call on every run — matches the
  `testing-conventions` skill's speed-first stance.

## Observability

Wrap a completion call in a span when it is not already covered by an
HTTP-client auto-instrumentor (see the `observability-stack` skill); record
provider, deployment name, and latency as span/log attributes — never the
prompt or completion content itself (data-boundary concern, not just size).

## References

- [LiteLLM documentation](https://docs.litellm.ai/) — providers, Router,
  retries/fallbacks, and cost tracking.
- [LiteLLM structured outputs](https://docs.litellm.ai/docs/completion/json_mode)
