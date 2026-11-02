# API versioning strategies

Choosing when and how to version is a bigger decision than the mechanism —
default to additive, non-breaking evolution and reserve a new version for a
genuine break.

## Prefer additive evolution first

Most schema changes do not need a version bump:

- Adding an optional request field or a new response field is non-breaking.
- Adding a new endpoint, method, or query parameter is non-breaking.
- Loosening validation (accepting more) is non-breaking; tightening it
  (rejecting previously-accepted input) is breaking.

Only version when the change cannot be made additive: removing/renaming a
field, changing a field's type or semantics, changing an error shape,
changing pagination/sort defaults, or changing authentication requirements.

## Mechanisms compared

| Mechanism | Example | Pros | Cons |
| --- | --- | --- | --- |
| URI path | `/v2/orders` | Cache-friendly, visible in logs/docs, easy to route | Duplicates routers per version; "URI should identify a resource, not its representation" purists object |
| Header | `Api-Version: 2` | Keeps URIs stable | Invisible in logs/browser; easy for clients to forget |
| Media type | `Accept: application/vnd.myapp.v2+json` | Most RESTfully "correct"; content negotiation | Least tooling support; hardest for consumers to discover |
| Query parameter | `?api-version=2` | Simple to add later | Easy to omit; caches may ignore it |

Default to URI path versioning unless the project already has an established
convention (`AGENTS.md` / `PROJECT.md` take precedence) — it is the easiest for
consumers to discover, route, and cache correctly.

## Deprecation signaling

When a version or endpoint is scheduled for removal:

- Keep an accidental public-path rename additive: expose the intended path in
  OpenAPI and retain the former path as a hidden compatibility alias. Exercise
  both paths in an HTTP contract test until the alias has a published sunset
  date.
- Return the `Deprecation` response header (RFC 8594-style) once deprecation
  begins, and `Sunset` with the planned removal date once one is committed.
- Document the migration path in the OpenAPI description, not only in a
  changelog nobody reading the live docs will see.
- Keep the deprecated version fully functional until the sunset date — a
  "soft" breaking change (silently degraded behavior) is worse than a clean
  removal on the announced date.

## Breaking vs non-breaking quick reference

| Change | Breaking? |
| --- | --- |
| Add optional request field | No |
| Add response field | No (clients must ignore unknown fields) |
| Remove/rename a field | Yes |
| Change a field's type (e.g. `str` → `int`) | Yes |
| Make an optional field required | Yes |
| Change enum values accepted | Depends — adding a value is usually safe; removing one is breaking |
| Change default sort/pagination | Yes (silently) |
| Change error response shape | Yes |
| Change status code for an existing case | Yes |

## Related

- `assets/route.py.template` — a versioned route module skeleton.
- `backend-structure` skill — router/dependency conventions this template
  follows.
