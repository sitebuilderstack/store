#!/usr/bin/env node
/* tests/test-browser.js — the built page, driven in a real browser.
 *
 *   PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser node tests/test-browser.js
 *
 * Runs against tests/preview.html, which build.py writes: the published
 * file inside the same document shell the Artifact runtime wraps it in.
 */
'use strict';
const path = require('path');
const fs = require('fs');
let puppeteer;
try { puppeteer = require('puppeteer-core'); } catch (e) { puppeteer = require('puppeteer'); }

const http = require('http');
const SRC = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const PREVIEW = fs.readFileSync(path.join(__dirname, 'preview.html'), 'utf8');
/* Served over HTTP rather than file://, so the page runs on a real origin
   with a real document.referrer story, the way the artifact viewer serves it. */
const server = http.createServer((req, res) => {
  if (req.url === '/' || req.url.startsWith('/index')) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(PREVIEW);
  } else if (req.url === '/favicon.ico') { res.writeHead(204); res.end(); }
  else { res.writeHead(404); res.end('not found'); }
});
let FILE = '';

let pass = 0, fail = 0;
const fails = [];
function t(name, cond, detail) {
  if (cond) { pass++; console.log('  ✓ ' + name); }
  else { fail++; fails.push(name + (detail ? ' — ' + detail : '')); console.log('  ✗ ' + name + (detail ? '\n      ' + detail : '')); }
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function clickOptionByText(page, text) {
  const done = await page.evaluate((txt) => {
    const labels = Array.from(document.querySelectorAll('label.opt'));
    const hit = labels.find(l => l.textContent.trim().toLowerCase().startsWith(txt.toLowerCase()));
    if (!hit) return false;
    hit.querySelector('input').click();
    return true;
  }, text);
  await sleep(40);
  return done;
}
async function clickButton(page, text) {
  const done = await page.evaluate((txt) => {
    const b = Array.from(document.querySelectorAll('button')).find(x => x.textContent.trim() === txt && !x.disabled);
    if (!b) return false; b.click(); return true;
  }, text);
  await sleep(60);
  return done;
}
async function text(page) { return page.evaluate(() => document.body.innerText); }

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  FILE = 'http://127.0.0.1:' + server.address().port + '/';
  const browser = await puppeteer.launch({
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium-browser',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });

  /* ---------- 1. static source checks ---------- */
  console.log('\nPublished source\n');
  t('No <html>, <head> or <body> wrapper in the published file', !/<\s*(html|head|body)[\s>]/i.test(SRC));
  t('A <title> is present in the first 8 KB', /<title>SiteBuilderStack Website Action Planner<\/title>/.test(SRC.slice(0, 8192)));
  t('No external script, stylesheet, font or image', !/<(script|link|img)[^>]+(src|href)\s*=\s*["']https?:/i.test(SRC));
  const links = SRC.match(/https?:\/\/[^"'\s)]+/g) || [];
  const offsite = [...new Set(links)].filter(u => !/^https:\/\/sitebuilderstack\.com/.test(u) && !/^https:\/\/claude\.ai\/artifact\//.test(u));
  t('Every absolute URL in the source points at sitebuilderstack.com', offsite.length === 0, offsite.join(', '));
  const secrets = /shpat_|shpss_|shpca_|SHOPIFY_CLIENT_SECRET|BEGIN [A-Z ]*PRIVATE KEY|api[_-]?key\s*[:=]\s*["'][A-Za-z0-9]{16}/i;
  t('No credential-shaped string in the published source', !secrets.test(SRC));
  t('No paid product file contents are embedded', !/01-technical-seo\/[a-z-]+\.md|BEGIN MODULE/i.test(SRC));
  t('Rendered page is well under the 16 MiB limit', Buffer.byteLength(SRC) < 16 * 1024 * 1024, Buffer.byteLength(SRC) + ' bytes');
  const allowed = ['primary_recommendation', 'recommendation_repeat', 'complementary_recommendation', 'bundle_comparison', 'product_comparison', 'free_next_step', 'example_result', 'header_brand', 'footer_brand', 'share_planner'];
  const used = [...new Set((SRC.match(/utm_content=([a-z_]+)/g) || []).map(s => s.split('=')[1]))];
  t('Static utm_content values are all from the documented list', used.every(u => allowed.includes(u)), used.join(', '));

  /* ---------- 2. a real render ---------- */
  console.log('\nFirst screen\n');
  const page = await browser.newPage();
  const consoleErrors = [];
  const requests = [];
  page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('pageerror', e => consoleErrors.push('pageerror: ' + e.message));
  page.on('request', r => requests.push(r.url()));
  await page.setViewport({ width: 390, height: 844, isMobile: true });
  await page.goto(FILE, { waitUntil: 'networkidle0' });

  let body = await text(page);
  t('The headline renders', body.includes('Find your next website move.'));
  t('The supporting text renders', body.includes('practical action plan'));
  t('Both primary and secondary actions are present', body.includes('Build my free plan') && body.includes('See an example'));
  t('It states the plan is free and needs no email', /No email address is required/i.test(body));
  t('It states it does not scan a website', /does not scan, crawl or audit/i.test(body));
  t('It discloses that SiteBuilderStack made it', /made by SiteBuilderStack and recommends SiteBuilderStack products/i.test(body));
  t('The brand links to the storefront', await page.$('a.brand[href^="https://sitebuilderstack.com/"]') !== null);

  async function overflow() {
    return page.evaluate(() => ({
      scroll: document.documentElement.scrollWidth,
      client: document.documentElement.clientWidth,
      widest: (() => {
        let worst = null, w = 0;
        document.querySelectorAll('*').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.right > w) { w = r.right; worst = el.tagName + '.' + (el.className || ''); }
        });
        return worst + ' @ ' + Math.round(w);
      })(),
    }));
  }
  let o = await overflow();
  t('No horizontal overflow at 390px (intro)', o.scroll <= o.client + 1, JSON.stringify(o));

  /* ---------- 3. the example ---------- */
  console.log('\nExample project\n');
  await clickButton(page, 'See an example');
  body = await text(page);
  t('The example is clearly labelled', /Example project\./.test(body));
  t('The example says it is not a case study', /not a real customer, not a case study/i.test(body));
  t('The example produces a full result', /Three prioritised actions/.test(body) && /free starter Claude Code prompt/i.test(body));
  o = await overflow();
  t('No horizontal overflow at 390px (result)', o.scroll <= o.client + 1, JSON.stringify(o));
  const exCtas = await page.$$eval('a[data-cta]', els => els.map(e => e.dataset.cta));
  t('Example CTAs use the example placement, not the real one', exCtas.length > 0 && exCtas.every(c => c === 'example_result'), exCtas.join(','));
  await clickButton(page, 'Build my own plan');
  t('The example hands off to the real questionnaire', (await text(page)).includes('What are you trying to do?'));

  /* ---------- 4. the questionnaire ---------- */
  console.log('\nQuestionnaire\n');
  await page.goto(FILE, { waitUntil: 'networkidle0' });
  await clickButton(page, 'Build my free plan');
  body = await text(page);
  t('Step 1 of 6 is shown', /Step 1 of 6/.test(body));
  t('Next is disabled until an answer is chosen', await page.evaluate(() => document.getElementById('next').disabled));
  await clickOptionByText(page, 'Improve search visibility');
  t('Next becomes enabled after an answer', await page.evaluate(() => !document.getElementById('next').disabled));
  t('A second goal is offered as optional', (await text(page)).includes('Add a second goal (optional)'));

  await clickButton(page, 'Next');
  t('Step 2 asks for the platform', (await text(page)).includes('What is the site built on?'));
  await clickOptionByText(page, 'WordPress');
  await clickButton(page, 'Next');
  await clickOptionByText(page, 'Live, receiving traffic');
  await clickButton(page, 'Next');
  body = await text(page);
  t('The contextual question matches the goal', /Which of these is closest to what you are seeing/.test(body));
  t('An irrelevant contextual question is not asked', !/Which repetitive administrative task/.test(body));
  t('"Not sure" is available', /Not sure/.test(body));
  await clickOptionByText(page, 'Pages are indexed but rank for nothing');
  await clickButton(page, 'Next');
  await clickOptionByText(page, 'I already use Claude Code');
  await clickButton(page, 'Next');
  body = await text(page);
  t('Ownership is optional and explained', /No login, no purchase history/.test(body));
  await clickOptionByText(page, 'I own none of them');
  t('The final button says what it does', (await text(page)).includes('Show my plan'));

  /* back navigation */
  console.log('\nBack navigation and answer changes\n');
  await clickButton(page, 'Back');
  await clickButton(page, 'Back');
  body = await text(page);
  t('Back returns to the contextual step', /Which of these is closest to what you are seeing/.test(body));
  t('Back preserves the earlier answer', await page.evaluate(() => {
    const i = Array.from(document.querySelectorAll('input[name="seo_symptom"]')).find(x => x.value === 'indexed_no_rank');
    return !!i && i.checked;
  }));
  await clickButton(page, 'Back'); await clickButton(page, 'Back'); await clickButton(page, 'Back');
  t('Back reaches step 1 with the goal still selected', await page.evaluate(() => {
    const i = Array.from(document.querySelectorAll('input[name="goal"]')).find(x => x.value === 'seo');
    return !!i && i.checked;
  }));

  /* changing the goal must clear the dependent answer */
  await clickOptionByText(page, 'Migrate to another platform');
  const cleared = await page.evaluate(() => window.__planner.state.answers.seo_symptom === undefined);
  t('Changing the goal discards the dependent answer', cleared);
  await clickButton(page, 'Next'); await clickButton(page, 'Next'); await clickButton(page, 'Next');
  body = await text(page);
  t('The new goal asks its own questions', /What are you moving from/.test(body) && /What are you moving to/.test(body));
  t('Next stays disabled until both are answered', await page.evaluate(() => document.getElementById('next').disabled));
  await clickOptionByText(page, 'WordPress');
  await clickOptionByText(page, 'Astro');
  t('Next enables once both are answered', await page.evaluate(() => !document.getElementById('next').disabled));

  /* reset */
  await clickButton(page, 'Start again');
  body = await text(page);
  t('Start again returns to the first screen', body.includes('Find your next website move.'));
  t('Start again clears the answers', await page.evaluate(() => Object.keys(window.__planner.state.answers).length === 1));

  /* ---------- 5. a complete result ---------- */
  console.log('\nThe result\n');
  await page.setViewport({ width: 1280, height: 900 });
  await page.evaluate(() => { try { sessionStorage.clear(); } catch (e) {} });
  await page.goto(FILE, { waitUntil: 'networkidle0' });
  await clickButton(page, 'Build my free plan');
  await clickOptionByText(page, 'Turn existing traffic');
  await clickButton(page, 'Next');
  await clickOptionByText(page, 'Shopify');
  await clickButton(page, 'Next');
  await clickOptionByText(page, 'Live, receiving traffic');
  await clickButton(page, 'Next');
  await clickOptionByText(page, 'Yes — analytics is installed');
  await clickButton(page, 'Next');
  await clickOptionByText(page, 'I already use Claude Code');
  await clickButton(page, 'Next');
  await clickOptionByText(page, 'I own none of them');
  await clickButton(page, 'Show my plan');
  body = await text(page);
  t('All five result sections render', ['Recommended because you selected', 'Three prioritised actions', 'free starter Claude Code prompt', 'Your recommended toolkit', 'A free next step'].every(s => body.toLowerCase().includes(s.toLowerCase())));
  t('The matched product is the Conversion toolkit', body.includes('Claude Code Conversion & Revenue Optimization Toolkit'));
  t('The verified price is shown', body.includes('$19.99'));
  t('A reason not to buy yet is shown', /might not be for you yet/i.test(body));
  t('Free vs paid is explained', /Free plan vs the product/i.test(body));
  t('No fabricated match score', !/\d+% match/i.test(body));
  const ctas = await page.$$eval('a[data-cta]', els => els.map(e => ({ href: e.href, target: e.target, rel: e.rel, cta: e.dataset.cta })));
  t('The primary CTA links to the exact product page', ctas.some(c => c.href.startsWith('https://sitebuilderstack.com/products/claude-code-conversion-revenue-optimization-toolkit?')));
  t('Every CTA carries the campaign parameters', ctas.every(c => c.href.includes('utm_source=claude_artifact') && c.href.includes('utm_medium=interactive_tool') && c.href.includes('utm_campaign=website_action_planner')));
  t('Every CTA placement is from the documented list', ctas.every(c => allowed.includes(c.cta)), ctas.map(c => c.cta).join(','));
  t('CTAs open in a new tab with rel=noopener', ctas.every(c => c.target === '_blank' && /noopener/.test(c.rel)));
  t('No CTA is labelled "Complete purchase"', !/complete purchase/i.test(body));
  const btnCount = await page.$$eval('a[data-cta]', e => e.length);
  t('The default result does not show eight purchase buttons', btnCount <= 3, btnCount + ' product links');
  t('The free next step is present and secondary', await page.$('a[data-free]') !== null);

  o = await overflow();
  t('No horizontal overflow at 1280px', o.scroll <= o.client + 1, JSON.stringify(o));
  await page.setViewport({ width: 390, height: 844 });
  await sleep(120);
  o = await overflow();
  t('No horizontal overflow at 390px (full result)', o.scroll <= o.client + 1, JSON.stringify(o));

  /* comparison on demand */
  const opened = await page.evaluate(() => {
    const d = Array.from(document.querySelectorAll('details.more')).find(x => /Compare the bundle/.test(x.textContent));
    if (!d) return false; d.open = true; return true;
  });
  await sleep(60);
  body = await text(page);
  t('The product comparison is available on demand', opened && /every product, for reference/i.test(body));
  t('The comparison lists all eight products', await page.$$eval('table.table tbody tr', r => r.length) === 8);
  t('The bundle contents are stated accurately', /bundle is these three products only/i.test(body));
  t('The bundle is not described as seven products', !/seven products/i.test(body));

  /* ---------- 6. copy, export, share ---------- */
  console.log('\nCopy, export and share\n');
  await page.evaluate(() => {
    window.__copied = null;
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: (t) => { window.__copied = t; return Promise.resolve(); } } });
  });
  await clickButton(page, 'Copy prompt');
  await sleep(80);
  const copied = await page.evaluate(() => window.__copied);
  t('Copy prompt puts the prompt on the clipboard', typeof copied === 'string' && copied.includes('STOP HERE'));
  t('Success is shown only after success', (await page.$eval('#prompt-status', e => e.textContent)) === 'Copied.');
  await clickButton(page, 'Copy action plan');
  await sleep(80);
  const plan = await page.evaluate(() => window.__copied);
  t('Copy action plan copies the whole plan as Markdown', plan.includes('# Your SiteBuilderStack website action plan') && plan.includes('## Three prioritised actions'));
  t('The export carries the attribution and the caveat', plan.includes('https://sitebuilderstack.com') && plan.includes('self-reported answers'));
  t('The export contains no tracking parameters', !plan.includes('utm_'));

  await page.evaluate(() => {
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: () => Promise.reject(new Error('blocked')) } });
  });
  await clickButton(page, 'Copy prompt');
  await sleep(100);
  const st = await page.$eval('#prompt-status', e => e.textContent);
  const fb = await page.$('#prompt-fallback textarea');
  t('A refused clipboard reports failure rather than success', /could not copy/i.test(st));
  t('A refused clipboard offers selectable text instead', fb !== null);
  t('The fallback holds the real text', fb !== null && (await page.$eval('#prompt-fallback textarea', e => e.value)).includes('OBJECTIVE'));

  const exportHidden = await page.evaluate(() => { const b = document.getElementById('export-plan'); return !b || b.hidden; });
  t('Export is hidden when the downloads capability is absent', exportHidden);
  t('...and the page says so rather than failing silently', /File export is not available in this view/.test(await text(page)));
  await page.evaluate(() => { Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: (t) => { window.__copied = t; return Promise.resolve(); } } }); });
  await clickButton(page, 'Share the planner');
  await sleep(120);
  const shared = await page.evaluate(() => window.__copied);
  t('Share copies the planner\u2019s own URL', /^https:\/\/claude\.ai\/artifact\//.test(String(shared)), String(shared));
  t('The shared link carries no answers', !/goal|platform|stage|owns|seo_symptom|\?/.test(String(shared)));
  t('Share says what was copied', /your answers are not in it/i.test(await page.$eval('#plan-status', e => e.textContent)));

  /* ---------- 7. measurement ---------- */
  console.log('\nMeasurement\n');
  const journal = await page.evaluate(() => window.SBSPlannerAnalytics.journal());
  const names = journal.map(j => j.event);
  t('The expected events fired', ['artifact_opened', 'planner_started', 'planner_completed', 'recommendation_viewed', 'starter_prompt_copied'].every(n => names.includes(n)), names.join(','));
  t('One-shot events fire once', names.filter(n => n === 'artifact_opened').length === 1);
  const props = new Set(journal.flatMap(j => Object.keys(j.props)));
  t('Only allowlisted properties are recorded', [...props].every(p => ['artifact_name', 'artifact_version', 'product_id', 'cta_placement', 'environment', 'timestamp'].includes(p)), [...props].join(','));
  t('No answer appears in any event', !JSON.stringify(journal).match(/"(goal|platform|stage|owns|seo_symptom|conv_measurement)"/));
  t('Remote transmission is off', await page.evaluate(() => window.SBSPlannerAnalytics.remoteEnabled === false));
  await page.evaluate(() => { const d = Array.from(document.querySelectorAll('details.more')).find(x => /What this page measures/.test(x.textContent)); if (d) d.open = true; });
  await sleep(50);
  t('The page explains what it measures', /It is not analytics and it is not a visitor count/.test(await text(page)));

  const external = requests.filter(u => u !== FILE && !/\/favicon\.ico$/.test(u) && !u.startsWith('data:') && !u.startsWith('about:'));
  t('The page made no network request at all', external.length === 0, external.join(', '));

  /* ---------- 8. accessibility ---------- */
  console.log('\nKeyboard and structure\n');
  await page.goto(FILE, { waitUntil: 'networkidle0' });
  await clickButton(page, 'Build my free plan');
  const kb = await page.evaluate(async () => {
    const first = document.querySelector('input[name="goal"]');
    first.focus();
    return { focused: document.activeElement === first, tag: document.activeElement.tagName };
  });
  t('The first option takes focus', kb.focused && kb.tag === 'INPUT');
  await page.keyboard.press('ArrowDown');
  await sleep(50);
  t('Arrow keys move through the radio group', await page.evaluate(() => window.__planner.state.answers.goal === 'seo'));
  await page.keyboard.press('Tab');
  const outline = await page.evaluate(() => {
    const a = document.activeElement;
    const s = getComputedStyle(a);
    return { tag: a.tagName, outline: s.outlineStyle, width: s.outlineWidth };
  });
  t('Focus is visible on the next control', outline.outline !== 'none', JSON.stringify(outline));
  const struct = await page.evaluate(() => ({
    fieldsets: document.querySelectorAll('fieldset > legend').length,
    labelled: Array.from(document.querySelectorAll('input')).every(i => i.closest('label') !== null),
    h1: document.querySelectorAll('h1').length,
    live: document.querySelectorAll('[aria-live]').length,
  }));
  t('Every input sits inside a label', struct.labelled);
  t('Question groups use fieldset and legend', struct.fieldsets >= 1);
  t('There is exactly one h1 per screen', struct.h1 === 1, String(struct.h1));
  t('Progress is announced', struct.live >= 1);

  t('No console errors during the whole run', consoleErrors.length === 0, consoleErrors.join(' | '));

  await browser.close();
  server.close();
  console.log('\n' + pass + ' passed, ' + fail + ' failed\n');
  if (fail) { fails.forEach(f => console.log('  FAILED: ' + f)); process.exit(1); }
})().catch(e => { console.error(e); try { server.close(); } catch (x) {} process.exit(1); });
