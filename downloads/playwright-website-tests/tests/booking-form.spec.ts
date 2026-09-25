import { test, expect } from '@playwright/test';

// The booking form. Each test asserts one visitor-visible outcome — the
// message shown, the field focused, the request made — using role and label
// locators so a CSS refactor cannot break the suite.

test.describe('booking form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('required name shows an error and nothing is sent', async ({ page }) => {
    let posted = false;
    await page.route('**/api/book', (route) => { posted = true; return route.fulfill({ status: 200, body: '{"ok":true}' }); });

    await page.getByRole('button', { name: 'Request my assessment' }).click();

    await expect(page.getByRole('status')).toHaveText('Please enter your name.');
    await expect(page.getByLabel('Your name')).toBeFocused();
    expect(posted).toBe(false);
  });

  test('empty or malformed email is rejected before any success message', async ({ page }) => {
    // Assert the exact error text. An early draft matched /email/i, which the
    // success message "Thanks! We will email you to confirm." also matches —
    // a false pass that only showed up when the check was deliberately broken.
    const error = 'Please enter a valid email address so we can confirm your slot.';
    let posted = false;
    await page.route('**/api/book', (route) => { posted = true; return route.fulfill({ status: 200, body: '{"ok":true}' }); });

    await page.getByLabel('Your name').fill('Test Visitor');
    await page.getByRole('button', { name: 'Request my assessment' }).click();
    await expect(page.getByRole('status')).toHaveText(error);

    await page.getByLabel(/Email/).fill('bob@');
    await page.getByRole('button', { name: 'Request my assessment' }).click();
    await expect(page.getByRole('status')).toHaveText(error);
    expect(posted, 'nothing should be sent with a missing or malformed email').toBe(false);
  });

  test('a valid submission posts the fields and shows the confirmation (mocked endpoint)', async ({ page }) => {
    // The endpoint is mocked: this proves the page posts the right fields and
    // handles a 200. It proves nothing about email delivery — see the guide.
    const requests: Record<string, string>[] = [];
    await page.route('**/api/book', async (route) => {
      const form = route.request().postDataBuffer();
      const fields: Record<string, string> = {};
      if (form) {
        // multipart/form-data: read the field names and values loosely
        const text = form.toString('latin1');
        for (const m of text.matchAll(/name="([^"]+)"\r\n\r\n([^\r]*)/g)) fields[m[1]] = m[2];
      }
      requests.push(fields);
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' });
    });

    await page.getByLabel('Your name').fill('Test Visitor');
    await page.getByLabel(/Email/).fill('visitor@example.com');
    await page.getByLabel('Preferred time').selectOption('afternoon');
    await page.getByRole('button', { name: 'Request my assessment' }).click();

    await expect(page.getByRole('status')).toHaveText('Thanks! We will email you to confirm.');
    expect(requests).toHaveLength(1);
    expect(requests[0]).toMatchObject({ name: 'Test Visitor', email: 'visitor@example.com', slot: 'afternoon' });
  });

  test('a failed submission is reported, not hidden behind Thanks', async ({ page }) => {
    await page.route('**/api/book', (route) => route.fulfill({ status: 500, body: 'boom' }));
    await page.getByLabel('Your name').fill('Test Visitor');
    await page.getByLabel(/Email/).fill('visitor@example.com');
    await page.getByRole('button', { name: 'Request my assessment' }).click();
    await expect(page.getByRole('status')).toContainText(/did not send/);
  });
});
