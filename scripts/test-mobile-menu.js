/* Behavioural test for the mobile navigation panel.
 *
 * Before this existed the header nav was `display: none` below 896px with no
 * alternative, so a phone had no navigation at all. The assertions that matter
 * most here are the ones about what happens when the script does NOT run: the
 * links must still be reachable, because hiding them behind a toggle that
 * cannot open is worse than the state it replaced.
 *
 * Usage: node test-mobile-menu.js <url> [--preview <themeId>]
 */
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH ||
            '/home/ubuntu/.cache/chrome-manual/chrome-linux64/chrome';
const url = process.argv[2];
const pIdx = process.argv.indexOf('--preview');
const preview = pIdx > -1 ? process.argv[pIdx + 1] : null;
const NOISE = ["Framing 'https://shop.app/' violates", 'Error producing monorail event',
               "Invalid 'X-Frame-Options' header"];
const MOBILE = { width: 390, height: 800 };
const DESKTOP = { width: 1280, height: 900 };

let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d ? '  -> ' + d : ''}`); };

async function assertNotThrottled(page) {
  const s = await page.evaluate(() => document.title + ' ' +
    (document.body ? document.body.textContent.slice(0, 200) : ''));
  if (/429|Too Many Requests|rate limit/i.test(s)) {
    console.log('  ABORT  the site is rate-limiting this client (HTTP 429).');
    process.exit(2);
  }
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: EXE, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const page = await browser.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport(MOBILE);
  const errors = [];
  const rec = t => { if (!NOISE.some(n => t.includes(n))) errors.push(t); };
  page.on('console', m => { if (m.type() === 'error') rec(m.text()); });
  page.on('pageerror', e => rec(String(e)));

  if (preview) await page.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  await page.goto(url, { waitUntil: 'networkidle2' });
  await assertNotThrottled(page);

  const B = '#sbs-burger';
  const N = '#sbs-primary-nav';
  const painted = sel => page.$eval(sel, e => e.getBoundingClientRect().height > 0);

  check('the burger is a real button', await page.$eval(B, e => e.tagName === 'BUTTON' && e.type === 'button'));
  check('the burger is shown on mobile', await painted(B));
  check('it has an accessible name',
        (await page.$eval(B, e => e.textContent.trim())).length > 0);
  check('aria-controls points at the nav',
        await page.evaluate((b, n) => document.getElementById(
          document.querySelector(b).getAttribute('aria-controls')) === document.querySelector(n), B, N));
  check('the panel starts closed',
        (await page.$eval(B, e => e.getAttribute('aria-expanded'))) === 'false' && !(await painted(N)));
  check('the header stays 64px tall when closed',
        (await page.$eval('.sbs-header__inner', e => Math.round(e.getBoundingClientRect().height))) === 64);

  await page.click(B);
  await new Promise(r => setTimeout(r, 180));
  check('tapping the burger opens the panel',
        (await page.$eval(B, e => e.getAttribute('aria-expanded'))) === 'true' && (await painted(N)));
  check('focus moves into the panel',
        await page.evaluate(n => document.querySelector(n).contains(document.activeElement), N));
  check('the page behind is locked from scrolling',
        await page.evaluate(() => document.documentElement.classList.contains('sbs-menu-open')));

  const links = await page.$$eval(N + ' a', els => els
    .filter(a => a.getBoundingClientRect().height > 0)
    .map(a => a.getAttribute('href')));
  check('every nav link is reachable in the panel', links.length >= 7, links.length + ' links');
  /* Read the catalogue rather than hard-coding a count. A literal here fails
     the day a product is added, which is the opposite of what it should do:
     the drift worth catching is a product the panel omits. */
  const catalogue = await browser.newPage();
  await catalogue.goto(new URL('/collections/all', url).href, { waitUntil: 'networkidle2' });
  const sold = await catalogue.$$eval('a[href^="/products/"]',
    els => [...new Set(els.map(a => a.getAttribute('href').split('?')[0]))]);
  await catalogue.close();

  const panelProducts = links.filter(h => h && h.startsWith('/products/'))
    .map(h => h.split('?')[0]);
  const absent = sold.filter(h => !panelProducts.includes(h));
  check('every product in the catalogue is in the panel',
        sold.length > 0 && absent.length === 0,
        `catalogue=${sold.length} panel=${panelProducts.length}` +
        (absent.length ? ` missing=${absent.join(' ')}` : ''));
  check('the products list is expanded, not a second disclosure',
        !(await painted('.sbs-nav__toggle')) && (await painted('.sbs-nav__grouplabel')));
  check('every panel link is keyboard reachable',
        await page.$$eval(N + ' a', els => els.filter(a => a.getBoundingClientRect().height > 0)
          .every(a => { a.focus(); return document.activeElement === a; })));

  // Escape closes and returns focus to the burger.
  await page.keyboard.press('Escape');
  await new Promise(r => setTimeout(r, 150));
  check('Escape closes the panel',
        (await page.$eval(B, e => e.getAttribute('aria-expanded'))) === 'false');
  check('Escape returns focus to the burger',
        await page.evaluate(b => document.activeElement === document.querySelector(b), B));
  check('scroll lock is released', 
        await page.evaluate(() => !document.documentElement.classList.contains('sbs-menu-open')));

  // Keyboard activation.
  await page.focus(B);
  await page.keyboard.press('Enter');
  await new Promise(r => setTimeout(r, 150));
  check('Enter opens it from the keyboard',
        (await page.$eval(B, e => e.getAttribute('aria-expanded'))) === 'true');

  // Following a link closes it, so it is not left open behind the next page.
  await page.evaluate(n => {
    document.addEventListener('click', e => { const a = e.target.closest('a'); if (a) e.preventDefault(); }, true);
    const a = document.querySelector(n + ' a'); a.click();
  }, N);
  await new Promise(r => setTimeout(r, 150));
  check('following a link closes the panel',
        (await page.$eval(B, e => e.getAttribute('aria-expanded'))) === 'false');

  /* Resizing across the breakpoint must leave a consistent state — the panel
     was hidden with an attribute, and that attribute must not survive into the
     desktop layout where the nav is the inline row. */
  await page.setViewport(DESKTOP);
  await new Promise(r => setTimeout(r, 250));
  check('desktop: the nav is visible again', await painted(N));
  check('desktop: the burger is gone', !(await painted(B)));
  check('desktop: the products disclosure is back',
        await painted('.sbs-nav__toggle') && !(await painted('.sbs-nav__grouplabel')));
  check('desktop: the products list is collapsed again', !(await painted('.sbs-nav__sub')));

  await page.setViewport(MOBILE);
  await new Promise(r => setTimeout(r, 250));
  check('back on mobile: the burger returns and the panel is closed',
        (await painted(B)) && !(await painted(N)));

  check('no console errors', errors.length === 0, errors.slice(0, 2).join(' | '));
  await page.close();

  /* The decisive one. With no JavaScript the burger must not be painted and
     every link must be reachable as a plain list. */
  const noJs = await browser.newPage();
  await noJs.setJavaScriptEnabled(false);
  await noJs.setViewport(MOBILE);
  if (preview) await noJs.goto(`https://sitebuilderstack.com/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });
  await noJs.goto(url, { waitUntil: 'networkidle2' });
  const off = await noJs.evaluate(() => ({
    burger: document.getElementById('sbs-burger').getBoundingClientRect().height,
    nav: document.getElementById('sbs-primary-nav').getBoundingClientRect().height,
    links: [...document.querySelectorAll('#sbs-primary-nav a')]
      .filter(a => a.getBoundingClientRect().height > 0).map(a => a.getAttribute('href')),
    overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  }));
  check('no-JS: the burger is not painted', off.burger === 0, off.burger + 'px');
  check('no-JS: every nav link is visible', off.links.length >= 7, off.links.length + ' links');
  const offProducts = off.links.filter(h => h && h.startsWith('/products/'))
    .map(h => h.split('?')[0]);
  check('no-JS: every product is visible',
        offProducts.length === sold.length && sold.length > 0,
        `${offProducts.length} of ${sold.length}`);
  check('no-JS: no horizontal overflow at 390px', !off.overflow);
  await noJs.close();

  await browser.close();
  console.log(`\n${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();
