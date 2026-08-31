---
name: accessibility
description: Apply WCAG 2.1 AA and inclusive UI patterns. Use when building or reviewing interactive interfaces, forms, navigation, focus behavior, semantic HTML, keyboard support, or accessibility tests.
---

# Accessibility Skill (WCAG 2.1 AA)

## Purpose

Ensure all UI components meet WCAG 2.1 Level AA standards for users with
disabilities, including screen reader users, keyboard-only users, and users
with visual impairments.

## Core Principles (POUR)

| Principle | Meaning | Examples |
|-----------|---------|----------|
| **Perceivable** | Content is perceivable by all senses | Alt text, contrast, captions |
| **Operable** | UI is operable by all input methods | Keyboard nav, no time limits |
| **Understandable** | Content is understandable | Clear language, predictable UI |
| **Robust** | Works with assistive technologies | Semantic HTML, ARIA |

## Semantic HTML First

Always prefer native HTML semantics before reaching for ARIA:

```typescript
// Good — native semantics
<button onClick={handleSubmit}>Send</button>
<nav aria-label="Hovednavigation">...</nav>
<main>...</main>

// Bad — div soup with ARIA
<div role="button" onClick={handleSubmit}>Send</div>
```

## Keyboard Navigation

- All interactive elements must be reachable via Tab.
- Custom widgets implement arrow key navigation.
- Focus is visible and follows logical order.
- Modal dialogs trap focus (Radix UI handles this automatically).
- Skip links for repetitive navigation.

## Color and Contrast

- Text contrast: minimum 4.5:1 (normal text), 3:1 (large text).
- UI component contrast: minimum 3:1 against adjacent colors.
- Never convey information through color alone.
- Test with color blindness simulators.

## Forms

```typescript
// Always associate labels with inputs
<Label htmlFor="caseId">Sagsnummer</Label>
<Input id="caseId" aria-describedby="caseId-error" aria-invalid={!!error} />
{error && <p id="caseId-error" role="alert">{error.message}</p>}
```

## Live Regions

Use for dynamic content changes (toast notifications, loading states):

```typescript
<div role="status" aria-live="polite">
  {isLoading && "Indlæser..."}
</div>

<div role="alert" aria-live="assertive">
  {errorMessage}
</div>
```

## Testing Library Query Priority

Reflects accessibility hierarchy:

1. `getByRole` — most accessible (ARIA roles)
2. `getByLabelText` — form controls
3. `getByText` — visible content
4. `getByTestId` — last resort only

## Playwright Accessibility Audit

```typescript
import AxBuilder from "@axe-core/playwright";

test("no accessibility violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

## Checklist

- [ ] All images have alt text (or `alt=""` for decorative)
- [ ] All form inputs have visible labels
- [ ] Error messages are announced to screen readers
- [ ] Focus order is logical
- [ ] Color contrast meets AA ratios
- [ ] Interactive elements have accessible names
- [ ] Loading states are announced
- [ ] Modal dialogs manage focus correctly
- [ ] Page has proper heading hierarchy (h1 → h2 → h3)
- [ ] Language attribute set on `<html>` element
