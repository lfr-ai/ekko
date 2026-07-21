---
name: gitnexus-impact-analysis
description: "Use when the user wants to know what will break if they change something, or needs safety analysis before editing code. Examples: \"Is it safe to change X?\", \"What depends on this?\", \"What will break?\""
---

# Impact Analysis with GitNexus

## When to Use

- "Is it safe to change this function?"
- "What will break if I modify X?"
- "Show me the blast radius"
- "Who uses this code?"
- Before making non-trivial code changes
- Before committing — to understand what your changes affect

## Workflow

```
1. gitnexus_impact({target: "X", direction: "upstream"})  → What depends on this
2. READ gitnexus://repo/{name}/processes                   → Check affected execution flows
3. gitnexus_detect_changes()                               → Map current git changes to affected flows
4. Assess risk and report to user
```

> If "Index is stale" → run `npx gitnexus analyze` in terminal.

## Checklist

```
- [ ] gitnexus_impact({target, direction: "upstream"}) to find dependents
- [ ] Review d=1 items first (these WILL BREAK)
- [ ] Check high-confidence (>0.8) dependencies
- [ ] READ processes to check affected execution flows
- [ ] gitnexus_detect_changes() for pre-commit check
- [ ] Assess risk level and report to user
```

## Understanding Output

| Depth | Risk Level       | Meaning                  |
| ----- | ---------------- | ------------------------ |
| d=1   | **WILL BREAK**   | Direct callers/importers |
| d=2   | LIKELY AFFECTED  | Indirect dependencies    |
| d=3   | MAY NEED TESTING | Transitive effects       |

## Risk Assessment

| Affected                       | Risk     |
| ------------------------------ | -------- |
| <5 symbols, few processes      | LOW      |
| 5-15 symbols, 2-5 processes    | MEDIUM   |
| >15 symbols or many processes  | HIGH     |
| Critical path (auth, AI pipe)  | CRITICAL |

## Tools

**gitnexus_impact** — the primary tool for symbol blast radius:

```
gitnexus_impact({
  target: "ChatService",
  direction: "upstream",
  minConfidence: 0.8,
  maxDepth: 3
})

→ d=1 (WILL BREAK):
  - stream_handler (src/ekko/presentation/api/routes/stream.py:42) [CALLS, 100%]
  - graphql_chat_mutation (src/ekko/presentation/graphql/mutations.py:15) [CALLS, 100%]

→ d=2 (LIKELY AFFECTED):
  - Container.chat_service (src/ekko/composition/container.py:22) [CALLS, 95%]
```

**gitnexus_detect_changes** — git-diff based impact analysis:

```
gitnexus_detect_changes({scope: "staged"})

→ Changed: 5 symbols in 3 files
→ Affected: ChatFlow, SummarizationPipeline, AudioCapture
→ Risk: MEDIUM
```

## Example: "What breaks if I change ChatService?"

```
1. gitnexus_impact({target: "ChatService", direction: "upstream"})
   → d=1: stream_handler, graphql_mutation (WILL BREAK)
   → d=2: Container, app_factory (LIKELY AFFECTED)

2. READ gitnexus://repo/ekko/processes
   → ChatFlow and SummarizationPipeline touch ChatService

3. Risk: 2 direct callers, 2 processes = MEDIUM
```

## OpenSpec Integration

When impact analysis reveals a significant blast radius, use OpenSpec to
formalize the change:

1. **Assess impact** → `gitnexus_impact({target, direction: "upstream"})`
2. **Check affected specs** → `openspec list --specs` and review relevant domain
3. **Propose change** → `/opsx:propose <change-name>` with impact context
4. **Design includes blast radius** → Reference GitNexus output in design.md
5. **Verify after implementation** → `/opsx:verify` + `gitnexus_detect_changes()`
