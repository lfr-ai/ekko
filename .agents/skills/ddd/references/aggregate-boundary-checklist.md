# Aggregate boundary checklist

Sizing an aggregate wrong is the most expensive DDD mistake — too large and
every edit contends on the same lock/row; too small and invariants that must be
atomic end up split across a transaction. Use this checklist when drawing or
reviewing an aggregate boundary.

## 1. Find the true invariant, not the object graph

Ask: "what rule must never be violated, even under concurrent writes?" Only
data required to enforce that rule belongs inside the boundary.

- Good: "an order's line-item total must never exceed its credit limit" →
  `Order` + `OrderLine` are one aggregate.
- Bad: "an order belongs to a customer" is a *reference*, not an invariant —
  `Customer` stays a separate aggregate, referenced by `customer_id`.

## 2. One aggregate = one transaction = one repository

- A single command handler commits at most one aggregate per transaction.
- If a use case appears to need atomic writes across two aggregates, either the
  boundary is wrong (merge them) or consistency is genuinely eventual (emit a
  domain event and let a second handler apply the follow-up change).
- `core/ports/` therefore exposes exactly one repository protocol per
  aggregate root — never a repository keyed by a child entity.

## 3. Reference other aggregates by ID only

Never hold a full object reference to another aggregate root; store its
identifier (a `NewType` opaque ID, per the project's custom-type tiers) and
look it up through its own repository when needed. This keeps aggregates
independently loadable and prevents accidental cascading writes.

## 4. Keep the aggregate small

Prefer several small aggregates connected by IDs and domain events over one
"god aggregate" that owns most of the object graph. Symptoms of an oversized
aggregate:

- Loading it requires joining many unrelated tables.
- Most transactions only touch one child entity, not the invariant.
- Two features never observed to race still share a lock because they share
  an aggregate.

## 5. Cross-aggregate consistency is eventual, and explicit

When aggregate B must react to a change in aggregate A:

1. A's command handler commits A's transaction and returns/publishes a domain
   event (see `assets/domain_event.py.template`).
2. A separate handler consumes the event and issues B's own command.
3. Document the acceptable staleness window; do not fake atomicity with a
   distributed transaction across two repositories.

## 6. Review triggers

Re-examine an aggregate boundary when:

- A new invariant needs data living in a different aggregate today.
- A repository method starts taking multiple aggregate IDs at once.
- Two features consistently need to change two aggregates in the same request.

## Related

- `assets/repository_protocol.py.template` — one-repository-per-aggregate shape.
- `assets/domain_event.py.template` — the eventual-consistency mechanism.
- `clean-architecture` skill — where aggregates sit in the layer hierarchy.
