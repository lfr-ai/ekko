import { expect, test } from "@playwright/test";
import { injectAxe } from "axe-playwright";

test.describe("Accessibility and responsiveness", () => {
  test("renders a valid main landmark and heading", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("main")).toBeVisible();
    await expect(
      page.getByRole("heading", { level: 1, name: "Ekko Voice Assistant" }),
    ).toBeVisible();
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
      page.getByRole("heading", { level: 1, name: "Ekko Voice Assistant" }),
    ).toBeVisible();
    await expect(page.getByText("Local assistant runtime is active.")).toBeVisible();
  });

  test("keeps core homepage content visible on desktop viewport", async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto("/", { waitUntil: "domcontentloaded" });

    await expect(
      page.getByRole("heading", { level: 1, name: "Ekko Voice Assistant" }),
    ).toBeVisible();
    await expect(page.getByText("Local assistant runtime is active.")).toBeVisible();
  });
});
