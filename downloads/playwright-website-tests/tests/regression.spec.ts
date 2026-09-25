import { test, expect } from '@playwright/test';

// A regression check for a bug that was fixed once and must stay fixed:
// the success message used to appear before the request completed, so a
// failed send still showed "Thanks!". The test delays the mocked response
// and asserts the message is not shown early.
test('success message waits for the server response (regression)', async ({ page }) => {
  await page.goto('/');
  let release!: () => void;
  const gate = new Promise<void>((r) => { release = r; });
  await page.route('**/api/book', async (route) => {
    await gate;
    await route.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' });
  });

  await page.getByLabel('Your name').fill('Test Visitor');
  await page.getByLabel(/Email/).fill('visitor@example.com');
  await page.getByRole('button', { name: 'Request my assessment' }).click();

  await expect(page.getByRole('status')).toHaveText('Sending…');
  await expect(page.getByRole('status')).not.toContainText('Thanks');
  release();
  await expect(page.getByRole('status')).toHaveText('Thanks! We will email you to confirm.');
});
