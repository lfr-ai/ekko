---
name: jinja2
description: Render Jinja2 templates safely and idiomatically — autoescaping, StrictUndefined, sandboxing untrusted template sources, and template/logic separation. Use when adding or reviewing any Jinja2-rendered HTML, email, or generated-report/config template (FastAPI `Jinja2Templates`, a standalone `Environment`, etc.).
---

# Jinja2

`jinja2` is a direct dependency for rendering real output (HTML pages,
emails, generated reports/config) — **not** for prompt bodies. Prompt
templates under `src/**/prompts/**/*.md` intentionally use plain
`{placeholder}` string substitution, never Jinja2; see
[`prompt.instructions.md`](../../instructions/prompt.instructions.md) and
`openspec/config.yaml`. Do not introduce a Jinja `Environment` into the
prompt-registry pipeline — this skill governs every *other* Jinja2 use.

## Environment setup

- Build **one** shared `Environment` (or FastAPI's
  `fastapi.templating.Jinja2Templates`) per app at startup — never a fresh
  `Environment` per request/call; it recompiles and re-parses every template.
- Always set `autoescape=select_autoescape([...])` for HTML/XML output — this
  is the default XSS defense; only wrap explicitly-trusted content in
  `markupsafe.Markup(...)` to bypass it.
- Set `undefined=jinja2.StrictUndefined` so a typo'd variable name raises at
  render time instead of silently rendering an empty string.

```python
from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape

templates_env = Environment(
    loader=PackageLoader("myapp", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
    undefined=StrictUndefined,
)
```

## Security

- Autoescaping protects against untrusted **variables**; it does nothing for
  an untrusted **template source**. If the template body itself ever comes
  from user input or an external source, render it through
  `jinja2.sandbox.SandboxedEnvironment`/`ImmutableSandboxedEnvironment`,
  never the plain `Environment`.
- Never call `Environment().from_string(user_supplied_text)` — that is
  server-side template injection (SSTI), not just an XSS risk.
- Keep templates as files under a dedicated `templates/` directory loaded via
  `PackageLoader`/`FileSystemLoader`; reserve `DictLoader` for tests.

## Keep logic out of templates

Pass a fully-prepared view model/DTO into `render()`; a template only
formats and iterates, it never computes business rules — this mirrors the
existing thin-Presentation convention in `backend-structure`.

```jinja
{# Good — formats a precomputed value #}
<p>Total: {{ order.formatted_total }}</p>

{# Bad — business logic (currency conversion, tax) lives in the template #}
<p>Total: {{ (order.subtotal * 1.25) | round(2) }} DKK</p>
```

Use `{% macro %}` for a repeated fragment (a row, a card) instead of
copy-pasting the same block across templates.

## Testing

Render with representative and edge-case context and assert on the output
string (or a parsed DOM for HTML) — not on internal template mechanics.

## Anti-patterns

- A fresh `Environment` built per request instead of one shared instance.
- Autoescape left off for HTML output, or turned off broadly instead of
  wrapping the one value that's genuinely pre-sanitized in `Markup(...)`.
- Rendering a template string built from user/external input directly with
  the plain (non-sandboxed) `Environment`.
- Business logic, currency/date formatting math, or DB calls inside a
  template instead of on the view model passed in.
- Reaching for Jinja2 to template a prompt body — use the prompt registry's
  plain `{placeholder}` substitution instead.
