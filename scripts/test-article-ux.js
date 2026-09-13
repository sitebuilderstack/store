/* Behavioural test for the guide reading experience.
 *
 * Three things shipped together and each can fail silently: a progress strip
 * that never moves, a sticky header that is declared sticky and is not, and a
 * free-tool CTA that renders on the wrong guide.
 *
 * The sticky assertion exists because the header carried `position: sticky`
 * from launch and never stuck once — Shopify wraps each section in a generated
 * element and a sticky element cannot travel outside its parent. Nothing
 * caught it because nothing scrolled the page and looked.
 *
 * Usage: node test-article-ux.js [--preview <themeId>]
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
const url = p => ORIGIN + p + (preview ? '?preview_theme_id=' + preview : '');

(async () => {
  const browser = await puppeteer.launch({ executablePath: EXE, headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const ctx = await browser.createBrowserContext();
  const errors = [];

  async function open(path, w = 1280) {
    const page = await ctx.newPage();
    page.on('console', m => {
      if (m.type() === 'error' && !NOISE.some(n => m.text().includes(n))) errors.push(m.text());
    });
    await page.setViewport({ width: w, height: 900 });
    await page.goto(url(path), { waitUntil: 'networkidle2', timeout: 60000 });
    return page;
  }
  const scrollTo = (page, frac) => page.evaluate(f => {
    window.scrollTo(0, Math.round(document.body.scrollHeight * f));
  }, frac).then(() => new Promise(r => setTimeout(r, 400)));

  // ---- reading progress -----------------------------------------------
  let page = await open('/blogs/guides/claude-code-hooks');

  const top = await page.evaluate(() => ({
    hidden: document.querySelector('[data-sbs-reading]').hidden,
    fill: parseFloat(document.querySelector('[data-sbs-reading-fill]').style.width) || 0,
    position: getComputedStyle(document.querySelector('[data-sbs-reading]')).position,
  }));
  check('progress: the strip is revealed by script', !top.hidden);
  check('progress: fixed, so it cannot shift layout', top.position === 'fixed', top.position);
  check('progress: starts near zero at the top of the page', top.fill < 40, top.fill + '%');

  await scrollTo(page, 0.5);
  const mid = await page.evaluate(() => ({
    fill: parseFloat(document.querySelector('[data-sbs-reading-fill]').style.width) || 0,
    section: document.querySelector('[data-sbs-reading-section]').textContent.trim(),
  }));
  check('progress: advances as the page scrolls', mid.fill > top.fill, `${top.fill}% -> ${mid.fill}%`);
  check('progress: names the section being read', mid.section.length > 0, mid.section);

  await scrollTo(page, 1);
  const end = await page.evaluate(() => ({
    fill: parseFloat(document.querySelector('[data-sbs-reading-fill]').style.width) || 0,
    section: document.querySelector('[data-sbs-reading-section]').textContent.trim(),
  }));
  check('progress: reaches the end of the prose', end.fill >= 99, end.fill + '%');
  check('progress: the section changed while scrolling', end.section !== mid.section,
        `${mid.section} -> ${end.section}`);

  // The strip must never announce itself: a screen reader navigates by heading
  // and would hear the section re-read on every scroll tick.
  check('progress: hidden from assistive technology',
        await page.$eval('[data-sbs-reading]', e => e.getAttribute('aria-hidden') === 'true'));

  // ---- sticky header ---------------------------------------------------
  await scrollTo(page, 0.5);
  const sticky = await page.evaluate(() => {
    const h = document.querySelector('.sbs-header').getBoundingClientRect();
    const r = document.querySelector('[data-sbs-reading]').getBoundingClientRect();
    return { headerTop: Math.round(h.top), headerBottom: Math.round(h.bottom),
             stripTop: Math.round(r.top) };
  });
  check('header: actually sticks when scrolled', sticky.headerTop >= -1, 'top=' + sticky.headerTop);
  check('header: the progress strip sits below it, not over it',
        sticky.stripTop >= sticky.headerBottom - 1,
        `strip=${sticky.stripTop} headerBottom=${sticky.headerBottom}`);
  await page.close();

  // ---- the free tool CTA ----------------------------------------------
  // Each guide must offer the tool matched to ITS subject, not a default one.
  const expect = [
    ['/blogs/guides/claude-code-hooks', '/pages/claude-md-generator'],
    ['/blogs/guides/claude-code-seo-website-optimization', '/pages/seo-audit-prompt-generator'],
    ['/blogs/guides/claude-code-website-audit', '/pages/launch-readiness-score'],
    ['/blogs/guides/shopify-admin-api-claude-code', '/pages/website-prompt-builder'],
  ];
  for (const [path, tool] of expect) {
    const pg = await open(path);
    const got = await pg.evaluate(() => {
      const a = document.querySelector('.sbs-article__tool a');
      const el = document.querySelector('.sbs-article__tool');
      return a ? { href: new URL(a.href).pathname, painted: el.getBoundingClientRect().height > 0,
                   beforeProduct: !!(document.querySelector('.sbs-article__cta') &&
                     el.compareDocumentPosition(document.querySelector('.sbs-article__cta')) &
                     Node.DOCUMENT_POSITION_FOLLOWING) } : null;
    });
    check(`tool CTA on ${path.split('/').pop()}`,
          !!got && got.href === tool && got.painted,
          got ? got.href : 'no tool block');
    if (got) {
      check(`tool CTA precedes the product CTA on ${path.split('/').pop()}`, got.beforeProduct);
    }
    await pg.close();
  }

  /* Without JavaScript the nav ships fully expanded — that is the fallback —
     and it is over 500px tall. Sticking that pins half the viewport over the
     page and swallows clicks meant for the content beneath. This shipped once
     and was caught by an unrelated test clicking a label and landing on a nav
     link, so it is asserted here directly. */
  const noJs = await ctx.newPage();
  await noJs.setJavaScriptEnabled(false);
  await noJs.setViewport({ width: 1280, height: 900 });
  await noJs.goto(url('/blogs/guides/claude-code-hooks'), { waitUntil: 'networkidle2', timeout: 60000 });
  const fallback = await noJs.evaluate(() => {
    const wrap = [...document.querySelectorAll('.shopify-section-group-sbs-header-group')]
      .find(e => e.querySelector(':scope > .sbs-header'));
    const h = document.querySelector('.sbs-header');
    return { wrapPosition: wrap ? getComputedStyle(wrap).position : null,
             headerHeight: Math.round(h.getBoundingClientRect().height),
             enhanced: h.classList.contains('is-enhanced') };
  });
  check('no-JS: the header is not enhanced', !fallback.enhanced);
  check('no-JS: the tall fallback nav is NOT stuck over the page',
        fallback.wrapPosition !== 'sticky',
        `${fallback.wrapPosition}, header ${fallback.headerHeight}px`);
  const noJsStrip = await noJs.evaluate(() => {
    const r = document.querySelector('[data-sbs-reading]');
    return r ? r.getBoundingClientRect().height : 0;
  });
  check('no-JS: the progress strip is not painted', noJsStrip === 0, noJsStrip + 'px');
  await noJs.close();

  check('no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
