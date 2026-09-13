/* Behavioural test for the interactive checklists.
 *
 * Covers the parts that only exist at runtime: persistence across a reload,
 * the progress figure, native reset, and — most importantly — that the page
 * still works with JavaScript disabled, because the checkboxes and the reset
 * are real HTML rather than script-built controls.
 *
 * Usage: node test-checklist.js <url> [--preview <themeId>]
 */
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH ||
            '/home/ubuntu/.cache/chrome-manual/chrome-linux64/chrome';
const url = process.argv[2];
const pIdx = process.argv.indexOf('--preview');
const preview = pIdx > -1 ? process.argv[pIdx + 1] : null;
const NOISE = ["Framing 'https://shop.app/' violates", 'Error producing monorail event'];

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
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d ? '  -> ' + d : ''}`); };

(async () => {
  const browser = await puppeteer.launch({
    executablePath: EXE, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });
  const errors = [];
  const rec = t => { if (!NOISE.some(n => t.includes(n))) errors.push(t); };
  page.on('console', m => { if (m.type() === 'error') rec(m.text()); });
  page.on('pageerror', e => rec(String(e)));

  if (preview) await page.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  await page.goto(url, { waitUntil: 'networkidle2' });
  await assertNotThrottled(page);

  const total = await page.$$eval('[data-sbs-check]', e => e.length);
  check('checkboxes rendered', total > 50, `${total} items`);

  check('every checkbox has an accessible name',
    await page.$$eval('[data-sbs-check]', els => els.every(i => {
      const l = document.querySelector(`label[for="${CSS.escape(i.id)}"]`);
      return l && l.textContent.trim().length > 0;
    })));

  check('ids are content-hashed, not positional',
    await page.$$eval('[data-sbs-check]', e => e.every(i => /^chk-[0-9a-f]{12}$/.test(i.id))));

  const countText = () => page.$eval('[data-sbs-cl-count]', e => e.textContent.trim());
  check('progress starts at zero', (await countText()).startsWith('0 of '), await countText());

  // Tick three, confirm the count and the progressbar value both move.
  const ids = await page.$$eval('[data-sbs-check]', e => e.slice(0, 3).map(i => i.id));
  for (const id of ids) await page.click(`label[for="${id}"]`);
  check('ticking updates the count', (await countText()).startsWith('3 of '), await countText());
  const aria = await page.$eval('[data-sbs-cl-bar]', e => e.getAttribute('aria-valuenow'));
  check('progressbar reports a percentage', Number(aria) > 0, aria + '%');

  // Reload: state must survive.
  await page.reload({ waitUntil: 'networkidle2' });
  const stillChecked = await page.$$eval('[data-sbs-check]', (e, want) =>
    want.every(id => (e.find(x => x.id === id) || {}).checked), ids);
  check('ticks survive a reload', stillChecked);
  check('count restored after reload', (await countText()).startsWith('3 of '), await countText());

  // Reset must clear the boxes, the count, and the stored state.
  await page.click('[data-sbs-cl-reset]');
  await new Promise(r => setTimeout(r, 120));
  check('reset clears every box',
    (await page.$$eval('[data-sbs-check]', e => e.filter(i => i.checked).length)) === 0);
  check('reset clears the count', (await countText()).startsWith('0 of '), await countText());
  await page.reload({ waitUntil: 'networkidle2' });
  check('reset persists across a reload', (await countText()).startsWith('0 of '), await countText());

  check('print button revealed by JS',
    await page.$eval('[data-sbs-cl-print]', e => !e.hidden));

  check('no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));

  /* Without JavaScript the checkboxes must still tick and the reset must still
     clear them — that is the whole reason they are real HTML inside a form. */
  const noJs = await browser.newPage();
  await noJs.setJavaScriptEnabled(false);
  if (preview) await noJs.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  await noJs.goto(url, { waitUntil: 'networkidle2' });
  const firstId = await noJs.$eval('[data-sbs-check]', e => e.id);
  await noJs.click(`label[for="${firstId}"]`);
  check('no-JS: a checkbox still ticks',
    await noJs.$eval(`#${firstId}`, e => e.checked));
  await noJs.click('[data-sbs-cl-reset]');
  check('no-JS: native reset still clears it',
    (await noJs.$$eval('[data-sbs-check]', e => e.filter(i => i.checked).length)) === 0);
  check('no-JS: print button stays hidden (it would do nothing)',
    await noJs.$eval('[data-sbs-cl-print]', e => e.hidden));
  await noJs.close();

  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
