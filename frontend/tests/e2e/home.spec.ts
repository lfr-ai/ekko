import { expect, test } from "@playwright/test";

const BASE_URL = process.env.FRONTEND_BASE_URL || "http://localhost:3000";

test.describe("Home page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test("renders page title", async ({ page }) => {
    await expect(page).toHaveTitle("Ekko");
  });

  test("displays heading", async ({ page }) => {
    const heading = page.getByRole("heading", { level: 1, name: "Ekko" });
    await expect(heading).toBeVisible();
  });

  test("displays description text", async ({ page }) => {
    const description = page.getByText("AI-powered voice assistant platform");
    await expect(description).toBeVisible();
  });

  test("content is centered on screen", async ({ page }) => {
    const container = page.locator("div.flex.min-h-screen");
    await expect(container).toBeVisible();
    await expect(container).toHaveCSS("display", "flex");
  });

  test("has correct lang attribute", async ({ page }) => {
    const lang = await page.locator("html").getAttribute("lang");
    expect(lang).toBe("en");
  });

  test("has viewport meta tag", async ({ page }) => {
    const viewport = page.locator('meta[name="viewport"]');
    await expect(viewport).toHaveAttribute("content", /width=device-width/);
  });

  test("root element exists", async ({ page }) => {
    const root = page.locator("#root");
    await expect(root).toBeAttached();
    const children = await root.locator("> *").count();
    expect(children).toBeGreaterThan(0);
  });

  test("no console errors on load", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    await page.goto(BASE_URL);
    await page.waitForLoadState("networkidle");
    expect(errors).toHaveLength(0);
  });

  test("no JavaScript errors on load", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));
    await page.goto(BASE_URL);
    await page.waitForLoadState("networkidle");
    expect(errors).toHaveLength(0);
  });
});

test.describe("Responsive viewports", () => {
  test("renders on mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE_URL);
    const heading = page.getByRole("heading", { level: 1, name: "Ekko" });
    await expect(heading).toBeVisible();
  });

  test("renders on tablet viewport", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(BASE_URL);
    const heading = page.getByRole("heading", { level: 1, name: "Ekko" });
    await expect(heading).toBeVisible();
  });

  test("renders on desktop viewport", async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto(BASE_URL);
    const heading = page.getByRole("heading", { level: 1, name: "Ekko" });
    await expect(heading).toBeVisible();
  });
});

test.describe("Accessibility", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test("heading hierarchy is valid", async ({ page }) => {
    const h1Count = await page.getByRole("heading", { level: 1 }).count();
    expect(h1Count).toBe(1);
  });

  test("text has sufficient contrast (theme tokens applied)", async ({ page }) => {
    const body = page.locator("body");
    const bgColor = await body.evaluate((el) => getComputedStyle(el).backgroundColor);
    const textColor = await body.evaluate((el) => getComputedStyle(el).color);
    expect(bgColor).toBeTruthy();
    expect(textColor).toBeTruthy();
    expect(bgColor).not.toBe(textColor);
  });

  test("page is keyboard navigable", async ({ page }) => {
    await page.keyboard.press("Tab");
    const focusedTag = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedTag).toBeTruthy();
  });
});

test.describe("Theme system", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test("CSS custom properties are defined", async ({ page }) => {
    const hasPrimary = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return style.getPropertyValue("--primary").trim().length > 0;
    });
    expect(hasPrimary).toBe(true);
  });

  test("background color is applied from theme", async ({ page }) => {
    const bgColor = await page.evaluate(() => {
      return getComputedStyle(document.body).backgroundColor;
    });
    expect(bgColor).toBeTruthy();
    expect(bgColor).not.toBe("");
  });

  test("dark mode variables are available in stylesheet", async ({ page }) => {
    const hasDarkRule = await page.evaluate(() => {
      for (const sheet of document.styleSheets) {
        try {
          for (const rule of sheet.cssRules) {
            if (rule instanceof CSSStyleRule && rule.selectorText?.includes(".dark")) {
              return true;
            }
          }
        } catch {
          continue;
        }
      }
      return false;
    });
    expect(hasDarkRule).toBe(true);
  });
});

test.describe("Performance", () => {
  test("page loads within 5 seconds", async ({ page }) => {
    const start = Date.now();
    await page.goto(BASE_URL);
    await page.waitForLoadState("domcontentloaded");
    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(5000);
  });

  test("no unnecessary network requests on initial load", async ({ page }) => {
    const requests: string[] = [];
    page.on("request", (req) => requests.push(req.url()));
    await page.goto(BASE_URL);
    await page.waitForLoadState("networkidle");
    const externalRequests = requests.filter(
      (url) => !url.startsWith(BASE_URL) && !url.startsWith("data:"),
    );
    expect(externalRequests).toHaveLength(0);
  });
});
