import { expect, test } from "@playwright/test";

test.describe("Listening flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("toggles from idle to listening and back", async ({ page }) => {
    const statusBadge = page.getByTestId("assistant-status-badge");
    const startButton = page.getByRole("button", { name: "Start listening" });

    await expect(statusBadge).toContainText("Idle");
    await startButton.click();

    await expect(statusBadge).toContainText("Listening");
    await expect(page.getByRole("button", { name: "Stop listening" })).toBeVisible();
    await expect(page.getByText("Audio Input").locator("..").getByText("Active")).toBeVisible();

    await page.getByRole("button", { name: "Stop listening" }).click();
    await expect(statusBadge).toContainText("Idle");
    await expect(page.getByRole("button", { name: "Start listening" })).toBeVisible();
    await expect(page.getByText("Audio Input").locator("..").getByText("Standby")).toBeVisible();
  });

  test("activates visualizer pulse classes while listening", async ({ page }) => {
    const bars = page.getByTestId("audio-visualizer-bar");

    await expect(bars.first()).not.toHaveClass(/animate-pulse/);
    await page.getByRole("button", { name: "Start listening" }).click();
    await expect(bars.first()).toHaveClass(/animate-pulse/);

    await page.getByRole("button", { name: "Stop listening" }).click();
    await expect(bars.first()).not.toHaveClass(/animate-pulse/);
  });

  test("keeps quick actions available throughout listening state changes", async ({ page }) => {
    const clearTranscript = page.getByRole("button", { name: "Clear Transcript" });
    const exportConversation = page.getByRole("button", { name: "Export Conversation" });
    const languageSettings = page.getByRole("button", { name: "Language Settings" });

    await expect(clearTranscript).toBeEnabled();
    await expect(exportConversation).toBeEnabled();
    await expect(languageSettings).toBeEnabled();

    await page.getByRole("button", { name: "Start listening" }).click();

    await expect(clearTranscript).toBeEnabled();
    await expect(exportConversation).toBeEnabled();
    await expect(languageSettings).toBeEnabled();
  });
});
