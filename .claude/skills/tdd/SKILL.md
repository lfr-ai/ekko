---
name: tdd
description: Test-Driven Development Red-Green-Refactor methodology. Use when implementing features test-first, fixing bugs with regression tests, or refactoring with test safety nets.
---

# Test-driven development

Use short Red-Green-Refactor cycles with the repository's declared test runner.
Load `testing-conventions` for Python or `frontend/testing` for React/TypeScript;
this shared skill defines the method, not framework syntax.

## Cycle

```text
RED → GREEN → REFACTOR → repeat
```

1. **Red** — add the smallest test that describes one observable behavior. Run
     it and confirm it fails for the intended reason, not setup noise.
2. **Green** — implement only enough production behavior to pass that test. Do
     not add speculative abstractions, options, or unrelated cleanup.
3. **Refactor** — improve names, duplication, and structure while the focused
     test remains green. Run the relevant broader suite before the next slice.

If a cycle cannot be completed quickly, split the behavior into a thinner
vertical slice. Compilation/type failures may be a valid red state when adding a
new typed interface, but the test must still express the desired behavior.

## Test design

- Name the scenario and expected outcome; avoid implementation vocabulary.
- Use concrete inputs and assert public outcomes, state transitions, emitted
    events, or boundary calls—not private fields or incidental call order.
- Arrange, act, and assert clearly. Keep one behavioral reason for failure.
- Prefer small protocol/interface-conforming fakes. Use mocks only at boundaries
    where interaction itself is the contract.
- Keep tests deterministic and independent of execution order, wall clock,
    network, developer state, and shared mutable fixtures.
- Select the lowest-cost test level that proves the behavior; add integration or
    E2E coverage only when a real boundary is part of the contract.
- Property tests are for invariant-rich pure logic, not a quota.

## Bug fixes

1. Reproduce the defect with a failing regression test.
2. Confirm the failure would have caught the original defect.
3. Apply the smallest fix and make the regression test pass.
4. Refactor only while all affected tests remain green.
5. Run the repository's full completion gate before handoff.

## Guardrails

- Never write production code first and add a test that can only pass.
- Never weaken an assertion to encode known-bad behavior.
- Never require a particular test factory, marker, directory, or coverage number
    here; those are project/framework conventions and CI policy.
- Do not perform Git operations; hand the verified test and implementation
    changes back together.
- [ ] Failing test written BEFORE implementation
- [ ] Test name describes behavior, not implementation
- [ ] `pytest.raises` uses `match=` parameter
- [ ] AAA phases separated by blank lines
- [ ] Factory-boy for test data (no MagicMock on domain)
- [ ] All tests pass after refactoring
- [ ] Coverage targets met
