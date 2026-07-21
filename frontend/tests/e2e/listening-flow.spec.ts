import { expect, test } from "@playwright/test";

test.describe("Home page", () => {
  test("renders landing content", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { name: "Ekko Voice Assistant" })).toBeVisible();
    await expect(page.getByText(/Local assistant runtime is active\./i)).toBeVisible();
  });
});
