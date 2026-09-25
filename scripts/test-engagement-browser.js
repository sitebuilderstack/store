/* Browser journey for the engagement layer, against the live site or a
 * theme preview:
 *
 *   guide with a Try-this module → generate → copy → save to My Project
 *   → My Projects shows the artifact and a continue action → rename, task,
 *   export JSON, import (merge) → a lab: wrong answer fails, right answer
 *   passes, complete, save → challenge: tick criteria, save (self-reported)
 *   → storage disabled: everything still works for the visit with a warning
 *   → no-JS: the fallback text is present and no form is exposed
 *   → privacy: no request carries the project name, URL or generated text;
 *     engagement events carry ids only
 *
 * Usage: node test-engagement-browser.js [--preview <themeId>] [--origin URL]
 */
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium-browser';
const pIdx = process.argv.indexOf('--preview');
const preview = pIdx > -1 ? process.argv[pIdx + 1] : null;
const oIdx = process.argv.indexOf('--origin');
const ORIGIN = oIdx > -1 ? process.argv[oIdx + 1] : 'https://sitebuilderstack.com';
const GUIDE = '/blogs/guides/claude-code-technical-seo-audit';
const LAB = '/pages/lab-technical-seo';
const CHALLENGE = '/blogs/weekly-fix/does-your-contact-form-actually-deliver';
const SECRET_NAME = 'Zq7 Private Clinic Site';
const SECRET_URL = 'https://zq7-private.example';
const SECRET_PAGE = '/zq7-secret-page';

