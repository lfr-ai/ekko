import { expect, test } from "@playwright/test";

test.describe("App shell", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });
  });

  test("renders core layout and metadata", async ({ page }) => {
    await expect(page).toHaveTitle("Ekko Frontend");
    await expect(page).toHaveURL(/\/claims\/intake$/);

    const lang = await page.locator("html").getAttribute("lang");
    expect(lang).toBe("en");

    await expect(page.locator('meta[name="viewport"]')).toHaveAttribute(
      "content",
      /width=device-width/,
    );
  });

  test("renders intake sections and submit call-to-action", async ({ page }) => {
    await expect(
      page.getByRole("heading", { level: 1, name: "Insurance claim intake" }),
    ).toBeVisible();
    await expect(page.getByText("Claims automation frontend")).toBeVisible();
    await expect(page.getByLabel("CPR")).toBeVisible();
    await expect(page.getByLabel("Coverage period start")).toBeVisible();
    await expect(page.getByLabel("Coverage period end")).toBeVisible();
    await expect(page.getByRole("button", { name: "Submit claim intake" })).toBeVisible();
  });

  test("has no top-level JavaScript runtime errors on load", async ({ page }) => {
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    await page.goto("/", { waitUntil: "domcontentloaded" });
    await page.waitForLoadState("networkidle");

    expect(pageErrors).toEqual([]);
  });
});
