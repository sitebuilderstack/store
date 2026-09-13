/* Browser test for the product picker.
 *
 * The scoring table is covered exhaustively by test-picker-logic.js without a
 * browser. This asserts the parts only a browser can: that the form is
 * revealed, that answers reach the scorer, that exactly one card is shown with
 * a live price, and that the no-JS fallback is a usable list rather than
 * nothing.
 *
 * Usage: node test-picker.js [--preview <themeId>]
 */
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH ||
            '/home/ubuntu/.cache/chrome-manual/chrome-linux64/chrome';
const ORIGIN = 'https://sitebuilderstack.com';
const pIdx = process.argv.indexOf('--preview');
const preview = pIdx > -1 ? process.argv[pIdx + 1] : null;
const NOISE = ["Framing 'https://shop.app/' violates", 'Error producing monorail event'];
const PATH = '/pages/build-rank-convert';

let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d ? '  -> ' + d : ''}`); };
const url = () => ORIGIN + PATH + (preview ? '?preview_theme_id=' + preview : '');

/* Choose option `idx` for every question, then submit and read the result. */
async function answer(page, picks) {
  await page.evaluate((picks) => {
    document.querySelectorAll('.sbs-picker__q').forEach((q, i) => {
      const opts = q.querySelectorAll('input[type=radio]');
      const want = opts[picks[i]] || opts[0];
      want.checked = true;
    });
  }, picks);
  await page.click('[data-sbs-picker-form] button[type=submit]');
  await new Promise(r => setTimeout(r, 350));
  return page.evaluate(() => {
    const shown = [...document.querySelectorAll('[data-pick]')].filter(c => !c.hidden);
    const alt = document.querySelector('[data-sbs-picker-alt]');
    return {
      count: shown.length,
      key: shown[0] ? shown[0].getAttribute('data-pick') : null,
      title: shown[0] ? shown[0].querySelector('h4').textContent.trim() : null,
      price: shown[0] ? shown[0].querySelector('.sbs-picker__price').textContent.trim() : null,
      why: shown[0] ? shown[0].querySelector('[data-sbs-pick-why]').textContent.trim() : '',
      altShown: alt ? !alt.hidden : false,
    };
  });
}

(async () => {
  const browser = await puppeteer.launch({ executablePath: EXE, headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const ctx = await browser.createBrowserContext();
  const errors = [];
  const page = await ctx.newPage();
  page.on('console', m => {
    if (m.type() === 'error' && !NOISE.some(n => m.text().includes(n))) errors.push(m.text());
  });
  await page.setViewport({ width: 1280, height: 900 });
  await page.goto(url(), { waitUntil: 'networkidle2', timeout: 60000 });

  const shape = await page.evaluate(() => ({
    revealed: !document.querySelector('[data-sbs-picker]').hidden,
    fallbackHidden: document.querySelector('[data-sbs-picker-fallback]').hidden,
    questions: document.querySelectorAll('.sbs-picker__q').length,
    resultHidden: document.querySelector('[data-sbs-picker-result]').hidden,
    labelled: [...document.querySelectorAll('.sbs-picker__opt input')]
      .every(i => !!document.querySelector(`label[for="${i.id}"]`)),
    live: document.querySelector('[data-sbs-picker-result]').getAttribute('aria-live'),
  }));
  check('the form is revealed by script', shape.revealed);
  check('the no-JS list is hidden once the form works', shape.fallbackHidden);
  check('five questions render', shape.questions === 5, String(shape.questions));
  check('no result is shown before answering', shape.resultHidden);
  check('every option has a real label', shape.labelled);
  check('the result region announces politely', shape.live === 'polite', shape.live);

  // Option order per question: see page.build-rank-convert.json
  // Q1 stage, Q2 problem, Q3 role, Q4 lifecycle, Q5 outcome
  const build = await answer(page, [0, 0, 0, 1, 0]);
  check('not built + building problem -> Launch System',
        build.key === 'build' && build.count === 1, `${build.key} (${build.title})`);
  check('the recommendation carries a live price', /\$\d/.test(build.price || ''), build.price);
  check('the recommendation explains itself', build.why.length > 30);

  const rank = await answer(page, [2, 1, 3, 1, 1]);
  check('live site + ranking problem -> SEO toolkit',
        rank.key === 'rank' && rank.count === 1, `${rank.key} (${rank.title})`);

  /* The case the brief singles out. */
  const convert = await answer(page, [2, 2, 0, 1, 2]);
  check('live site + converting problem -> Conversion toolkit',
        convert.key === 'convert', `${convert.key} (${convert.title})`);
  check('converting problem never returns the Launch System', convert.key !== 'build');

  const operate = await answer(page, [4, 4, 0, 1, 4]);
  check('live + keeping it healthy -> Operations system',
        operate.key === 'operate' && operate.count === 1, `${operate.key} (${operate.title})`);

  const all = await answer(page, [3, 3, 2, 0, 3]);
  check('several sites + all of the above -> Complete Stack',
        all.key === 'all' && all.count === 1, `${all.key} (${all.title})`);

  check('exactly one card is ever visible',
        [build, rank, convert, operate, all].every(r => r.count === 1));

  await page.click('[data-sbs-picker-form] button[type=reset]');
  await new Promise(r => setTimeout(r, 250));
  check('reset hides the result',
        await page.$eval('[data-sbs-picker-result]', e => e.hidden));

  check('no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await page.close();

  // ---- without JavaScript --------------------------------------------------
  const noJs = await ctx.newPage();
  await noJs.setJavaScriptEnabled(false);
  await noJs.goto(url(), { waitUntil: 'networkidle2', timeout: 60000 });
  const fb = await noJs.evaluate(() => ({
    fallbackPainted: document.querySelector('[data-sbs-picker-fallback]').getBoundingClientRect().height > 0,
    products: document.querySelectorAll('[data-sbs-picker-fallback] li').length,
    formPainted: document.querySelector('[data-sbs-picker]').getBoundingClientRect().height > 0,
    stages: document.querySelectorAll('.sbs-life__stage').length,
  }));
  check('no-JS: the five products remain as a readable list',
        fb.fallbackPainted && fb.products === 5, `${fb.products} products`);
  check('no-JS: the unusable form is not painted', !fb.formPainted);
  check('no-JS: the lifecycle stages still render', fb.stages === 5, String(fb.stages));
  await noJs.close();

  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
