import { test, expect } from '@playwright/test';

test('the primary call to action lands on the booking form', async ({ page }) => {
  await page.goto('/services.html');
  await page.getByRole('link', { name: 'Book a free 15-minute assessment' }).click();
  await expect(page).toHaveURL(/\/#book$/);
  await expect(page.getByRole('heading', { name: 'Request your free assessment' })).toBeInViewport();
});

test('every main-navigation link returns 200', async ({ page, request }) => {
  await page.goto('/');
  // includeHidden: at phone width the menu is collapsed, and a link that is
  // hidden until the menu opens still has to resolve.
  const links = await page.getByRole('navigation', { name: 'Main', includeHidden: true }).getByRole('link', { includeHidden: true }).all();
  expect(links.length).toBeGreaterThan(0);
  for (const link of links) {
    const href = await link.getAttribute('href');
    const res = await request.get(href!);
    expect(res.status(), `${href} should return 200`).toBe(200);
  }
});

test.describe('mobile navigation', () => {
  // Only meaningful at phone width; the desktop project skips it.
  test.skip(({ isMobile }) => !isMobile, 'mobile-only');

  test('menu opens and closes and reports its state', async ({ page }) => {
    await page.goto('/');
    const toggle = page.getByRole('button', { name: 'Menu' });
    const nav = page.getByRole('navigation', { name: 'Main' });
    await expect(nav).toBeHidden();
    await expect(toggle).toHaveAttribute('aria-expanded', 'false');
    await toggle.click();
    await expect(nav).toBeVisible();
    await expect(toggle).toHaveAttribute('aria-expanded', 'true');
    await toggle.click();
    await expect(nav).toBeHidden();
  });
});
