/* Core Web Vitals and page weight, measured on the live storefront.
 *
 * LCP and CLS come from PerformanceObserver in a real render. INP cannot be
 * measured without a real interaction, so it is not reported here rather than
 * being estimated — a fabricated INP is worse than an absent one.
 *
 * Usage: node audit-performance.js <url> [width]
 */
let puppeteer;
try { puppeteer = require('puppeteer-core'); }
catch (e) { puppeteer = require('puppeteer'); }

(async () => {
  const url = process.argv[2];
  const width = parseInt(process.argv[3] || '412', 10);
  const browser = await puppeteer.launch({
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width, height: 820, deviceScaleFactor: 2, isMobile: width < 600 });

  const bytes = { total: 0, byType: {} };
  page.on('response', async r => {
    try {
      const len = parseInt(r.headers()['content-length'] || '0', 10);
      const type = (r.headers()['content-type'] || 'other').split(';')[0];
      bytes.total += len;
      bytes.byType[type] = (bytes.byType[type] || 0) + len;
    } catch (e) { /* redirects and cached entries have no length */ }
  });

  await page.evaluateOnNewDocument(() => {
    window.__vitals = { lcp: 0, cls: 0, shifts: [] };
    new PerformanceObserver(l => {
      for (const e of l.getEntries()) window.__vitals.lcp = e.startTime;
    }).observe({ type: 'largest-contentful-paint', buffered: true });
    new PerformanceObserver(l => {
      for (const e of l.getEntries()) {
        if (e.hadRecentInput) continue;
        window.__vitals.cls += e.value;
        if (e.value > 0.001) window.__vitals.shifts.push(+e.value.toFixed(4));
      }
    }).observe({ type: 'layout-shift', buffered: true });
  });

  await page.goto(url, { waitUntil: 'networkidle2', timeout: 90000 });
  await page.evaluate(() => new Promise(r => setTimeout(r, 1500)));

  const out = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0] || {};
    const res = performance.getEntriesByType('resource');
    const lcpEl = document.querySelector('img[fetchpriority="high"], h1');
    return {
      lcp: Math.round(window.__vitals.lcp),
      cls: +window.__vitals.cls.toFixed(4),
      shifts: window.__vitals.shifts.slice(0, 5),
      ttfb: Math.round(nav.responseStart || 0),
      domContentLoaded: Math.round(nav.domContentLoadedEventEnd || 0),
      requests: res.length,
      scripts: res.filter(r => r.initiatorType === 'script').length,
      thirdParty: [...new Set(res.map(r => new URL(r.name).host)
        .filter(h => !/(^|\.)sitebuilderstack\.com$/.test(h)))],
      imagesLazy: document.querySelectorAll('img[loading="lazy"]').length,
      imagesTotal: document.querySelectorAll('img').length,
      imagesNoDims: [...document.querySelectorAll('img')]
        .filter(i => !i.getAttribute('width') || !i.getAttribute('height')).length,
      imagesNoAlt: [...document.querySelectorAll('img')]
        .filter(i => i.getAttribute('alt') === null).length,
      lcpCandidate: lcpEl ? lcpEl.tagName + ' ' + (lcpEl.getAttribute('src') || '').slice(-50) : null,
    };
  });

  out.transferBytes = bytes.total;
  out.byType = Object.fromEntries(Object.entries(bytes.byType)
    .sort((a, b) => b[1] - a[1]).slice(0, 6));
  out.verdict = {
    lcp: out.lcp <= 2500 ? 'good' : out.lcp <= 4000 ? 'needs improvement' : 'poor',
    cls: out.cls <= 0.1 ? 'good' : out.cls <= 0.25 ? 'needs improvement' : 'poor',
    inp: 'not measured — requires a real interaction',
  };
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})();
