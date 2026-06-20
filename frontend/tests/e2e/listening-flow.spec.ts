import { expect, test } from "@playwright/test";

test.describe("Claim intake interactions", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("accepts URL attachment and lists it", async ({ page }) => {
    const urlInput = page.getByPlaceholder("Paste file URL (PDF or similar)");
    await urlInput.fill("https://example.com/documents/claim.pdf");
    await page.getByRole("button", { name: "Add URL" }).click();

    await expect(page.getByText("claim.pdf")).toBeVisible();
    await expect(page.getByText("URL")).toBeVisible();
  });

  test("shows validation if submit is attempted without required fields", async ({ page }) => {
    await page.getByRole("button", { name: "Submit claim intake" }).click();

    await expect(page.getByText(/CPR must be formatted/i)).toBeVisible();
    await expect(page.getByText(/Choose an insurance condition/i)).toBeVisible();
    await expect(page.getByText(/Add at least one file or URL/i)).toBeVisible();
  });
});
