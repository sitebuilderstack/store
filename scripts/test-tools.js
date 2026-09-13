/* Behavioural test for the four free tools.
 *
 * The privacy assertion is the important one: a sentinel string is typed into
 * every text field, and then every analytics payload the page published is
 * searched for it. Generated CLAUDE.md files and project descriptions must
 * never reach an analytics service, and the only way to know is to look.
 *
 * Usage: node test-tools.js [--preview <themeId>]
 */
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH ||
            '/home/ubuntu/.cache/chrome-manual/chrome-linux64/chrome';
const ORIGIN = 'https://sitebuilderstack.com';
const pIdx = process.argv.indexOf('--preview');
const preview = pIdx > -1 ? process.argv[pIdx + 1] : null;
const NOISE = ["Framing 'https://shop.app/' violates", 'Error producing monorail event'];
const SENTINEL = 'ZZSECRETPROJECTZZ';

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

/* Capture analytics and stub the clipboard before any page script runs. */
const INSTRUMENT = () => {
  window.__events = [];
  const install = () => {
    window.Shopify = window.Shopify || {};
    window.Shopify.analytics = window.Shopify.analytics || {};
    window.Shopify.analytics.publish = (name, payload) => {
      window.__events.push({ name, payload: JSON.parse(JSON.stringify(payload || {})) });
    };
  };
  install();
  window.addEventListener('load', install);
  window.__copied = [];
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true,
    value: {
      writeText: t => { window.__copied.push(t); return Promise.resolve(); },
      readText: () => Promise.resolve(window.__copied[window.__copied.length - 1] || ''),
    },
  });
};

