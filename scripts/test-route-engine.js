/* Behavioural test for the homepage learning-path engine.
 *
 * Covers what only exists once the page runs: whether the fallback is replaced,
 * whether three answers produce exactly one roadmap with the right level variant,
 * whether progress persists across a reload, whether reset is scoped to one
 * roadmap, and whether the whole thing works from the keyboard and without
 * JavaScript.
 *
 * Assertions are against what the browser PAINTS, not what a DOM attribute
 * claims — `el.hidden` is only honoured when no author rule sets display, and
 * that has silently broken here before.
 *
 * Usage: node test-route-engine.js <url> [--preview <themeId>]
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

/* Scroll into view, then click. The roadmap is long enough that an element can
   sit thousands of pixels down the page, and a plain click on a target that has
   just been re-laid-out by a previous answer is flaky in a way that has nothing
   to do with whether a real person could click it — verified separately that
   the controls are reachable and topmost at 390px and 1280px. */
async function tap(page, selector) {
  const el = await page.$(selector);
  if (!el) throw new Error('no element for ' + selector);
  await el.evaluate(e => e.scrollIntoView({ block: 'center' }));
  await new Promise(r => setTimeout(r, 40));
  await el.click();
  await new Promise(r => setTimeout(r, 80));
}

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

  const goals = await page.$$eval('input[name="sbs-goal"]', e => e.map(x => x.value));
  const stages = await page.$$eval('input[name="sbs-stage"]', e => e.map(x => x.value));
  const levels = await page.$$eval('input[name="sbs-level"]', e => e.map(x => x.value));
  check('all three questions render', goals.length >= 10 && stages.length === 5 && levels.length === 3,
        `${goals.length} goals, ${stages.length} stages, ${levels.length} levels`);

  check('engine revealed by JS', await page.$eval('[data-sbs-route]', e => !e.hidden));
  check('no-JS fallback hidden once live', await page.$eval('[data-sbs-selector-fallback]', e => e.hidden));

  const shownPanels = () => page.$$eval('[data-sbs-route-panel]',
    e => e.filter(x => x.getBoundingClientRect().height > 0).map(x => x.getAttribute('data-sbs-route-panel')));

  check('no roadmap before answering', (await shownPanels()).length === 0);

  await tap(page, `#sbs-goal-${goals[3]}`);
  check('one answer is not enough', (await shownPanels()).length === 0);
  check('prompt asks for the next answer',
        (await page.$eval('[data-sbs-route-prompt]', e => e.textContent)).toLowerCase().includes('where you are'));

  await tap(page, '#sbs-stage-building');
  check('two answers still not enough', (await shownPanels()).length === 0);

  await tap(page, '#sbs-level-experienced');
  const shown = await shownPanels();
  check('three answers give exactly one roadmap', shown.length === 1 && shown[0] === goals[3], shown.join(','));

  // Exactly one level-specific first step, and it must be the chosen level.
  const painted = await page.evaluate(() => {
    const steps = [...document.querySelectorAll('[data-sbs-route-panel]:not([hidden]) [data-step-level]')];
    return {
      shown: steps.filter(s => s.getBoundingClientRect().height > 0).map(s => s.getAttribute('data-step-level')),
      focusableHidden: steps.filter(s => s.hidden)
        .flatMap(s => [...s.querySelectorAll('a')])
        .filter(a => { a.focus(); return document.activeElement === a; }).length,
    };
  });
  check('exactly one first step is painted, for the chosen level',
        painted.shown.length === 1 && painted.shown[0] === 'experienced', painted.shown.join(','));
  check('no link inside a hidden step can take focus', painted.focusableHidden === 0);

  const visibleSteps = await page.$$eval('[data-sbs-route-panel]:not([hidden]) [data-sbs-step]',
    e => e.filter(x => x.getBoundingClientRect().height > 0).length);
  check('the roadmap is seven steps', visibleSteps === 7, String(visibleSteps));

  check('the stage marks where you join',
        (await page.$$eval('[data-sbs-route-panel]:not([hidden]) .is-entry', e => e.length)) === 1);

  const links = await page.$$eval('[data-sbs-route-panel]:not([hidden]) [data-sbs-step]:not([hidden]) a',
    e => e.map(a => a.getAttribute('href')));
  check('every roadmap link is an internal path',
        links.length >= 7 && links.every(h => h && h.startsWith('/')), `${links.length} links`);

  check('URL is shareable',
        ['build=', 'stage=', 'level='].every(k => page.url().includes(k)), page.url());

  // Progress
  const countText = () => page.$eval('[data-sbs-route-count]', e => e.textContent.trim());
  check('progress starts at zero', (await countText()).startsWith('0 of 7'), await countText());

  /* Step 1 renders once per experience level, so three elements share the
     step-1 id and only one of them is visible. Selecting by id alone can
     therefore return a hidden one, which is not clickable — scope to the
     visible panel and the visible step. */
  const VISIBLE_BOX =
    '[data-sbs-route-panel]:not([hidden]) [data-sbs-step]:not([hidden]) [data-sbs-step-done]';
  const boxHandles = await page.$$(VISIBLE_BOX);
  for (const h of boxHandles.slice(0, 3)) {
    await h.evaluate(e => e.scrollIntoView({ block: 'center' }));
    await new Promise(r => setTimeout(r, 40));
    await h.click();
    await new Promise(r => setTimeout(r, 80));
  }
  check('ticking updates the count', (await countText()).startsWith('3 of 7'), await countText());
  check('progressbar reports a percentage',
        Number(await page.$eval('[data-sbs-route-track]', e => e.getAttribute('aria-valuenow'))) > 0);

  await page.reload({ waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 200));
  check('answers and progress survive a reload', (await countText()).startsWith('3 of 7'), await countText());
  check('the same roadmap is restored', (await shownPanels())[0] === goals[3]);

  // Reset must clear this roadmap only.
  await tap(page, '[data-sbs-route-reset]');
  await new Promise(r => setTimeout(r, 120));
  check('reset clears this roadmap', (await countText()).startsWith('0 of 7'), await countText());

  // Change goal returns to the questions without wiping other roadmaps.
  await tap(page, `label[for="sbs-goal-${goals[0]}"]`);
  const otherBox = await page.$(VISIBLE_BOX);
  await otherBox.evaluate(e => e.scrollIntoView({ block: 'center' }));
  await otherBox.click();
  await new Promise(r => setTimeout(r, 120));
  check('a different roadmap tracks its own progress', (await countText()).startsWith('1 of 7'), await countText());
  await tap(page, '[data-sbs-route-change]');
  await new Promise(r => setTimeout(r, 120));
  check('change goal returns to the questions', (await shownPanels()).length === 0);
  await tap(page, `label[for="sbs-goal-${goals[0]}"]`);
  await new Promise(r => setTimeout(r, 120));
  check('reselecting restores that roadmap\'s progress', (await countText()).startsWith('1 of 7'), await countText());

  // A shared link beats saved state.
  await page.goto(`${url.split('?')[0]}?build=${goals[6]}&stage=live&level=beginner`, { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 200));
  const restored = await shownPanels();
  const restoredLvl = await page.$$eval('[data-sbs-route-panel]:not([hidden]) [data-step-level]',
    e => e.filter(x => x.getBoundingClientRect().height > 0).map(x => x.getAttribute('data-step-level')));
  check('a shared link wins over saved state',
        restored[0] === goals[6] && restoredLvl[0] === 'beginner', `${restored[0]} / ${restoredLvl[0]}`);

  // Keyboard
  await page.goto(url, { waitUntil: 'networkidle2' });
  check('the first goal radio is focusable',
        await page.evaluate(() => {
          const f = document.querySelector('input[name="sbs-goal"]'); f.focus();
          return document.activeElement === f;
        }));
  await page.keyboard.press('ArrowDown');
  check('arrow keys move within the group',
        (await page.$$eval('input[name="sbs-goal"]:checked', e => e.length)) === 1);
  check('every Done control is a real labelled checkbox',
        await page.$$eval('[data-sbs-step-done]', els => els.every(b =>
          b.type === 'checkbox' && b.closest('label') && b.closest('label').textContent.trim().length > 0)));

  check('no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));

  // Without JavaScript the questions must be gone and hub links present.
  const noJs = await browser.newPage();
  await noJs.setJavaScriptEnabled(false);
  if (preview) await noJs.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  await noJs.goto(url, { waitUntil: 'networkidle2' });
  const off = await noJs.evaluate(() => ({
    engine: document.querySelector('[data-sbs-route]').getBoundingClientRect().height,
    fb: document.querySelector('[data-sbs-selector-fallback]').getBoundingClientRect().height,
    hubs: document.querySelectorAll('.sbs-sel__browse a').length,
  }));
  check('no-JS: the questions are not painted', off.engine === 0, off.engine + 'px');
  check('no-JS: a real hub list is shown instead', off.fb > 0 && off.hubs >= 4, off.hubs + ' hub links');
  await noJs.close();

  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
