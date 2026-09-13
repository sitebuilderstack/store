/* Behavioural test for learning progress.
 *
 * The assertions that matter are the negative ones. Progress that appears
 * without being set, or survives a reset, is worse than no progress feature —
 * so every state is checked in both directions: absent before, present after,
 * absent again after clearing.
 *
 * Nothing here trusts an attribute. `hidden` on a grid container loses to
 * `display: grid`, so visibility is asserted by painted height.
 *
 * Usage: node test-learning.js [--preview <themeId>]
 */
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH ||
            '/home/ubuntu/.cache/chrome-manual/chrome-linux64/chrome';
const ORIGIN = 'https://sitebuilderstack.com';
const pIdx = process.argv.indexOf('--preview');
const preview = pIdx > -1 ? process.argv[pIdx + 1] : null;
const NOISE = ["Framing 'https://shop.app/' violates", 'Error producing monorail event'];

let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d ? '  -> ' + d : ''}`); };

const url = p => ORIGIN + p + (preview ? (p.includes('?') ? '&' : '?') + 'preview_theme_id=' + preview : '');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: EXE, headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  const errors = [];
  const ctx = await browser.createBrowserContext
    ? await browser.createBrowserContext()
    : browser.defaultBrowserContext();

  async function open(path) {
    const page = await ctx.newPage();
    page.on('console', m => {
      if (m.type() === 'error' && !NOISE.some(n => m.text().includes(n))) errors.push(m.text());
    });
    await page.goto(url(path), { waitUntil: 'networkidle2', timeout: 60000 });
    return page;
  }
  const painted = (page, sel) => page.evaluate(s => {
    const e = document.querySelector(s);
    return e ? e.getBoundingClientRect().height > 0 : false;
  }, sel);

  // ── a guide: mark complete and save ───────────────────────────────────────
  let page = await open('/blogs/guides/claude-code-seo-website-optimization');

  const controlsPainted = await painted(page, '[data-sbs-lesson-controls]');
  check('guide: lesson controls appear when storage works', controlsPainted);

  const before = await page.evaluate(() => localStorage.getItem('sbs-learning'));
  check('guide: nothing is stored before any click',
        !before || Object.keys(JSON.parse(before).done || {}).length === 0,
        before || 'empty');

  await page.click('[data-sbs-lesson-done]');
  const afterDone = await page.evaluate(() => ({
    store: JSON.parse(localStorage.getItem('sbs-learning') || '{}'),
    pressed: document.querySelector('[data-sbs-lesson-done]').getAttribute('aria-pressed'),
    label: document.querySelector('[data-sbs-lesson-done-label]').textContent,
  }));
  check('guide: marking complete stores exactly one lesson',
        Object.keys(afterDone.store.done || {}).length === 1,
        Object.keys(afterDone.store.done || {}).join(','));
  check('guide: the key is the unqualified handle, matching the hub',
        !!(afterDone.store.done || {})['claude-code-seo-website-optimization'],
        Object.keys(afterDone.store.done || {})[0]);
  check('guide: the button reports its state to assistive tech',
        afterDone.pressed === 'true' && afterDone.label === 'Completed',
        `aria-pressed=${afterDone.pressed} label="${afterDone.label}"`);

  await page.click('[data-sbs-lesson-save]');
  const afterSave = await page.evaluate(() =>
    JSON.parse(localStorage.getItem('sbs-learning') || '{}'));
  check('guide: saving records a title and a url, not just a flag',
        !!(afterSave.saved || {})['claude-code-seo-website-optimization'] &&
        !!afterSave.saved['claude-code-seo-website-optimization'].u,
        JSON.stringify(afterSave.saved || {}).slice(0, 90));

  // Clicking again must undo, not accumulate.
  await page.click('[data-sbs-lesson-done]');
  const toggled = await page.evaluate(() =>
    JSON.parse(localStorage.getItem('sbs-learning') || '{}'));
  check('guide: clicking complete again clears it',
        Object.keys(toggled.done || {}).length === 0);
  await page.click('[data-sbs-lesson-done]');   // set it again for the next page
  await page.close();

  // ── the hub: progress reflects what was marked ────────────────────────────
  page = await open('/pages/claude-code-seo');
  const hub = await page.evaluate(() => {
    const el = document.querySelector('[data-sbs-path-count]');
    const done = document.querySelectorAll('.sbs-path__item.is-done').length;
    return { text: el ? el.textContent : null, done,
             barPainted: (() => { const b = document.querySelector('[data-sbs-path-progress]');
                                  return b ? b.getBoundingClientRect().height > 0 : false; })() };
  });
  check('hub: the path shows progress from the guide that was marked',
        hub.barPainted && /1 of \d+ complete/.test(hub.text || ''), hub.text);
  check('hub: exactly the marked lesson is struck through', hub.done === 1, String(hub.done));
  await page.close();

  // ── my learning ───────────────────────────────────────────────────────────
  page = await open('/pages/my-learning');
  const my = await page.evaluate(() => ({
    total: document.querySelector('[data-sbs-learn-done]').textContent,
    tracks: document.querySelectorAll('[data-sbs-learn-track]').length,
    lessons: document.querySelectorAll('[data-sbs-lesson]').length,
    ticks: document.querySelectorAll('.sbs-learn__lesson.is-done').length,
    savedShown: document.querySelectorAll('[data-sbs-learn-saved] li').length,
    nextVisible: [...document.querySelectorAll('[data-sbs-learn-next]')]
      .filter(e => !e.hidden).length,
    resetPainted: (() => { const b = document.querySelector('[data-sbs-learn-reset-block]');
                           return b ? b.getBoundingClientRect().height > 0 : false; })(),
  }));
  check('my-learning: counts the completed guide', my.total === '1', my.total);
  check('my-learning: renders every configured track server-side',
        my.tracks >= 4 && my.lessons > my.tracks,
        `${my.tracks} tracks, ${my.lessons} lessons`);
  check('my-learning: ticks the completed lesson', my.ticks === 1, String(my.ticks));
  check('my-learning: lists the saved guide', my.savedShown === 1, String(my.savedShown));
  check('my-learning: offers a next step on a started track',
        my.nextVisible === 1, String(my.nextVisible));
  check('my-learning: offers a reset when there is something to reset', my.resetPainted);

  // Reset must actually clear storage, not just the display.
  await page.evaluate(() => { window.confirm = () => true; });
  await page.click('[data-sbs-learn-reset]');
  const after = await page.evaluate(() => ({
    store: JSON.parse(localStorage.getItem('sbs-learning') || '{}'),
    total: document.querySelector('[data-sbs-learn-done]').textContent,
    ticks: document.querySelectorAll('.sbs-learn__lesson.is-done').length,
    resetPainted: (() => { const b = document.querySelector('[data-sbs-learn-reset-block]');
                           return b ? b.getBoundingClientRect().height > 0 : false; })(),
  }));
  check('my-learning: reset empties storage, not just the view',
        Object.keys(after.store.done || {}).length === 0 &&
        Object.keys(after.store.saved || {}).length === 0,
        JSON.stringify(after.store));
  check('my-learning: the count returns to zero', after.total === '0', after.total);
  check('my-learning: no lesson is left ticked', after.ticks === 0, String(after.ticks));
  check('my-learning: the reset control withdraws once there is nothing to reset',
        !after.resetPainted);
  await page.close();

  // ── without JavaScript the page is still useful ───────────────────────────
  page = await ctx.newPage();
  await page.setJavaScriptEnabled(false);
  await page.goto(url('/pages/my-learning'), { waitUntil: 'networkidle2', timeout: 60000 });
  const noJs = await page.evaluate(() => ({
    tracks: document.querySelectorAll('[data-sbs-learn-track]').length,
    lessons: document.querySelectorAll('[data-sbs-lesson]').length,
    links: document.querySelectorAll('.sbs-learn__lessons a').length,
    controls: (() => { const e = document.querySelector('[data-sbs-learn-reset-block]');
                       return e ? e.getBoundingClientRect().height > 0 : false; })(),
  }));
  /* Compared against what the JS-enabled render produced rather than against a
     literal. The literal was 21 and went stale the day the learning paths were
     extended, reporting a correct page as broken. What matters is that the
     no-JS render contains exactly the same tracks and lessons, whatever that
     number happens to be. */
  check('no-JS: every track and lesson is still a real crawlable list',
        noJs.tracks === my.tracks && noJs.lessons === my.lessons &&
        noJs.links === noJs.lessons && noJs.lessons > 0,
        `${noJs.tracks} tracks, ${noJs.lessons} lessons, ${noJs.links} links ` +
        `(with JS: ${my.tracks} tracks, ${my.lessons} lessons)`);
  check('no-JS: the reset control is not offered', !noJs.controls);
  await page.close();

  check('no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
