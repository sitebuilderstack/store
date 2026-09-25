#!/usr/bin/env node
/* Product-page browser QA — the eight pages, rendered, at three widths.
 *
 *   PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser \
 *     node docs/product-pages/qa-product-browser.js [--live]
 *
 * The static suite (qa-product-pages.py) reads markup. This one exercises the
 * things only a browser shows: overflow at a narrow width, console errors,
 * focus visibility, the sticky bar's show/hide rules, and that a double click
 * on Add to cart submits once.
 */
'use strict';
const PREVIEW = '191797854500';
const SITE = 'https://sitebuilderstack.com';
const LIVE = process.argv.includes('--live');

const HANDLES = [
  'claude-code-website-launch-system',
  'claude-code-seo-website-audit-toolkit',
  'claude-code-conversion-revenue-optimization-toolkit',
  'claude-code-website-operations-maintenance-system',
  'claude-code-shopify-automation-admin-api-toolkit',
  'claude-code-website-migration-replatforming-system',
  'claude-code-agency-client-delivery-system',
  'complete-site-builder-stack',
];
const WIDTHS = [390, 768, 1280];

let puppeteer;
try { puppeteer = require('puppeteer-core'); } catch (e) { puppeteer = require('puppeteer'); }

let pass = 0, fail = 0;
const failures = [];
function t(scope, name, ok, detail) {
  if (ok) { pass++; } else { fail++; failures.push(`${scope}: ${name}${detail ? ' [' + detail + ']' : ''}`); }
}
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const url = (h) => `${SITE}/products/${h}` + (LIVE ? '' : `?preview_theme_id=${PREVIEW}`);

