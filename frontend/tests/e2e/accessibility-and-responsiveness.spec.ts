import { expect, test } from "@playwright/test";
import { injectAxe } from "axe-playwright";

test.describe("Accessibility and responsiveness", () => {
  test("has keyboard-focusable primary controls", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });

    await page.getByLabel("CPR").focus();
    await expect(page.getByLabel("CPR")).toBeFocused();

    await page.getByLabel("Coverage period start").focus();
    await expect(page.getByLabel("Coverage period start")).toBeFocused();
  });

  test("has no critical accessibility violations in app shell", async ({ page }) => {
    test.slow();
    await page.goto("/", { waitUntil: "domcontentloaded" });
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
    await page.goto("/", { waitUntil: "domcontentloaded" });

    await expect(
      page.getByRole("heading", { level: 1, name: "Insurance claim intake" }),
    ).toBeVisible();
    await expect(page.getByLabel("CPR")).toBeVisible();
    await expect(page.getByRole("button", { name: "Submit claim intake" })).toBeVisible();
  });

  test("keeps upload and submit controls visible on desktop viewport", async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto("/", { waitUntil: "domcontentloaded" });

    await expect(page.getByText("Select files", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Add URL" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Submit claim intake" })).toBeVisible();
  });
});
