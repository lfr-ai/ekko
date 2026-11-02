---
paths:
  - "**/*.jinja"
  - "**/*.jinja2"
  - "**/*.j2"
  - "**/templates/**/*.html"
  - "**/templates/**/*.xml"
---

# Jinja2 templates

- Render HTML/XML through one application-owned environment configured with
  autoescaping and `StrictUndefined`; never create an environment per request.
- Treat template source as trusted code. Never render user-supplied template text
  with a plain environment; use a sandbox only when external template sources are
  an explicit requirement.
- Pass a prepared, typed view model. Templates format, branch, and iterate; they
  do not query databases, call services, calculate business rules, or read env.
- Escape by default. Mark content safe only at the narrow point where its
  sanitization is proven, and never concatenate markup from untrusted values.
- Extract repeated presentation fragments into macros/includes and test rendered
  output with representative, missing, and hostile values.
- Do not use Jinja2 for prompt-registry templates unless that registry explicitly
  adopts it; follow the `jinja2` skill for environment and security details.