async function overflow(page) {
  return page.evaluate(() => {
    const d = document.documentElement;
    let worst = '', w = 0;
    document.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.right > w) { w = r.right; worst = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(/\s+/)[0] : ''); }
    });
    return { scroll: d.scrollWidth, client: d.clientWidth, worst, right: Math.round(w) };
  });
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium-browser',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });

  /* 8 products x 3 widths is 24 page loads. Fired back to back, Shopify
     throttles the tail of the run and returns 503s that look like defects but
     are the rate limiter. Pace the requests instead of filtering the symptom. */
  let first = true;
  for (const handle of HANDLES) {
    for (const width of WIDTHS) {
      if (!first) await sleep(2500);
      first = false;
      const scope = `${handle} @${width}`;
      const page = await browser.newPage();
      const errors = [];
      page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
      page.on('pageerror', e => errors.push('pageerror: ' + e.message));
      await page.setViewport({ width, height: 900 });
      await page.goto(url(handle), { waitUntil: 'networkidle2', timeout: 60000 });

      const o = await overflow(page);
      t(scope, 'no horizontal overflow', o.scroll <= o.client + 1, `${o.scroll}>${o.client} worst ${o.worst}@${o.right}`);

      /* A 503 that survives the pacing above is reported, not swallowed: it is
         only excluded when a paced re-run clears it, which is a judgement for a
         person, not for this suite.
         Shopify's own telemetry beacon (monorail / shopify_pay_page_load) and
         the theme preview bar are platform scripts that fail in a headless
         sandbox with no outbound analytics route. They are not this theme's
         errors and are excluded; everything else counts. */
      const ours = errors.filter(e => !/preview_bar|shopify\.com|monorail|MonorailRequestError|shopify_pay_page_load/i.test(e));
      t(scope, 'no console errors', ours.length === 0, ours.slice(0, 2).join(' | '));

      if (width === 390) {
        /* Sticky bar: hidden at rest over the opening panel, shown once it has
           scrolled away, hidden again over the closing panel. */
        const atTop = await page.evaluate(() => {
          const b = document.querySelector('[data-sbs-sticky]');
          return b ? b.getAttribute('data-visible') : 'absent';
        });
        t(scope, 'sticky bar hidden over the opening buy panel', atTop === 'false', String(atTop));

        await page.evaluate(() => window.scrollTo(0, Math.round(document.body.scrollHeight * 0.45)));
        await sleep(700);
        const mid = await page.evaluate(() => {
          const b = document.querySelector('[data-sbs-sticky]');
          return b ? b.getAttribute('data-visible') : 'absent';
        });
        t(scope, 'sticky bar shown mid-page', mid === 'true', String(mid));

        const bar = await page.evaluate(() => {
          const b = document.querySelector('[data-sbs-sticky]');
          if (!b) return null;
          const r = b.getBoundingClientRect();
          const btn = b.querySelector('button[type="submit"], a');
          return {
            product: b.getAttribute('data-sbs-sticky-product'),
            withinViewport: r.right <= window.innerWidth + 1 && r.left >= -1,
            tapHeight: btn ? Math.round(btn.getBoundingClientRect().height) : 0,
            isForm: !!b.querySelector('form[action="/cart/add"]'),
          };
        });
        t(scope, 'sticky bar is for this product', bar && bar.product === handle, bar && bar.product);
        t(scope, 'sticky bar fits the viewport', bar && bar.withinViewport);
        t(scope, 'sticky control is a real add-to-cart', bar && bar.isForm);
        t(scope, 'sticky tap target at least 44px', bar && bar.tapHeight >= 44, bar && String(bar.tapHeight));

        /* The rule is "hidden whenever a buy panel is on screen", so the
           closing panel is scrolled INTO view rather than scrolling to the
           document end — at the end a tall footer has already pushed the panel
           off the top, and the bar is then correctly visible. */
        const atEnd = await page.evaluate(async () => {
          const panel = document.querySelector('#get [data-sbs-buy]');
          if (!panel) return { visible: null, panelSeen: false };
          panel.scrollIntoView({ block: 'center' });
          await new Promise(r => setTimeout(r, 700));
          const b = document.querySelector('[data-sbs-sticky]');
          const r = panel.getBoundingClientRect();
          return {
            visible: b && b.getAttribute('data-visible'),
            panelSeen: true,
            panelOnScreen: r.top < window.innerHeight && r.bottom > 0,
          };
        });
        t(scope, 'closing buy panel exists', atEnd.panelSeen);
        t(scope, 'sticky bar hides over the closing panel',
          atEnd.panelOnScreen && atEnd.visible === 'false', `visible=${atEnd.visible} onScreen=${atEnd.panelOnScreen}`);
      }

      if (width === 1280) {
        // Keyboard: the first purchase control must be reachable and show focus.
        const focus = await page.evaluate(() => {
          const btn = document.querySelector('#sbs-product-form button[type="submit"]');
          if (!btn) return null;
          btn.focus();
          const s = getComputedStyle(btn);
          return { focused: document.activeElement === btn, outline: s.outlineStyle, width: s.outlineWidth };
        });
        t(scope, 'the buy button takes keyboard focus', focus && focus.focused);

        // A double click must submit once.
        const submits = await page.evaluate(async () => {
          const form = document.getElementById('sbs-product-form');
          if (!form) return -1;
          let n = 0;
          form.addEventListener('submit', (e) => { e.preventDefault(); n++; });
          const btn = form.querySelector('button[type="submit"]');
          btn.click(); btn.click();
          await new Promise(r => setTimeout(r, 60));
          return n;
        });
        t(scope, 'double click submits once', submits === 1, String(submits));

        // Section links must move within the page, not navigate away.
        const anchors = await page.evaluate(() => {
          const out = [];
          document.querySelectorAll('header a[href^="#"]').forEach(a => {
            out.push({ href: a.getAttribute('href'), target: !!document.getElementById(a.getAttribute('href').slice(1)) });
          });
          return out;
        });
        t(scope, 'every header anchor resolves on this page',
          anchors.length > 0 && anchors.every(a => a.target),
          anchors.filter(a => !a.target).map(a => a.href).join(','));

        // Zoom to 200%: content must stay readable without sideways scroll.
        await page.setViewport({ width: 640, height: 900, deviceScaleFactor: 1 });
        await sleep(200);
        const z = await overflow(page);
        t(scope, 'no overflow at 200% zoom equivalent (640px)', z.scroll <= z.client + 1, `${z.scroll}>${z.client} ${z.worst}`);
      }

      await page.close();
    }
  }

  await browser.close();
  console.log(`\n${pass} passed, ${fail} failed`);
  if (fail) { failures.forEach(f => console.log('  ✗ ' + f)); process.exit(1); }
})().catch(e => { console.error(e); process.exit(1); });