(async () => {
  const browser = await puppeteer.launch({
    executablePath: EXE, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const errors = [];

  async function open(path) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    page.on('console', m => { if (m.type() === 'error' && !NOISE.some(n => m.text().includes(n))) errors.push(m.text()); });
    page.on('pageerror', e => { if (!NOISE.some(n => String(e).includes(n))) errors.push(String(e)); });
    await page.evaluateOnNewDocument(INSTRUMENT);
    if (preview) await page.goto(`${ORIGIN}/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
    await page.goto(ORIGIN + path, { waitUntil: 'networkidle2' });
  await assertNotThrottled(page);
    return page;
  }
  const out = p => p.$eval('[data-sbs-tool-output]', e => e.textContent);
  async function submit(page) {
    const b = await page.$('[data-sbs-tool-generate]');
    await b.evaluate(e => e.scrollIntoView({ block: 'center' }));
    await b.click();
    await new Promise(r => setTimeout(r, 250));
  }

  // ---- shared structure across all four -----------------------------------
  const paths = {
    claudemd: '/pages/claude-md-generator',
    'seo-prompt': '/pages/seo-audit-prompt-generator',
    readiness: '/pages/launch-readiness-score',
    'prompt-builder': '/pages/website-prompt-builder',
  };
  for (const [tool, path] of Object.entries(paths)) {
    const page = await open(path);
    check(`${tool}: form revealed by JS`,
          await page.$eval('[data-sbs-tool]', e => !e.hidden));
    check(`${tool}: every control has a label`,
          await page.$$eval('input:not([type=hidden]), select, textarea', els => els.every(c => {
            if (c.closest('label')) return true;
            const l = c.id && document.querySelector(`label[for="${CSS.escape(c.id)}"]`);
            return Boolean(l && l.textContent.trim());
          })));
    check(`${tool}: result hidden before generating`,
          await page.$eval('[data-sbs-tool-result]', e => e.hidden));
    await page.close();
  }

  // ---- tool 1: CLAUDE.md ---------------------------------------------------
  let page = await open(paths.claudemd);
  await page.type('#p-name', SENTINEL);
  await page.type('#p-build', 'npm run build');
  await page.type('#p-never', 'Never touch production');
  await submit(page);
  let text = await out(page);
  check('claudemd: generates a CLAUDE.md', text.startsWith('# CLAUDE.md'));
  check('claudemd: includes the commands given', text.includes('npm run build'));
  check('claudemd: omits commands left empty', !/Test: `\s*`/.test(text) && !text.includes('- Test:'));
  check('claudemd: includes the prohibition given', text.includes('Never touch production'));
  check('claudemd: always states the credential rule', text.includes('Never commit a credential'));

  const copyBtn = await page.$('[data-sbs-tool-copy]');
  await copyBtn.evaluate(e => e.scrollIntoView({ block: 'center' }));
  await copyBtn.click();
  await new Promise(r => setTimeout(r, 150));
  check('claudemd: copy puts the exact result on the clipboard',
        (await page.evaluate(() => window.__copied[0])) === text);

  // The privacy assertion.
  const ev = await page.evaluate(() => window.__events);
  const names = ev.map(e => e.name);
  check('claudemd: fires tool_started, tool_completed and tool_result_copied',
        ['tool_started', 'tool_completed', 'tool_result_copied'].every(n => names.includes(n)),
        names.join(','));
  const serialised = JSON.stringify(ev);
  check('claudemd: nothing typed reaches analytics', !serialised.includes(SENTINEL),
        serialised.includes(SENTINEL) ? 'SENTINEL FOUND IN PAYLOAD' : 'clean');
  check('claudemd: no generated content reaches analytics',
        !serialised.includes('Never commit a credential'));

  const resetBtn = await page.$('[data-sbs-tool-reset]');
  await resetBtn.evaluate(e => e.scrollIntoView({ block: 'center' }));
  await resetBtn.click();
  await new Promise(r => setTimeout(r, 150));
  check('claudemd: reset hides the result', await page.$eval('[data-sbs-tool-result]', e => e.hidden));
  await page.close();

  // ---- tool 2: SEO audit prompt -------------------------------------------
  page = await open(paths['seo-prompt']);
  await page.select('#s-platform', 'Astro');
  await page.select('#s-gsc', 'Not set up');
  await submit(page);
  text = await out(page);
  check('seo-prompt: scoped to the chosen platform', text.includes('Astro'));
  check('seo-prompt: carries platform-specific behaviour',
        text.includes('site` is set in astro.config') || text.includes('astro.config'));
  check('seo-prompt: forbids ranking claims with no Search Console',
        text.includes('Do not claim anything about rankings'));
  check('seo-prompt: forbids fixing in the same run',
        text.includes('Do not fix anything in this run'));
  await page.select('#s-platform', 'Shopify');
  await submit(page);
  const shopText = await out(page);
  check('seo-prompt: changing platform changes the prompt',
        shopText.includes('sitemap.xml and it cannot be hand-edited') && shopText !== text);
  await page.close();

  // ---- tool 3: readiness score --------------------------------------------
  page = await open(paths.readiness);
  await submit(page);
  check('readiness: all "Not sure" scores zero', (await out(page)).includes('readiness: 0/100'));
  const setAll = (page, idx) => page.evaluate(i => {
    document.querySelectorAll('.sbs-tool__q').forEach(q => {
      const r = q.querySelectorAll('input[type=radio]')[i];
      if (r) { r.checked = true; }
    });
  }, idx);
  await setAll(page, 0);
  await submit(page);
  let scored = await out(page);
  check('readiness: all "Yes" scores 100', scored.includes('readiness: 100/100'), scored.split('\n')[0]);
  check('readiness: reports every category',
        ['SEO:', 'Performance:', 'Accessibility:', 'Security:', 'Conversion:'].every(c => scored.includes(c)));
  /* All "Yes" is the case that must recommend NOTHING. A tool that sells
     something whatever you answer is not deriving anything from the answers,
     and this is the direction that proves it. */
  const recPerfect = await page.$eval('[data-sbs-tool-rec]',
    e => ({ hidden: e.hidden,
            shown: [...e.querySelectorAll('[data-rec]')].filter(c => !c.hidden).length }));
  check('readiness: a perfect score recommends no product',
        recPerfect.hidden && recPerfect.shown === 0,
        `hidden=${recPerfect.hidden} shown=${recPerfect.shown}`);
  check('readiness: says plainly it is not an audit',
        scored.includes('self-assessment, not a technical audit'));
  await setAll(page, 2); // all "No"
  await submit(page);
  scored = await out(page);
  check('readiness: all "No" scores zero and lists every gap',
        scored.includes('readiness: 0/100') && (scored.match(/\n\d+\. \[/g) || []).length === 24,
        (scored.match(/\n\d+\. \[/g) || []).length + ' recommendations');
  /* Everything weak is a build-plus-search-plus-conversion problem, so the
     bundle is the honest answer here and a single product is not. */
  const recAllNo = await page.$eval('[data-sbs-tool-rec]',
    e => ({ hidden: e.hidden,
            shown: [...e.querySelectorAll('[data-rec]')].filter(c => !c.hidden)
                     .map(c => c.getAttribute('data-rec')) }));
  check('readiness: all weak recommends the bundle, and only it',
        !recAllNo.hidden && recAllNo.shown.length === 1 && recAllNo.shown[0] === 'stack',
        recAllNo.shown.join(',') || 'nothing shown');
  const scoreBlock = await page.$eval('[data-sbs-tool-score]',
    e => ({ hidden: e.hidden, painted: e.getBoundingClientRect().height > 0,
            big: (e.querySelector('.sbs-score strong') || {}).textContent,
            cats: e.querySelectorAll('.sbs-score__cats li').length }));
  check('readiness: renders a visible score block with all seven categories',
        !scoreBlock.hidden && scoreBlock.painted && scoreBlock.big === '0' && scoreBlock.cats === 7,
        `painted=${scoreBlock.painted} score=${scoreBlock.big} cats=${scoreBlock.cats}`);
  /* One weak category must select that category's product, not the bundle.
     Answers "Yes" everywhere except Conversion, whose index comes from the
     rendered legend rather than being hard-coded. */
  await page.evaluate(() => {
    const cats = [...document.querySelectorAll('.sbs-tool__cat')];
    const conv = cats.findIndex(c => /Conversion/.test(c.querySelector('legend').textContent));
    cats.forEach((cat, i) => {
      cat.querySelectorAll('.sbs-tool__q').forEach(q => {
        const r = q.querySelectorAll('input[type=radio]')[i === conv ? 2 : 0];
        if (r) { r.checked = true; }
      });
    });
  });
  await submit(page);
  const recCro = await page.$eval('[data-sbs-tool-rec]',
    e => [...e.querySelectorAll('[data-rec]')].filter(c => !c.hidden)
           .map(c => c.getAttribute('data-rec')));
  check('readiness: only Conversion weak recommends the conversion toolkit',
        recCro.length === 1 && recCro[0] === 'cro', recCro.join(',') || 'nothing shown');
  const recPrice = await page.$eval('[data-rec="cro"] a', a => a.textContent.trim());
  check('readiness: the recommendation carries a live price',
        /\$\d/.test(recPrice), recPrice);
  await page.close();

  // ---- tool 4: prompt builder ---------------------------------------------
  page = await open(paths['prompt-builder']);
  await page.type('#b-what', SENTINEL + ' scheduling app');
  await page.type('#b-features', 'Contact form\nRSS feed');
  await submit(page);
  text = await out(page);
  check('prompt-builder: includes the description given', text.includes(SENTINEL));
  check('prompt-builder: turns lines into separate requirements',
        text.includes('- Contact form') && text.includes('- RSS feed'));
  check('prompt-builder: always includes a no-change discovery phase',
        text.includes('do this first, and change nothing'));
  check('prompt-builder: a build task produces implementation deliverables',
        text.includes('## Implementation') && !text.includes('This task changes nothing'));

  /* The read-only guarantee is the assertion that matters. An audit prompt that
     permits editing is the failure this tool exists to prevent, so it is tested
     in both directions: build allows implementation, audit forbids it. */
  await page.select('#b-task', 'Audit it');
  await page.select('#b-stage', 'In production');
  await submit(page);
  const audit = await out(page);
  check('prompt-builder: an audit task forbids changing anything',
        audit.includes('This task changes nothing.') && audit.includes('No code changes'),
        audit.split('\n')[0]);
  check('prompt-builder: an audit task drops the implementation section',
        !audit.includes('## Implementation') && audit.includes('## Reporting'));
  check('prompt-builder: production stage states the risk',
        audit.includes('LIVE and real users depend on it'));
  await page.select('#b-task', 'Deploy it');
  await page.select('#b-stage', 'In production');
  await submit(page);
  const deploy = await out(page);
  check('prompt-builder: a deploy task in production demands a rollback',
        deploy.includes('blast radius and the rollback') && !deploy.includes('This task changes nothing'),
        deploy.split('\n')[0]);
  check('prompt-builder: always requires checks to be seen failing',
        text.includes('must be shown failing before I will trust it passing'));
  check('prompt-builder: always requires checks against the built output',
        text.includes('run against the built output, not the source'));
  const ev4 = JSON.stringify(await page.evaluate(() => window.__events));
  check('prompt-builder: nothing typed reaches analytics', !ev4.includes(SENTINEL));
  await page.close();

  check('no console errors across all four', errors.length === 0, errors.slice(0, 2).join(' | '));

  // ---- no JavaScript -------------------------------------------------------
  const noJs = await browser.newPage();
  await noJs.setJavaScriptEnabled(false);
  if (preview) await noJs.goto(`${ORIGIN}/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  await noJs.goto(ORIGIN + paths.claudemd, { waitUntil: 'networkidle2' });
  const off = await noJs.evaluate(() => ({
    form: document.querySelector('[data-sbs-tool]').getBoundingClientRect().height,
    prose: document.querySelector('.sbs-article__body').textContent.trim().length,
    links: document.querySelectorAll('.sbs-article__body a').length,
  }));
  check('no-JS: the form is not painted', off.form === 0, off.form + 'px');
  check('no-JS: the prose and its links remain', off.prose > 500 && off.links >= 2,
        `${off.prose} chars, ${off.links} links`);
  await noJs.close();

  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