let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d && !ok ? '  -> ' + String(d).slice(0, 300) : ''}`); };
const url = (p) => ORIGIN + p;
// Scroll the target to the middle of the viewport first, so a smooth scroll
// started by the page (e.g. after Generate) cannot move it under the cursor.
async function click(pg, sel) {
  await pg.$eval(sel, (el) => el.scrollIntoView({ block: 'center', behavior: 'instant' }));
  await new Promise((r) => setTimeout(r, 120));
  await pg.click(sel);
}

async function main() {
  const browser = await puppeteer.launch({ executablePath: EXE, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 390, height: 844, isMobile: true, hasTouch: true });
  const requests = [];
  const events = [];
  const consoleErrors = [];
  page.on('request', (r) => requests.push({ url: r.url(), body: r.postData() || '' }));
  page.on('pageerror', (e) => consoleErrors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error' && !/shop\.app|monorail|favicon|net::ERR/.test(m.text())) consoleErrors.push(m.text()); });
  // Shopify's preview bar is an iframe fixed to the bottom of the viewport
  // in theme previews; at phone width it sits over the buttons this test
  // clicks. It is not part of the theme, so it is hidden here.
  const hidePreviewBar = () => {
    const add = () => { const st = document.createElement('style'); st.textContent = '#PBarNextFrame, #preview-bar-iframe { display: none !important; }'; (document.head || document.documentElement).appendChild(st); };
    if (document.head) add(); else document.addEventListener('DOMContentLoaded', add);
  };
  await page.evaluateOnNewDocument(hidePreviewBar);
  await page.evaluateOnNewDocument(() => {
    window.__events = [];
    const install = () => {
      window.Shopify = window.Shopify || {};
      window.Shopify.analytics = window.Shopify.analytics || {};
      window.Shopify.analytics.publish = (n, p) => { window.__events.push([n, p]); };
    };
    // Shopify's own bundle replaces the object later; reinstall after load
    // (same approach as test-analytics-events.js).
    install(); document.addEventListener('DOMContentLoaded', install); window.addEventListener('load', install);
  });
  if (preview) await page.goto(url(`/?preview_theme_id=${preview}`), { waitUntil: 'networkidle2' });

  // ---- 1. guide with module ----------------------------------------------
  await page.goto(url(GUIDE), { waitUntil: 'networkidle2' });
  const mod = await page.$('[data-sbs-try]');
  check('guide renders the Try-this module', !!mod);
  await page.waitForFunction(() => document.querySelector('[data-sbs-try].is-ready'), { timeout: 15000 }).catch(() => {});
  check('module is enhanced (form shown, fallback hidden)', await page.evaluate(() => { const r = document.querySelector('[data-sbs-try]'); return r && r.classList.contains('is-ready') && !r.querySelector('form').hidden && r.querySelector('[data-try-fallback]').hidden; }));
  // validation: empty submit keeps inputs and shows message
  await click(page, '[data-sbs-try] button[type="submit"]');
  check('empty submit shows a validation message and no result', await page.evaluate(() => { const r = document.querySelector('[data-sbs-try]'); return !r.querySelector('[data-try-status]').hidden && r.querySelector('[data-try-result]').hidden; }));
  await page.type('#try-pages', SECRET_PAGE);
  await click(page, '[data-sbs-try] button[type="submit"]');
  await page.waitForFunction(() => !document.querySelector('[data-try-result]').hidden, { timeout: 5000 });
  const out = await page.$eval('[data-try-output]', (t) => t.value);
  check('generate produces an editable result containing the typed page', out.includes(SECRET_PAGE) && out.includes('Read-only'), out.slice(0, 100));
  await click(page, '[data-try-copy]');
  await page.waitForFunction(() => /Copied|Ctrl/.test(document.querySelector('[data-try-copy]').textContent), { timeout: 4000 }).catch(() => {});
  check('copy button reports success or the fallback instruction', /Copied|Ctrl/.test(await page.$eval('[data-try-copy]', (b) => b.textContent)));
  await click(page, '[data-try-save]');
  await page.waitForFunction(() => document.querySelector('[data-try-save]').textContent === 'Saved', { timeout: 5000 });
  check('save records the artifact and reveals the next step', await page.evaluate(() => !document.querySelector('[data-try-next]').hidden && /Saved to/.test(document.querySelector('[data-try-status]').textContent)));
  await click(page, '[data-try-save]');
  check('repeated save does not duplicate the artifact', await page.evaluate(() => JSON.parse(localStorage.getItem('sbs-projects')).projects[Object.keys(JSON.parse(localStorage.getItem('sbs-projects')).projects)[0]].artifacts.length === 1));
  let ev = await page.evaluate(() => window.__events);
  const names = ev.map((e) => e[0]);
  check('events: started, generated, copied, saved — each once', ['engagement_module_started', 'artifact_generated', 'artifact_copied', 'artifact_saved'].every((n) => names.filter((x) => x === n).length === 1), names.join(',') + ' | copyBtn=' + await page.$eval('[data-try-copy]', (b) => b.textContent));
  check('events carry ids only (module, guide), never the typed page', ev.filter((e) => /^(engagement|artifact)/.test(e[0])).every((e) => Object.keys(e[1]).every((k) => ['module', 'guide'].includes(k)) && !JSON.stringify(e[1]).includes('zq7')), JSON.stringify(ev.slice(0, 3)));
  const nextHref = await page.$eval('[data-try-next] a', (a) => a.getAttribute('href'));
  check('next step points at the lab', nextHref === LAB, nextHref);

  // ---- 2. My Projects ------------------------------------------------------
  await page.goto(url('/pages/my-projects'), { waitUntil: 'networkidle2' });
  await page.waitForFunction(() => document.querySelector('[data-sbs-projects].is-ready'), { timeout: 15000 });
  check('workspace lists the saved artifact', await page.evaluate(() => document.querySelectorAll('[data-pw-artifacts] .sbs-pw__item').length === 1));
  check('continue action offered (artifact is newest generated)', await page.evaluate(() => /Use what you generated/.test(document.querySelector('[data-pw-next]').textContent)));
  // rename + url + objective
  await click(page, '.sbs-pw__details summary');
  await page.$eval('#pw-e-name', (i) => { i.value = ''; });
  await page.type('#pw-e-name', SECRET_NAME);
  await page.type('#pw-e-url', SECRET_URL);
  await page.type('#pw-e-objective', 'Zq7 more quote requests');
  await click(page, '[data-pw-edit] button[type="submit"]');
  await page.waitForFunction(() => /saved/i.test(document.querySelector('[data-pw-status]').textContent), { timeout: 4000 });
  check('rename persists', (await page.$eval('[data-pw-name]', (h) => h.textContent)) === SECRET_NAME);
  // task
  await page.type('#pw-task', 'Zq7 test the form');
  await click(page, '[data-pw-task-form] button[type="submit"]');
  await page.waitForFunction(() => document.querySelectorAll('[data-pw-tasks] .sbs-pw__task').length === 1, { timeout: 4000 });
  check('task added and becomes the continue action', await page.evaluate(() => /Finish: Zq7 test the form/.test(document.querySelector('[data-pw-next]').textContent)));
  await click(page, '[data-pw-tasks] input[type="checkbox"]');
  await page.waitForFunction(() => document.querySelector('[data-pw-tasks] .sbs-pw__task.is-done'), { timeout: 4000 });
  check('task can be completed', true);
  // export JSON: intercept the download by reading exportJSON directly
  const exported = await page.evaluate(() => window.SBSProjects.exportJSON());
  check('JSON export contains the project and artifact', exported.includes(SECRET_NAME) && exported.includes('sitebuilderstack-projects'));
  // keyboard: tab reaches the New project button and Enter opens the form
  await page.focus('[data-pw-new]'); await page.keyboard.press('Enter');
  check('keyboard: Enter on New project opens the create form', await page.evaluate(() => !document.querySelector('[data-pw-create]').hidden));
  await click(page, '[data-pw-create-cancel]');
  // delete with confirm cancelled → nothing happens
  page.once('dialog', (d) => d.dismiss());
  await click(page, '[data-pw-delete]');
  await new Promise((r) => setTimeout(r, 300));
  check('delete asks for confirmation; cancel keeps the project', (await page.$eval('[data-pw-name]', (h) => h.textContent)) === SECRET_NAME);
  // import merge via the storage API through the UI path is a file input; use the API to validate merge and a malformed file via the UI status
  const merged = await page.evaluate((json) => { const oldId = Object.keys(JSON.parse(json).projects)[0]; return window.SBSProjects.importJSON(json.split(oldId).join('pimportzz'), 'merge'); }, exported);
  check('import (merge) via the store adds a second project', merged.ok && merged.added === 1);
  const bad = await page.evaluate(() => window.SBSProjects.importJSON('{"format":"other"}', 'replace'));
  check('malformed import is rejected and existing projects survive', !bad.ok && (await page.evaluate(() => window.SBSProjects.list().length)) === 2);
  ev = await page.evaluate(() => window.__events);
  check('workspace events carry no project data', ev.every((e) => !JSON.stringify(e[1]).includes('Zq7') && !JSON.stringify(e[1]).includes('zq7')), JSON.stringify(ev));

  // ---- 3. lab ----------------------------------------------------------------
  await page.goto(url(LAB), { waitUntil: 'networkidle2' });
  await page.waitForFunction(() => document.querySelector('[data-lab-app]') && !document.querySelector('[data-lab-app]').hidden, { timeout: 30000 });
  check('lab renders scenario, declared sample data and step 1', await page.evaluate(() => { const a = document.querySelector('[data-lab-app]'); return /Scenario/.test(a.textContent) && /sample data/i.test(a.textContent) && /Step 1 of/.test(a.textContent); }));
  check('static version is hidden once the engine renders; product links hidden until the end', await page.evaluate(() => document.querySelector('[data-lab-static]').hidden && document.querySelector('.sbs-lab__links').hidden));
  const fixture = await page.$eval('[data-lab-fixture]', (s) => JSON.parse(s.textContent));
  // deliberately wrong answer on step 1
  const s1 = fixture.steps[0];
  const wrong = s1.decision.options.find((o) => o.id !== s1.decision.correct).id;
  await click(page, `#lab-${s1.id}-${wrong}`);
  await click(page, '[data-lab-app] .sbs-lab__actions button');
  check('a deliberately wrong answer fails with an explanation', await page.evaluate(() => { const f = document.querySelector('.sbs-lab__feedback'); return f && !f.hidden && f.classList.contains('is-error') && f.textContent.length > 40; }));
  check('wrong answer does not reveal the Next button', await page.evaluate(() => document.querySelectorAll('[data-lab-app] .sbs-lab__actions button')[1].hidden));
  await click(page, `#lab-${s1.id}-${s1.decision.correct}`);
  await click(page, '[data-lab-app] .sbs-lab__actions button');
  check('the correct answer passes and reveals Next', await page.evaluate(() => document.querySelector('.sbs-lab__feedback').classList.contains('is-ok') && !document.querySelectorAll('[data-lab-app] .sbs-lab__actions button')[1].hidden));
  // finish remaining steps correctly
  for (let i = 0; i < fixture.steps.length; i++) {
    await click(page, '[data-lab-app] .sbs-lab__actions button:not([hidden]):nth-of-type(2), [data-lab-app] .sbs-lab__actions button:nth-of-type(2)');
    if (i + 1 < fixture.steps.length) {
      const s = fixture.steps[i + 1];
      await page.waitForSelector(`#lab-${s.id}-${s.decision.correct}`);
      await click(page, `#lab-${s.id}-${s.decision.correct}`);
      await click(page, '[data-lab-app] .sbs-lab__actions button');
      await page.waitForFunction(() => document.querySelector('.sbs-lab__feedback.is-ok'));
    }
  }
  await page.waitForFunction(() => document.querySelector('.sbs-lab__end'), { timeout: 5000 });
  check('lab end shows the corrected version and first-attempt score 3 of 4', await page.evaluate(() => /3 of 4/.test(document.querySelector('.sbs-lab__score').textContent) && /corrected version/i.test(document.querySelector('.sbs-lab__end h2').textContent)));
  check('product link appears only after the lab delivered value', await page.evaluate(() => !document.querySelector('.sbs-lab__links').hidden && !!document.querySelector('.sbs-lab__next a[href^="/products/"]')));
  await click(page, '.sbs-lab__end .sbs-lab__actions button');
  await page.waitForFunction(() => document.querySelector('.sbs-lab__end .sbs-lab__actions button').textContent === 'Saved', { timeout: 5000 });
  const labRec = await page.evaluate(() => window.SBSProjects.active().labs['technical-seo']);
  check('lab saved as example-verified with score', labRec && labRec.state === 'example-verified' && labRec.score === 3, JSON.stringify(labRec));
  ev = await page.evaluate(() => window.__events);
  check('lab events: lab_started once, lab_completed once, ids only', ev.filter((e) => e[0] === 'lab_started').length === 1 && ev.filter((e) => e[0] === 'lab_completed').length === 1 && ev.filter((e) => /^lab_/.test(e[0])).every((e) => JSON.stringify(e[1]) === '{"lab":"technical-seo"}'), JSON.stringify(ev));
  // reset
  await click(page, '.sbs-lab__end .sbs-lab__actions button:last-of-type');
  check('reset returns to step 1', await page.evaluate(() => /Step 1 of/.test(document.querySelector('[data-lab-app]').textContent)));

  // ---- 4. challenge --------------------------------------------------------
  await page.goto(url(CHALLENGE), { waitUntil: 'networkidle2' });
  await page.waitForFunction(() => document.querySelector('[data-sbs-challenge].is-ready'), { timeout: 15000 });
  check('challenge renders the criteria checklist and the copyable prompt', await page.evaluate(() => document.querySelectorAll('[data-sbs-challenge] input[type="checkbox"]').length === 5 && !!document.querySelector('pre[data-sbs-copy="prompt"]')));
  await click(page, '[data-ch-start]');
  await click(page, '[data-ch-save]');
  await page.waitForFunction(() => /in progress/i.test(document.querySelector('[data-ch-status]').textContent), { timeout: 4000 });
  check('partial completion saves as in progress', await page.evaluate(() => window.SBSProjects.active().challenges['contact-form-delivers'].state === 'in-progress'));
  await page.$$eval('[data-sbs-challenge] input[type="checkbox"]', (cbs) => cbs.forEach((c) => c.click()));
  await click(page, '[data-ch-save]');
  await page.waitForFunction(() => /self-reported/i.test(document.querySelector('[data-ch-status]').textContent), { timeout: 4000 });
  check('all criteria ticked saves as self-reported (never verified)', await page.evaluate(() => window.SBSProjects.active().challenges['contact-form-delivers'].state === 'self-reported'));
  ev = await page.evaluate(() => window.__events);
  check('challenge events: started once, completed once, ids only', ev.filter((e) => e[0] === 'challenge_started').length === 1 && ev.filter((e) => e[0] === 'challenge_completed').length === 1 && ev.filter((e) => /^challenge_/.test(e[0])).every((e) => JSON.stringify(e[1]) === '{"challenge":"contact-form-delivers"}'), JSON.stringify(ev));

  // ---- 5. privacy: nothing typed left the browser ------------------------------
  const leaked = requests.filter((r) => /zq7|Zq7/.test(r.url) || /zq7|Zq7/.test(r.body));
  check('no network request carried the project name, URL, objective or typed page', leaked.length === 0, leaked.map((r) => r.url).join(' '));
  check('no page errors during the journey', consoleErrors.length === 0, consoleErrors.join(' | '));

  // ---- 6. storage disabled ---------------------------------------------------------
  const blocked = await browser.newPage();
  await blocked.setViewport({ width: 390, height: 844, isMobile: true });
  await blocked.evaluateOnNewDocument(hidePreviewBar);
  await blocked.evaluateOnNewDocument(() => { Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked'); } }); });
  if (preview) await blocked.goto(url(`/?preview_theme_id=${preview}`), { waitUntil: 'networkidle2' });
  await blocked.goto(url('/pages/my-projects'), { waitUntil: 'networkidle2' });
  await blocked.waitForFunction(() => document.querySelector('[data-sbs-projects].is-ready'), { timeout: 15000 });
  check('storage disabled: warning shown', await blocked.evaluate(() => !document.querySelector('[data-pw-storage]').hidden && /not letting the site remember/.test(document.querySelector('[data-pw-storage]').textContent)));
  await click(blocked, '[data-pw-new]'); await blocked.type('#pw-c-name', 'Temp'); await click(blocked, '[data-pw-create] button[type="submit"]');
  await blocked.waitForFunction(() => document.querySelector('[data-pw-name]') && document.querySelector('[data-pw-name]').textContent === 'Temp', { timeout: 4000 });
  check('storage disabled: project works in memory and says it is for this visit only', await blocked.evaluate(() => /this visit only/.test(document.querySelector('[data-pw-status]').textContent)));
  await blocked.close();

  // ---- 7. no JavaScript --------------------------------------------------------------
  const nojs = await browser.newPage();
  await nojs.setJavaScriptEnabled(false);
  if (preview) await nojs.goto(url(`/?preview_theme_id=${preview}`), { waitUntil: 'networkidle2' });
  await nojs.goto(url(GUIDE), { waitUntil: 'networkidle2' });
  check('no-JS guide: module fallback text visible, form hidden', await nojs.evaluate(() => { const r = document.querySelector('[data-sbs-try]'); return r && r.querySelector('form').hidden && !r.querySelector('[data-try-fallback]').hidden; }));
  await nojs.goto(url(LAB), { waitUntil: 'networkidle2' });
  check('no-JS lab: complete static lab with answers is readable', await nojs.evaluate(() => { const s = document.querySelector('[data-lab-static]'); return s && !s.hidden && s.querySelectorAll('details').length >= 3 && !!document.querySelector('.sbs-lab__links a[href^="/products/"]'); }));
  await nojs.goto(url('/pages/my-projects'), { waitUntil: 'networkidle2' });
  check('no-JS workspace: explains that there is nothing to show without JavaScript', await nojs.evaluate(() => !document.querySelector('[data-pw-nojs]').hidden));
  await nojs.close();

  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
}
main().catch((e) => { console.error(e); process.exit(1); });
