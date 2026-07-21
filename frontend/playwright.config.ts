import { defineConfig, devices } from "@playwright/test";

const E2E_DEFAULT_PORT = 4173;
const E2E_DEFAULT_BASE_URL = `http://127.0.0.1:${E2E_DEFAULT_PORT}`;

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 45 * 1000,
  expect: { timeout: 5000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 2,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: process.env.FRONTEND_BASE_URL || E2E_DEFAULT_BASE_URL,
    headless: true,
    viewport: { width: 1280, height: 720 },
    actionTimeout: 10_000,
    navigationTimeout: 45_000,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  webServer: {
    command: `bun run dev --host 127.0.0.1 --port ${E2E_DEFAULT_PORT}`,
    url: E2E_DEFAULT_BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "mobile-chrome", use: { ...devices["Pixel 5"] } },
  ],
});
