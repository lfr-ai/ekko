# Decisions

Durable agent-development decisions — why the agentic setup or a convention is
shaped the way it is. One entry per decision; link the change or discussion
that established it instead of re-arguing it here.

- GraphQL stays a single read-only `promptCatalog` query
  (`backend/src/ekko/presentation/graphql/`); REST + SSE cover every command
  and streaming surface. Do not grow the GraphQL schema without a verified
  consumer need — see the `api-contracts` skill.
- Skills are canonical under `.agents/skills/` and mirrored byte-identically to
  `.github/skills/` and `.claude/skills/`; every instruction pairs with a
  `.claude/rules/` file of equal scope — see the `agent-config` skill.
