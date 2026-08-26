---
description: Testing standards for Python tests
applyTo: "**/test_*.py, **/conftest.py"
---

# Testing Instructions

- Write focused tests with clear Arrange/Act/Assert structure.
- Prefer behavior-oriented assertions over implementation details.
- Add regression tests for every bug fix.
- Avoid flaky time/network dependencies unless explicitly integration-scoped.
- For HTTP status assertions, always use constants from 'fastapi.status'
	instead of numeric literals.
