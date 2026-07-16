import { expect, test } from "@playwright/test";

test.describe("Claim intake networked flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/api/insurance-conditions/options", async (route) => {
      await route.fulfill({
        body: JSON.stringify({
          items: [
            { code: "P_BASIC", id: "p-basic", label: "P Basic" },
            { code: "P_PLUS", id: "p-plus", label: "P Plus" },
          ],
        }),
        contentType: "application/json",
        status: 200,
      });
    });
  });

  test("submits a valid intake with URL attachment", async ({ page }) => {
    await page.route("**/api/claims/intake", async (route) => {
      await route.fulfill({
        body: JSON.stringify({
          acceptedAtIso: "2026-06-22T10:30:00Z",
          referenceId: "CLAIM-E2E-001",
        }),
        contentType: "application/json",
        status: 200,
      });
    });

    await page.goto("/", { waitUntil: "domcontentloaded" });

    await page.getByLabel("CPR").fill("010190-1234");
    await page.getByLabel("Insurance condition P").click();
    await page.getByRole("option", { name: "P Basic" }).click();
    await page.getByLabel("Coverage period start").fill("2026-01-01");
    await page.getByLabel("Coverage period end").fill("2026-12-31");
    await page.getByLabel("Payout amount").fill("3500");

    await page.getByPlaceholder("Paste file URL (PDF or similar)").fill("https://example.com/claim.pdf");
    await page.getByRole("button", { name: "Add URL" }).click();
    await expect(page.getByText("claim.pdf", { exact: true })).toBeVisible();

    await page.getByRole("button", { name: "Submit claim intake" }).click();

    await expect(page.getByText(/Claim intake submitted\. Reference:/)).toBeVisible();
    await expect(page.getByText(/CLAIM-E2E-001/)).toBeVisible();
  });

  test("shows option-loading error when options endpoint fails", async ({ page }) => {
    await page.route("**/api/insurance-conditions/options", async (route) => {
      await route.fulfill({
        body: JSON.stringify({ message: "service unavailable" }),
        contentType: "application/json",
        status: 503,
      });
    });

    await page.goto("/", { waitUntil: "domcontentloaded" });

    await expect(page.getByText("Could not load insurance conditions. Please retry.")).toBeVisible();
  });
});
