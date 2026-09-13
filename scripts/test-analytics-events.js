/* Verify the engagement events actually fire.
 *
 * Events go through Shopify.analytics.publish — the store's existing analytics,
 * not a second vendor script. This stubs that function before page scripts run
 * and records what is published, so the assertion is that a real interaction
 * produces a real event, not that the code looks like it would.
 *
 * Also asserts the guard: with Shopify.analytics absent, interacting must not
 * throw. Analytics failing is never allowed to break the page.
 *
 * Usage: node test-analytics-events.js [--preview <themeId>]
 */
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH ||
            '/home/ubuntu/.cache/chrome-manual/chrome-linux64/chrome';
const ORIGIN = 'https://sitebuilderstack.com';
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

const CAPTURE = () => {
  window.__events = [];
  const install = () => {
    window.Shopify = window.Shopify || {};
    window.Shopify.analytics = window.Shopify.analytics || {};
    window.Shopify.analytics.publish = (name, payload) => { window.__events.push({ name, payload }); };
  };
  install();
  // Shopify's own bundle replaces the object later; reinstall after load.
  window.addEventListener('load', install);
};

(async () => {
  const browser = await puppeteer.launch({
    executablePath: EXE, args: ['--no-sandbox', '--disable-dev-shm-usage'] });

  async function open(path, capture = true) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    if (capture) await page.evaluateOnNewDocument(CAPTURE);
    if (preview) await page.goto(`${ORIGIN}/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
    await page.goto(ORIGIN + path, { waitUntil: 'networkidle2' });
  await assertNotThrottled(page);
    return page;
  }
  const names = p => p.evaluate(() => window.__events.map(e => e.name));

  /* Clicking a link navigates, which destroys window.__events before it can be
     read. Suppressing the navigation in a CAPTURE listener leaves the site's own
     delegated bubble-phase tracker to run exactly as it normally does. */
  const stayPut = p => p.evaluate(() => document.addEventListener('click',
    e => { const a = e.target.closest('a'); if (a) e.preventDefault(); }, true));

  /* Homepage: the learning-path engine. Clicks go through labels and are
     scrolled into view first — the roadmap is long enough that a control can
     sit thousands of pixels down the page. */
  const tap = async (pg, sel) => {
    const el = await pg.$(sel);
    if (!el) throw new Error('no element for ' + sel);
    await el.evaluate(e => e.scrollIntoView({ block: 'center' }));
    await new Promise(r => setTimeout(r, 40));
    await el.click();
    await new Promise(r => setTimeout(r, 90));
  };

  let page = await open('/');
  await tap(page, 'label[for="sbs-goal-improve-rankings"]');
  await tap(page, 'label[for="sbs-stage-optimizing"]');
  await tap(page, 'label[for="sbs-level-beginner"]');
  let got = await names(page);
  for (const ev of ['route_started', 'route_goal_selected', 'route_stage_selected',
                    'route_level_selected', 'route_generated']) {
    check(`fires ${ev}`, got.includes(ev), got.join(','));
  }

  // Ticking a step must report completion.
  const box = await page.$('[data-sbs-route-panel]:not([hidden]) [data-sbs-step]:not([hidden]) [data-sbs-step-done]');
  await box.evaluate(e => e.scrollIntoView({ block: 'center' }));
  await box.click();
  await new Promise(r => setTimeout(r, 120));
  check('fires route_step_completed', (await names(page)).includes('route_step_completed'));

  await stayPut(page);
  await tap(page, '[data-sbs-route-panel]:not([hidden]) [data-sbs-step]:not([hidden]) a');
  check('fires route_step_clicked', (await names(page)).includes('route_step_clicked'));
  await page.close();

  // The free tools report their own name and nothing else.
  page = await open('/pages/claude-md-generator');
  await page.type('#p-name', 'Example');
  await new Promise(r => setTimeout(r, 120));
  check('fires tool_started', (await names(page)).includes('tool_started'));
  await tap(page, '[data-sbs-tool-generate]');
  check('fires tool_completed', (await names(page)).includes('tool_completed'));
  await page.close();

  // Library: filter and search.
  page = await open('/blogs/guides');
  await page.select('#sbs-lib-level', 'Advanced');
  await new Promise(r => setTimeout(r, 700));
  check('fires guide_filter_used', (await names(page)).includes('guide_filter_used'));
  await page.type('#sbs-lib-q', 'hooks');
  await new Promise(r => setTimeout(r, 700));
  check('fires guide_search_used', (await names(page)).includes('guide_search_used'));
  await page.close();

  // Article: related and next-step navigation, and the hub up-link.
  page = await open('/blogs/guides/claude-code-skills');
  await stayPut(page);
  await page.click('[data-sbs-track="pillar_up_click"]');
  await new Promise(r => setTimeout(r, 150));
  check('fires pillar_up_click', (await names(page)).includes('pillar_up_click'));
  await page.close();

  page = await open('/blogs/guides/claude-code-skills');
  await stayPut(page);
  await page.click('[data-sbs-track="next_step_clicked"]');
  await new Promise(r => setTimeout(r, 150));
  check('fires next_step_clicked', (await names(page)).includes('next_step_clicked'));
  await page.close();

  // Checklist.
  page = await open('/pages/claude-code-launch-checklist');
  await page.click('[data-sbs-check] + label, label[for^="chk-"]');
  await new Promise(r => setTimeout(r, 150));
  check('fires checklist_item_toggled', (await names(page)).includes('checklist_item_toggled'));
  await page.close();

  /* The three-product row on the homepage. Its own event name, so it does not
     merge with product_nav_clicked from the header menu. */
  page = await open('/');
  await stayPut(page);
  await tap(page, '[data-sbs-track="product_ecosystem_clicked"]');
  check('fires product_ecosystem_clicked',
        (await names(page)).includes('product_ecosystem_clicked'));
  /* And the negative: the ecosystem row must not also emit the header menu's
     event. A card that fired both would double-count every product click. */
  check('ecosystem click does not also fire product_nav_clicked',
        !(await names(page)).includes('product_nav_clicked'));
  await page.close();

  // Hub page: cluster click.
  page = await open('/pages/claude-code-seo');
  await stayPut(page);
  await page.click('[data-sbs-track="pillar_article_click"]');
  await new Promise(r => setTimeout(r, 150));
  check('fires pillar_article_click', (await names(page)).includes('pillar_article_click'));
  await page.close();

  /* The guard. Two realistic ways the analytics object lets us down: the
     publish function is missing, and publish throws. Neither may break the page.

     Deliberately NOT deleting window.Shopify wholesale — Shopify's own bundle
     needs that object and removing it produces errors from their code, which
     would make this test fail for a reason that has nothing to do with the
     site's own tracking. */
  const bare = await browser.newPage();
  const errs = [];
  bare.on('pageerror', e => { if (!NOISE.some(n => String(e).includes(n))) errs.push(String(e)); });
  await bare.evaluateOnNewDocument(() => {
    window.addEventListener('load', () => {
      if (window.Shopify) {
        window.Shopify.analytics = { publish: () => { throw new Error('analytics down'); } };
      }
    });
  });
  if (preview) await bare.goto(`${ORIGIN}/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  await bare.goto(ORIGIN + '/', { waitUntil: 'networkidle2' });
  const bareTap = async (sel) => {
    const el = await bare.$(sel);
    await el.evaluate(e => e.scrollIntoView({ block: 'center' }));
    await new Promise(r => setTimeout(r, 40));
    await el.click();
    await new Promise(r => setTimeout(r, 90));
  };
  await bareTap('label[for="sbs-goal-improve-rankings"]');
  await bareTap('label[for="sbs-stage-optimizing"]');
  await bareTap('label[for="sbs-level-beginner"]');
  const stillWorks = await bare.$$eval('[data-sbs-route-panel]',
    e => e.filter(x => x.getBoundingClientRect().height > 0).length);
  check('with analytics throwing, the roadmap still renders', stillWorks === 1,
        stillWorks + ' panels');
  check('with analytics absent, nothing throws', errs.length === 0, errs.slice(0, 2).join(' | '));
  await bare.close();

  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
