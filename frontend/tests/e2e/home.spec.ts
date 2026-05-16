import { expect, test } from "@playwright/test";

test.describe("App shell", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("renders core layout and metadata", async ({ page }) => {
    await expect(page).toHaveTitle("Ekko");
    await expect(page.getByTestId("app-shell")).toBeVisible();

    const lang = await page.locator("html").getAttribute("lang");
    expect(lang).toBe("en");

    await expect(page.locator('meta[name="viewport"]')).toHaveAttribute(
      "content",
      /width=device-width/,
    );
  });

  test("renders primary cards and footer details", async ({ page }) => {
    await expect(page.getByRole("heading", { level: 1, name: "Ekko" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Transcript" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Audio Input" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "System Status" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Quick Actions" })).toBeVisible();

    await expect(page.getByText("Ekko v0.1.0")).toBeVisible();
    await expect(page.getByText("React 19")).toBeVisible();
  });

  test("starts in idle state with standby audio", async ({ page }) => {
    await expect(page.getByTestId("assistant-status-badge")).toContainText("Idle");
    await expect(page.getByRole("button", { name: "Start listening" })).toBeVisible();
    await expect(page.getByText("Audio Input").locator("..").getByText("Standby")).toBeVisible();
  });

  test("has no top-level JavaScript runtime errors on load", async ({ page }) => {
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    expect(pageErrors).toEqual([]);
  });
});
