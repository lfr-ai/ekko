# Docstring patterns

Loaded on demand from `python-conventions/SKILL.md` — read this only when
deciding whether a docstring should stay minimal or expand.

## Function and method docstrings

### The brevity test

A section earns its place only if it carries meaning the signature can't: a
non-obvious constraint, a return value whose semantics aren't the type alone,
or an exception the caller must anticipate. If `Args`/`Returns` would only
restate a parameter/return type already visible in the signature, drop the
section and keep a one-line summary. This applies beyond properties — test
every function, not just accessors.

The same test applies to *why*-rationale: a docstring documents the contract
(what the function does, its params, return, and raised errors), never the
design reasoning behind it. Implementation rationale belongs in a short code
comment next to the relevant lines (see the `cognitive-load` skill), not
padded into the docstring summary.

**Sections are all-or-nothing, never a subset.** Once a docstring uses ANY
structured section, every warranted section must be present: `Args` for
every parameter (ruff `D417` rejects a partial `Args` listing only "the
interesting" params — drop it and go one-liner instead), `Returns` whenever
the return isn't `None` and isn't obvious from the type alone, and `Raises`
whenever the function raises a checked exception. Never keep one warranted
section while dropping another because it "felt obvious enough". The only
exempt shape is a bare one-line summary with zero sections.

```python
# Bad: Args/Returns restate what the signature already says
@property
def start_date(self) -> date:
    """First day of the date range.

    Returns:
        date: The start date.
    """


# Good: one-liner; Raises kept because the caller must anticipate it
@property
def start_date(self) -> date:
    """First day of the date range."""


def days_until(self, reference_date: date) -> int:
    """Whole days elapsed from the start date to a reference date.

    Args:
        reference_date (date): Date to measure the span to.

    Returns:
        int: Whole days elapsed since the start date.

    Raises:
        ValueError: If the reference date precedes the start date.
    """
```

## Module and class docstrings

Default to a single-line summary for both, unless explicitly asked for more —
the same brevity test above applies one level up. Expand past
one line only for real, STABLE information a reader can't already get from
the code: a genuine `Attributes:` section for public fields
(dataclass/NamedTuple/enum members), a non-obvious usage note, or a
behavioral characteristic (Google: "Docstrings that do not provide any new
information should not be used."). Never expand purely to restate the
class/module name in more words.

**Never bake in volatile specifics that will go stale.** A literal number
mirroring a constant (pool size, timeout, retry count, byte limit), or a
step-by-step restatement of the algorithm, silently lies once that constant
or flow changes — state the stable behavior instead; the code is the source
of truth for the exact value.

```python
# Good: no attributes, no usage nuance -> one line
class ChatClient(ChatClientPort):
    """Chat client implementing ChatClientPort via LiteLLM."""


# Good: stable behavior described generically -> multi-line earns its place,
# no literal numbers that duplicate _POOL_SIZE / _POOL_RECYCLE_SECONDS
class DatabaseManager:
    """Database manager for connection pooling and session lifecycle.

    Connections are pooled with overflow capacity and periodic recycling to
    avoid stale connections; each connection is pre-pinged before reuse.
    """


# Bad: literal config values duplicate the module's own constants -> goes
# stale the moment _POOL_SIZE/_POOL_OVERFLOW_LIMIT/_POOL_RECYCLE_SECONDS change
class DatabaseManager:
    """Database manager for handling database connections with optimized pooling.

    Connection Pool Configuration:
    - pool_size: 8 persistent connections
    - max_overflow: 12 additional connections for burst traffic
    - pool_recycle: 3600s (1 hour) - prevents stale connections
    """
```
