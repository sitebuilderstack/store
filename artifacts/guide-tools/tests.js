#!/usr/bin/env node
/* Shared checks for every guide tool.
 *
 *   PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser node tests.js
 *
 * Runs against each tool's preview.html — the published file inside the same
 * document shell the Artifact runtime wraps it in. Kept as a file rather than
 * a scratch harness, because there are four of these now.
 */
'use strict';
const http = require('http'), fs = require('fs'), path = require('path');
let puppeteer;
try { puppeteer = require('puppeteer-core'); } catch (e) { puppeteer = require('puppeteer'); }

const TOOLS = [
  { dir: 'seo-review', copy: 'Copy CSV', product: 'shopify-automation-admin-api-toolkit', campaign: 'seo_review_worksheet' },
  { dir: 'product-page', copy: 'Copy Markdown', product: 'conversion-revenue-optimization-toolkit', campaign: 'product_page_builder' },
  { dir: 'scope-builder', copy: 'Copy Markdown', product: 'agency-client-delivery-system', campaign: 'scope_builder' },
  { dir: 'aeo-checker', copy: 'Copy the report', product: 'claude-code-seo-website-audit-toolkit', campaign: 'aeo_checker' },
];
const WIDTHS = [390, 768, 1280];

let pass = 0, fail = 0;
const fails = [];
const t = (s, n, ok, d) => { ok ? pass++ : (fail++, fails.push(`${s}: ${n}${d ? ' [' + d + ']' : ''}`)); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium-browser',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });

  for (const tool of TOOLS) {
    const { dir, copy, product, campaign } = tool;
    const SRC = fs.readFileSync(path.join(__dirname, dir, 'index.html'), 'utf8');
    const PREVIEW = fs.readFileSync(path.join(__dirname, dir, 'preview.html'), 'utf8');

    /* ---- published source ---- */
    t(dir, 'no html/head/body wrapper', !/<\s*(html|head|body)[\s>]/i.test(SRC));
    t(dir, 'has a title in the first 8KB', /<title>[^<]+<\/title>/.test(SRC.slice(0, 8192)));
    t(dir, 'no external script, style or image', !/<(script|link|img)[^>]+(src|href)\s*=\s*["']https?:/i.test(SRC));
    const hrefs = [...new Set([...SRC.matchAll(/(?:href|src)="(https?:\/\/[^"]+)"/g)].map(m => m[1]))];
    const off = hrefs.filter(u => !/^https:\/\/sitebuilderstack\.com/.test(u));
    t(dir, 'every link points at sitebuilderstack', off.length === 0, off.join(','));
    const fict = [...new Set(SRC.match(/https?:\/\/(example-store\.myshopify|your-domain\.example)[^"'\s)]*/g) || [])];
    t(dir, 'fictional URLs appear as data, never as links', fict.every(u => !hrefs.includes(u)));
    t(dir, 'links its own product', SRC.includes(product));
    t(dir, 'campaign tag applied', (SRC.match(new RegExp('utm_campaign=' + campaign, 'g')) || []).length >= 3);
    t(dir, 'no credential-shaped string', !/shpat_|shpss_|BEGIN [A-Z ]*PRIVATE KEY/i.test(SRC));
    t(dir, 'under the 16MiB page limit', Buffer.byteLength(SRC) < 16 * 1024 * 1024);

    const server = http.createServer((q, r) => { r.writeHead(200, { 'Content-Type': 'text/html' }); r.end(PREVIEW); });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    const url = 'http://127.0.0.1:' + server.address().port + '/';

    for (const width of WIDTHS) {
      const page = await browser.newPage();
      const errs = [], reqs = [];
      page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
      page.on('pageerror', e => errs.push('pageerror: ' + e.message));
      page.on('request', r => reqs.push(r.url()));
      await page.setViewport({ width, height: 1000 });
      await page.goto(url, { waitUntil: 'networkidle0' });

      const o = await page.evaluate(() => {
        const d = document.documentElement;
        let worst = '', w = 0;
        document.querySelectorAll('*').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.right > w) { w = r.right; worst = el.tagName.toLowerCase() + '.' + (typeof el.className === 'string' ? el.className.split(/\s+/)[0] : ''); }
        });
        return { s: d.scrollWidth, c: d.clientWidth, worst, right: Math.round(w) };
      });
      t(`${dir} @${width}`, 'no horizontal overflow', o.s <= o.c + 1, `${o.s}>${o.c} ${o.worst}@${o.right}`);
      t(`${dir} @${width}`, 'no console errors', errs.length === 0, errs.slice(0, 1).join(''));
      t(`${dir} @${width}`, 'no network requests', reqs.filter(u => u !== url && !/favicon/.test(u)).length === 0);
      t(`${dir} @${width}`, 'exactly one h1', await page.$$eval('h1', e => e.length) === 1);

      if (width === 1280) {
        t(dir, 'opens in a working state', (await page.evaluate(() => document.body.innerText)).length > 1200);

        await page.evaluate(() => {
          window.__c = null;
          Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: t => { window.__c = t; return Promise.resolve(); } } });
        });
        const clicked = await page.evaluate(l => {
          const b = [...document.querySelectorAll('button')].find(x => x.textContent.trim() === l);
          if (!b) return false; b.click(); return true;
        }, copy);
        await sleep(140);
        const copied = await page.evaluate(() => window.__c);
        t(dir, 'copy control works', clicked && typeof copied === 'string' && copied.length > 200);
        t(dir, 'success shown only after success', (await page.$eval('#status', e => e.textContent)) === 'Copied.');

        await page.evaluate(() => {
          Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: () => Promise.reject(new Error('no')) } });
        });
        await page.evaluate(l => { [...document.querySelectorAll('button')].find(x => x.textContent.trim() === l).click(); }, copy);
        await sleep(160);
        t(dir, 'refused clipboard reports failure', /could not copy/i.test(await page.$eval('#status', e => e.textContent)));
        t(dir, 'refused clipboard offers selectable text', await page.$('#fallback textarea') !== null);
        t(dir, 'download hidden without the capability', await page.evaluate(() => { const b = document.getElementById('download'); return !b || b.hidden; }));
        t(dir, 'absent download is explained', await page.evaluate(() => { const n = document.getElementById('dl-note'); return n && !n.hidden; }));
        t(dir, 'first control takes keyboard focus', await page.evaluate(() => {
          const el = document.querySelector('textarea,input'); if (!el) return false; el.focus(); return document.activeElement === el;
        }));
        const resetLabel = dir === 'aeo-checker' ? 'Clear' : 'Start again';
        await page.evaluate(l => { const b = [...document.querySelectorAll('button')].find(x => x.textContent.trim() === l); if (b) b.click(); }, resetLabel);
        await sleep(140);
        t(dir, 'reset works', (await page.evaluate(() => document.body.innerText)).length > 200);
      }
      await page.close();
    }
    server.close();
  }

  await browser.close();
  console.log(`\n${pass} passed, ${fail} failed`);
  fails.forEach(f => console.log('  ✗ ' + f));
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
