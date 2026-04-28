import { test, expect } from '@playwright/test';

test('home page basic', async ({ page }) => {
  await page.goto(process.env.FRONTEND_BASE_URL || 'http://localhost:3000');
  await expect(page).toHaveTitle(/./);
});
