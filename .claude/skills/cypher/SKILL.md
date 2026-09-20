---
name: cypher
description: Write safe, efficient Cypher queries against any property-graph engine (GitNexus's embedded graph, Neo4j, Memgraph, Kùzu). Use when writing or reviewing a raw Cypher query — including `gitnexus_cypher`/`mcp_gitnexus_cypher` calls — covering parameterization, indexes, and EXPLAIN/PROFILE tuning.
---

# Cypher

Portable Cypher language conventions — independent of which graph engine runs
the query. In this repo the only active consumer is the GitNexus MCP `cypher`
tool; see the `gitnexus` skill family (`.agents/skills/gitnexus/`) for this
repo's concrete node/edge schema and worked query examples. This skill is the
language-level knowledge behind those queries, and applies equally to any
future real Neo4j/Memgraph work.

## Core patterns

- `MATCH (a)-[:REL]->(b)` for a directed pattern; add a label and property
  map (`(a:Label {prop: $value})`) to narrow the scan as early as possible.
- `OPTIONAL MATCH` for left-join semantics (keep unmatched rows with `null`),
  not `MATCH` followed by a manual null check.
- Bound every variable-length path (`[:REL*1..3]`) — an unbounded `*` walks
  the whole reachable graph and can hang on a large dataset.
- `WITH` to pipeline aggregation/filtering stages, the same way a SQL CTE
  chains `SELECT`s.
- Return only the properties you need (`RETURN a.name, a.filePath`), never a
  whole node/relationship object, to minimize data transfer.

## Safety: always parameterize

Never interpolate a variable into Cypher text — this is the same injection
class as SQL injection, and it applies even when the query is built
programmatically before being passed to `gitnexus_cypher` or a driver call.

```cypher
// Good — parameterized, plan-cacheable, injection-safe
MATCH (f:Function {name: $functionName}) RETURN f.filePath

// Bad — string-built, re-parsed every call, injectable if functionName
// ever comes from untrusted input
MATCH (f:Function {name: "` + functionName + `"}) RETURN f.filePath
```

## Performance

- Parameters over literals: a parameterized query reuses the cached
  execution plan; a literal forces a fresh parse/plan every call.
- Create an index/constraint on any property used in a frequent `MATCH`
  filter: `CREATE INDEX ... FOR (n:Label) ON (n.prop)`.
- Run `EXPLAIN` (plan only, no execution) or `PROFILE` (plan + real DB
  hits/rows) before trusting a query's cost. Look for `NodeIndexSeekByRange`
  in the plan (index used) vs. `NodeByLabelScan` (full label scan) or an
  unintended cartesian product (two `MATCH` clauses with no shared variable).
- Batch writes with `UNWIND $rows AS row ... IN TRANSACTIONS OF n ROWS`
  instead of one round-trip per row.

## Read vs write

- Read-only: `MATCH ... RETURN` — safe in a read transaction/replica.
- Write: `CREATE`, `MERGE`, `SET`, `DELETE` — needs a write transaction.
- `MERGE` matches on **every** property in its pattern — a partial match
  (e.g. matching only on `name` when the node also has an `id`) silently
  creates a duplicate node instead of matching the existing one.

## Anti-patterns

- Unbounded variable-length paths (`[:REL*]` with no upper bound).
- Returning whole nodes/relationships when two properties would do.
- Two independent `MATCH` clauses with no shared variable (cartesian
  product) instead of one connected pattern.
- Building the query string with f-strings/concatenation instead of `$params`.
- Using `CREATE` where `MERGE` was intended (silent duplicate nodes).

## References

- `.agents/skills/gitnexus/guide/SKILL.md` — this repo's concrete graph
  schema, `gitnexus_cypher` tool, and worked examples against it.
