/* Behavioural test for the guide library filter.
 *
 * The filter is the main new interaction on /blogs/guides, and every part of
 * it is invisible to static analysis: whether the controls appear, whether
 * filtering actually narrows the list, whether the empty state shows, whether
 * the URL becomes shareable, and whether it is operable from the keyboard.
 *
 * Each assertion is written so it can fail: the counts are compared against
 * what the page rendered, not against a constant.
 *
 * Usage: node test-library-filter.js <url> [--preview <themeId>]
 */
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH ||
            '/home/ubuntu/.cache/chrome-manual/chrome-linux64/chrome';

const url = process.argv[2];
const previewIdx = process.argv.indexOf('--preview');
const preview = previewIdx > -1 ? process.argv[previewIdx + 1] : null;

/* A rate-limited response renders an error page with none of the markup this
   test looks for, producing findings like "0 cards" that describe the throttle
   rather than the site. Fail loudly and specifically instead. */
async function assertNotThrottled(page) {
  const status = await page.evaluate(() =>
    document.title + ' ' + (document.body ? document.body.textContent.slice(0, 200) : ''));
  if (/429|Too Many Requests|rate limit/i.test(status)) {
    console.log('  ABORT  the site is rate-limiting this client (HTTP 429).');
    console.log('         These results would describe the throttle, not the site.');
    process.exit(2);
  }
}

let failures = 0;
function check(name, ok, detail) {
  if (!ok) failures++;
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  -> ' + detail : ''}`);
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: EXE,
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });

  /* Two console errors come from Shopify's own storefront scripts and appear
     on pages this project has never touched — verified against the untouched
     homepage and product page. They are ignored by exact substring so that a
     real error from site code still fails this test:
       · the Shop Pay login iframe being refused by frame-ancestors
       · Shopify's monorail analytics beacon failing to send
     Anything else is a genuine failure. */
  const PLATFORM_NOISE = [
    "Framing 'https://shop.app/' violates",
    'Error producing monorail event',
  ];
  const errors = [];
  const record = t => {
    if (!PLATFORM_NOISE.some(n => t.includes(n))) errors.push(t);
  };
  page.on('console', m => { if (m.type() === 'error') record(m.text()); });
  page.on('pageerror', e => record(String(e)));

  if (preview) {
    await page.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`,
                    { waitUntil: 'networkidle2' });
  }
  await page.goto(url, { waitUntil: 'networkidle2' });
  await assertNotThrottled(page);

  const total = await page.$$eval('[data-sbs-item]', els => els.length);
  check('guides rendered', total > 0, `${total} cards`);

  check('controls revealed by JS',
        await page.$eval('[data-sbs-library-controls]', el => !el.hidden));

  const visible = () => page.$$eval('[data-sbs-item]',
    els => els.filter(e => !e.hidden).length);

  check('all guides visible before filtering', (await visible()) === total);

  // Filter by a level the page actually offers, and compare against the number
  // of cards carrying that level — not against a hard-coded expectation.
  const level = await page.$eval('#sbs-lib-level',
    s => (Array.from(s.options).find(o => o.value) || {}).value);
  const expectLevel = await page.$$eval('[data-sbs-item]',
    (els, lv) => els.filter(e => e.dataset.level === lv).length, level);
  await page.select('#sbs-lib-level', level);
  await new Promise(r => setTimeout(r, 120));
  const gotLevel = await visible();
  check(`level filter "${level}" narrows the list`,
        gotLevel === expectLevel && gotLevel < total, `${gotLevel} shown, ${expectLevel} expected`);

  check('status region reports the filtered count',
        (await page.$eval('[data-sbs-library-status]', e => e.textContent)).trim()
          .startsWith(String(gotLevel)));

  check('URL carries the filter for sharing',
        page.url().includes('level=' + encodeURIComponent(level)), page.url());

  // Search that cannot match anything must produce the empty state.
  await page.type('#sbs-lib-q', 'zzzznotarealterm');
  await new Promise(r => setTimeout(r, 120));
  check('impossible search shows the empty state',
        (await visible()) === 0 &&
        (await page.$eval('[data-sbs-library-empty]', e => !e.hidden)));

  // Reset must restore everything and clear the querystring.
  await page.click('[data-sbs-library-reset]');
  await new Promise(r => setTimeout(r, 120));
  check('reset restores every guide', (await visible()) === total);
  check('reset clears the querystring', !page.url().includes('?'), page.url());

  // A shared filtered URL must arrive already filtered.
  await page.goto(`${url}${url.includes('?') ? '&' : '?'}level=${encodeURIComponent(level)}`,
                  { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 150));
  check('shared filtered URL applies on load', (await visible()) === expectLevel);

  // Keyboard: every control must be reachable and operable without a mouse.
  await page.goto(url, { waitUntil: 'networkidle2' });
  const reachable = await page.evaluate(() => {
    const ids = ['sbs-lib-q', 'sbs-lib-topic', 'sbs-lib-level', 'sbs-lib-goal', 'sbs-lib-type'];
    return ids.every(id => {
      const el = document.getElementById(id);
      if (!el) return false;
      el.focus();
      return document.activeElement === el;
    });
  });
  check('every filter control is focusable', reachable);

  const resetFocusable = await page.evaluate(() => {
    const b = document.querySelector('[data-sbs-library-reset]');
    b.focus();
    return document.activeElement === b && b.tagName === 'BUTTON';
  });
  check('reset is a real focusable button', resetFocusable);

  /* With JavaScript off the filter form must not be painted — it cannot do
     anything — while every guide must still be present and readable. That is
     also exactly what a crawler gets. */
  const noJs = await browser.newPage();
  await noJs.setJavaScriptEnabled(false);
  if (preview) {
    await noJs.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  }
  await noJs.goto(url, { waitUntil: 'networkidle2' });
  const off = await noJs.evaluate(() => ({
    ctrl: document.querySelector('[data-sbs-library-controls]').getBoundingClientRect().height,
    cards: [...document.querySelectorAll('[data-sbs-item]')]
      .filter(e => e.getBoundingClientRect().height > 0).length,
  }));
  check('no-JS: the filter form is not painted', off.ctrl === 0, off.ctrl + 'px');
  check('no-JS: every guide is still visible', off.cards === total,
        off.cards + ' of ' + total);
  await noJs.close();

  check('no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));

  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
