/* Behavioural test for the copy buttons.
 *
 * The defect this exists to prevent: the button was appended inside the <pre>
 * and the handler read pre.textContent at click time, so every block anyone
 * copied ended with the word "Copy". Invisible until you paste.
 *
 * Headless Chrome denies clipboard-write regardless of overridePermissions, so
 * rather than asserting on the real clipboard this stubs
 * navigator.clipboard.writeText before the page scripts run and captures the
 * exact string handed to it. That tests the defect directly and deterministically.
 * The real-clipboard failure path is asserted separately, because a rejected
 * write must leave the user a usable instruction rather than a stuck button.
 *
 * Usage: node test-copy-buttons.js <guideUrl> <promptGuideUrl> [--preview <themeId>]
 */
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH ||
            '/home/ubuntu/.cache/chrome-manual/chrome-linux64/chrome';
const [url, promptUrl] = process.argv.slice(2).filter(a => !a.startsWith('--'));
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

const STUB = () => {
  window.__copied = [];
  const real = navigator.clipboard && navigator.clipboard.writeText;
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true,
    value: {
      writeText: t => { window.__copied.push(t); return Promise.resolve(); },
      readText: () => Promise.resolve(window.__copied[window.__copied.length - 1] || ''),
      __real: real,
    },
  });
};

(async () => {
  const browser = await puppeteer.launch({
    executablePath: EXE, args: ['--no-sandbox', '--disable-dev-shm-usage'] });

  async function openStubbed(target) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    const errors = [];
    page.on('console', m => { if (m.type() === 'error' && !NOISE.some(n => m.text().includes(n))) errors.push(m.text()); });
    page.on('pageerror', e => { if (!NOISE.some(n => String(e).includes(n))) errors.push(String(e)); });
    await page.evaluateOnNewDocument(STUB);
    if (preview) await page.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
    await page.goto(target, { waitUntil: 'networkidle2' });
    return { page, errors };
  }

  const { page, errors } = await openStubbed(url);

  const info = await page.evaluate(() => {
    const pres = [...document.querySelectorAll('.sbs-article__body pre')];
    return { total: pres.length, withBtn: pres.filter(p => p.querySelector('.sbs-copy')).length };
  });
  check('every code block got a button', info.total > 0 && info.withBtn === info.total,
        `${info.withBtn}/${info.total}`);

  // The whole point: what reaches the clipboard is the code, nothing appended.
  const expected = await page.evaluate(() => {
    const clone = document.querySelector('.sbs-article__body pre').cloneNode(true);
    const b = clone.querySelector('.sbs-copy');
    if (b) b.remove();
    return clone.textContent;
  });
  await page.click('.sbs-article__body pre .sbs-copy');
  await new Promise(r => setTimeout(r, 150));
  const got = await page.evaluate(() => window.__copied[0]);
  check('copied text is exactly the code block', got === expected,
        got === expected ? 'exact match'
          : `ends …${JSON.stringify(String(got).slice(-20))} vs …${JSON.stringify(expected.slice(-20))}`);
  check('copied text does not carry the button label',
        !/Cop(y|ied)$|Add to CLAUDE\.md$/.test(String(got).trim()));

  check('button confirms the copy',
        /Copied|copied/.test(await page.$eval('.sbs-article__body pre .sbs-copy', e => e.textContent)));
  check('confirmation is announced to assistive tech',
        (await page.$$eval('[role="status"][aria-live="polite"]', e => e.map(x => x.textContent).join(' ')))
          .toLowerCase().includes('copied'));
  check('CLAUDE.md blocks get their own label',
        (await page.$eval('.sbs-article__body pre[data-sbs-copy="claudemd"] .sbs-copy', e => e.textContent))
          .includes('CLAUDE.md'));
  check('buttons are real focusable buttons',
        await page.$eval('.sbs-article__body pre .sbs-copy',
          e => { e.focus(); return document.activeElement === e && e.tagName === 'BUTTON' && e.type === 'button'; }));
  check('every button has an accessible name',
        await page.$$eval('.sbs-copy', els => els.every(b =>
          (b.getAttribute('aria-label') || b.textContent || '').trim().length > 0)));
  check('no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await page.close();

  // A guide full of prompts must label them as prompts.
  const { page: p2, errors: e2 } = await openStubbed(promptUrl);
  const labels = await p2.$$eval('.sbs-article__body pre .sbs-copy',
    els => [...new Set(els.map(e => e.textContent))]);
  check('prompt blocks are labelled "Copy prompt"', labels.includes('Copy prompt'), labels.join(' | '));
  check('labels differ by block kind on a mixed page', labels.length > 1, labels.join(' | '));
  check('no console errors on the prompt guide', e2.length === 0, e2.slice(0, 2).join(' | '));
  await p2.close();

  /* The failure path. Browsers deny clipboard writes in plenty of real
     situations (permission policy, an insecure embed, a locked-down profile),
     and a button that silently does nothing is the worst outcome. Forced here
     by making writeText reject, rather than waiting for a browser to refuse —
     an assertion that depends on the environment denying permission passes for
     the wrong reason the day the environment stops denying it. */
  const p3 = await browser.newPage();
  await p3.evaluateOnNewDocument(() => {
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText: () => Promise.reject(new Error('denied')) },
    });
  });
  if (preview) await p3.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  await p3.goto(url, { waitUntil: 'networkidle2' });
  await p3.click('.sbs-article__body pre .sbs-copy');
  await new Promise(r => setTimeout(r, 250));
  const denied = await p3.$eval('.sbs-article__body pre .sbs-copy', e => e.textContent);
  check('a rejected clipboard write leaves a usable instruction',
        /Ctrl\+C/.test(denied), JSON.stringify(denied));
  const spoken = await p3.$$eval('[role="status"][aria-live="polite"]',
    e => e.map(x => x.textContent).join(' '));
  check('the failure is announced too', /Control C|Ctrl/i.test(spoken), JSON.stringify(spoken.slice(0, 60)));
  await p3.close();

  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
