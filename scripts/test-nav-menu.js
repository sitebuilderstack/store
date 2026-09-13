/* Behavioural test for the header disclosure menu.
 *
 * A menu is the easiest thing to build in a way that excludes people: opening
 * on hover alone locks out keyboard and touch users, and hiding the panel in
 * CSS before JavaScript has enhanced it hides the links from anyone whose
 * script did not run. Both are asserted here.
 *
 * Usage: node test-nav-menu.js <url> [--preview <themeId>]
 */
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH ||
            '/home/ubuntu/.cache/chrome-manual/chrome-linux64/chrome';
const url = process.argv[2];
const pIdx = process.argv.indexOf('--preview');
const preview = pIdx > -1 ? process.argv[pIdx + 1] : null;
const NOISE = ["Framing 'https://shop.app/' violates", 'Error producing monorail event'];

let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d ? '  -> ' + d : ''}`); };

async function assertNotThrottled(page) {
  const s = await page.evaluate(() => document.title + ' ' +
    (document.body ? document.body.textContent.slice(0, 200) : ''));
  if (/429|Too Many Requests|rate limit/i.test(s)) {
    console.log('  ABORT  the site is rate-limiting this client (HTTP 429).');
    process.exit(2);
  }
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: EXE, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const page = await browser.newPage();
  // The nav is only shown at >= 56em, so test it at a width where it exists.
  await page.setViewport({ width: 1280, height: 900 });
  const errors = [];
  const rec = t => { if (!NOISE.some(n => t.includes(n))) errors.push(t); };
  page.on('console', m => { if (m.type() === 'error') rec(m.text()); });
  page.on('pageerror', e => rec(String(e)));

  if (preview) await page.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  await page.goto(url, { waitUntil: 'networkidle2' });
  await assertNotThrottled(page);

  const T = '.sbs-nav__toggle';
  const P = '.sbs-nav__sub';

  check('the menu toggle is a real button',
        await page.$eval(T, e => e.tagName === 'BUTTON' && e.type === 'button'));
  check('the toggle is revealed by JS', await page.$eval(T, e => !e.hidden));
  check('it starts collapsed',
        (await page.$eval(T, e => e.getAttribute('aria-expanded'))) === 'false');
  check('the panel is not painted while collapsed',
        (await page.$eval(P, e => e.getBoundingClientRect().height)) === 0);
  check('aria-controls points at the panel',
        await page.evaluate((t, p) => {
          const btn = document.querySelector(t);
          const el = document.getElementById(btn.getAttribute('aria-controls'));
          return el === document.querySelector(p);
        }, T, P));

  /* Hover must not open it. A hover-only menu is unusable by keyboard and
     touch, so this asserts the interaction is a real activation. */
  await page.hover(T);
  await new Promise(r => setTimeout(r, 250));
  check('hovering alone does not open it',
        (await page.$eval(T, e => e.getAttribute('aria-expanded'))) === 'false');

  await page.click(T);
  await new Promise(r => setTimeout(r, 120));
  check('clicking opens it',
        (await page.$eval(T, e => e.getAttribute('aria-expanded'))) === 'true' &&
        (await page.$eval(P, e => e.getBoundingClientRect().height)) > 0);

  const items = await page.$$eval(P + ' a', els => els.map(a => ({
    href: a.getAttribute('href'),
    title: (a.querySelector('.sbs-nav__subtitle') || {}).textContent,
    price: (a.querySelector('.sbs-nav__subprice') || {}).textContent,
  })));
  /* The catalogue is the source of truth, not a literal in this file. Asserting
     "two products" meant the test failed the day a third was added — which is
     backwards: the thing worth catching is a product in the catalogue that is
     missing from the menu, and a hard-coded count cannot tell the two apart. */
  const catalogue = await browser.newPage();
  await catalogue.goto(new URL('/collections/all', url).href, { waitUntil: 'networkidle2' });
  const sold = await catalogue.$$eval('a[href^="/products/"]',
    els => [...new Set(els.map(a => a.getAttribute('href').split('?')[0]))]);
  await catalogue.close();

  const listed = items.map(i => (i.href || '').split('?')[0]);
  const missing = sold.filter(h => !listed.includes(h));
  check('every product in the catalogue is listed',
        sold.length > 0 && missing.length === 0,
        `catalogue=${sold.length} menu=${listed.length}` +
        (missing.length ? ` missing=${missing.join(' ')}` : ''));
  check('every menu entry links to a product page',
        items.every(i => i.href && i.href.startsWith('/products/')),
        items.map(i => i.href).join(' '));
  check('each shows a live title and price',
        items.every(i => i.title && /^\$\d/.test((i.price || '').trim())),
        items.map(i => `${i.title}=${i.price}`).join(' | '));

  check('every item is reachable by keyboard',
        await page.$$eval(P + ' a', els => els.every(a => {
          a.focus(); return document.activeElement === a;
        })));

  // Escape must close and return focus to the toggle.
  await page.focus(P + ' a');
  await page.keyboard.press('Escape');
  await new Promise(r => setTimeout(r, 120));
  check('Escape closes it',
        (await page.$eval(T, e => e.getAttribute('aria-expanded'))) === 'false');
  check('Escape returns focus to the toggle',
        await page.evaluate(t => document.activeElement === document.querySelector(t), T));

  // Clicking outside must close it.
  await page.click(T);
  await new Promise(r => setTimeout(r, 100));
  await page.click('body', { offset: { x: 5, y: 400 } }).catch(() => page.mouse.click(5, 400));
  await new Promise(r => setTimeout(r, 120));
  check('clicking outside closes it',
        (await page.$eval(T, e => e.getAttribute('aria-expanded'))) === 'false');

  // Keyboard activation, not just mouse.
  await page.focus(T);
  await page.keyboard.press('Enter');
  await new Promise(r => setTimeout(r, 120));
  check('Enter opens it from the keyboard',
        (await page.$eval(T, e => e.getAttribute('aria-expanded'))) === 'true');

  check('no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await page.close();

  /* Without JavaScript the product links must still be present and painted —
     the toggle is what hides, never the links. */
  const noJs = await browser.newPage();
  await noJs.setJavaScriptEnabled(false);
  await noJs.setViewport({ width: 1280, height: 900 });
  if (preview) await noJs.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  await noJs.goto(url, { waitUntil: 'networkidle2' });
  const off = await noJs.evaluate(() => ({
    toggle: document.querySelector('.sbs-nav__toggle').getBoundingClientRect().height,
    links: [...document.querySelectorAll('.sbs-nav__sub a')]
      .filter(a => a.getBoundingClientRect().height > 0)
      .map(a => a.getAttribute('href')),
  }));
  check('no-JS: the toggle is not painted', off.toggle === 0, off.toggle + 'px');
  check('no-JS: every product link is visible inline',
        off.links.length === items.length && off.links.length > 0,
        `${off.links.length} of ${items.length}: ${off.links.join(' ')}`);
  await noJs.close();

  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
