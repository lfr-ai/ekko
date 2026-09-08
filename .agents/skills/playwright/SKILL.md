---
name: playwright
description: Build resilient Playwright end-to-end tests for user-visible journeys, accessibility, and browser compatibility. Use when adding E2E coverage, choosing locators, configuring browsers/traces, debugging failures, or validating a deployed frontend.
---

# Playwright E2E Testing Skill

## Purpose

Write and maintain end-to-end tests that verify critical user journeys,
accessibility compliance, and cross-browser behavior using Playwright.

## Test Structure

```typescript
import { expect, test } from "@playwright/test";

test.describe("Feature: [Feature Name]", () => {
  test("should [expected behavior] when [user action]", async ({ page }) => {
    // Navigate
    await page.goto("/");

    // Interact (prefer accessible locators)
    await page.getByRole("button", { name: "Submit" }).click();

    // Assert
    await expect(page.getByRole("alert")).toBeVisible();
  });
});
```

## Locator Priority

Use accessible locators in this order:

1. `page.getByRole()` — semantic role + accessible name
2. `page.getByLabel()` — form controls by label
3. `page.getByText()` — visible text content
4. `page.getByPlaceholder()` — input placeholders
5. `page.getByTestId()` — last resort for complex selectors

## Accessibility Testing

```typescript
import AxBuilder from "@axe-core/playwright";

test("page should have no accessibility violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

## Reusable helpers

For reusable interactions, create page objects:

```typescript
// tests/e2e/pages/example-page.ts
export class ExamplePage {
  constructor(private readonly page: Page) {}

  async navigate() {
    await this.page.goto("/");
  }

  async submit() {
    await this.page.getByRole("button", { name: "Submit" }).click();
  }
}
```

## Best Practices

- Test critical user journeys, not individual components.
- Keep each test isolated and control its data, cookies, and storage.
- Mock third-party systems at the network boundary; test only what you control.
- Use `test.describe` for logical grouping.
- Configure retries for CI (`retries: 2`).
- Capture screenshots on failure.
- Use `test.slow()` for inherently slow operations.
- Never hard-code timeouts — use `expect().toBeVisible()` with auto-waiting.
- Run against production build when possible.
- Use web-first assertions (`await expect(locator).toBeVisible()`), not manual
  `isVisible()` checks.

## Running Tests

Run through package scripts: `bun run test:e2e`. Install only the browsers the
project supports; Chromium is a lean default, while Firefox/WebKit belong in the
matrix when browser support requires them.

## Configuration

Defined in `playwright.config.ts`:

- Browser projects selected from the product support matrix
- Auto-start dev server via `webServer`
- Traces on first retry, screenshots on failure
- HTML reporter for local review
