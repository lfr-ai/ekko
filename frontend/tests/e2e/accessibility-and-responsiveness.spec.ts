import { expect, test } from "@playwright/test";
import { injectAxe } from "axe-playwright";

test.describe("Accessibility and responsiveness", () => {
  test("has keyboard-focusable primary controls", async ({ page }) => {
    await page.goto("/");

    await page.keyboard.press("Tab");
    await expect(page.getByRole("button", { name: "Start listening" })).toBeFocused();
  });

  test("has no critical accessibility violations in app shell", async ({ page }) => {
    await page.goto("/");
    await injectAxe(page);

    const results = await page.evaluate(async () => {
      return (
        window as typeof window & {
          axe: {
            run: (
              node?: Node,
              options?: unknown,
            ) => Promise<{ violations: Array<{ impact: string | null }> }>;
          };
        }
      ).axe.run(document, {
        runOnly: {
          type: "tag",
          values: ["wcag2a", "wcag2aa"],
        },
      });
    });

    const criticalViolations = results.violations.filter(
      (violation: { impact: string | null }) => violation.impact === "critical",
    );
    expect(criticalViolations).toEqual([]);
  });

  test("renders core content on narrow mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/");

    await expect(page.getByRole("heading", { level: 1, name: "Ekko" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Transcript" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Start listening" })).toBeVisible();
  });

  test("keeps sidebar controls visible on desktop viewport", async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto("/");

    await expect(page.getByRole("button", { name: "Start listening" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Audio output" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Settings", exact: true })).toBeVisible();
  });
});
