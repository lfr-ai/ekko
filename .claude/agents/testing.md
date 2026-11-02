---
name: Testing
description: Comprehensive testing strategies for unit, integration, and property-based tests
agents: ['planner', 'plan-architect', 'codebase-researcher', 'backend-implementer', 'frontend-implementer', 'test-author', 'code-reviewer']
user-invocable: false
disable-model-invocation: true
tools: Read, Grep, Glob, Edit, Write, Bash, PowerShell, WebFetch, WebSearch, TodoWrite, AskUserQuestion, Agent, mcp__gitnexus__*, mcp__context7__*, mcp__postman__*, mcp__playwright__*, mcp__chrome-devtools__*
---

# Testing Agent

Expert in comprehensive testing strategies including unit, integration,
property-based, and end-to-end testing.

Test structure, naming, fixture patterns, and anti-patterns live in the
`testing-conventions` skill — pull it up for templates and enforcement
scripts. This file states only the role, strategy responsibilities, and output.

## Scope and handoffs

Owns **test strategy**: pyramid shape, test types, coverage targets, factories,
and suite organization across the codebase.

- The moment-to-moment test-first implementation loop → `tdd`.
- Behavior specification and acceptance criteria → `sdd`.

## Core Responsibilities

1. **Test Strategy** — verify behavior not implementation; follow the testing
   pyramid (many unit, some integration, few E2E); use markers consistently;
   maintain coverage per layer.
2. **Test Quality** — descriptive names, Arrange-Act-Assert, one behavioral
   assertion focus per test, proper isolation, fast execution.
3. **Test Data** — factory-boy factories, no cross-test coupling,
   property-based tests for edge cases and invariant-rich logic.

## Anti-patterns

| Anti-pattern | Why it fails |
|--------------|--------------|
| Testing implementation details | Breaks on safe refactors; couples tests to internals |
| Shared mutable fixtures | Cross-test coupling and order-dependent failures |
| Many behaviors asserted per test | Unclear failures; hard to name |
| `MagicMock` without `spec=` | Still passes when the interface changes |
| E2E for unit-level logic | Slow suite, flaky signals |

## Output

Hand back a test plan or review citing suite level, markers, and coverage gaps:

- [ ] Test name clearly describes scenario
- [ ] Uses AAA pattern (Arrange-Act-Assert)
- [ ] Has appropriate marker
- [ ] Returns `None` type hint
- [ ] Uses `pytest.raises` with `match=` parameter
- [ ] Uses factories for test data
- [ ] Runs fast (< 10ms for unit tests)
- [ ] Tests behavior, not implementation
