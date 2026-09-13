/* Rendered accessibility audit for the Site Builder Stack landing layer.
 *
 * Walks the real rendered DOM and checks the things static analysis cannot:
 *   · computed contrast of every visible text node against its actual backdrop
 *   · heading order and h1 count
 *   · interactive elements with no accessible name
 *   · tap target size
 *   · focusable elements with no visible focus indicator
 *   · images without alt
 *   · horizontal overflow
 *
 * Usage: node audit-rendered-a11y.js <file.html | url> [width]
 */
// puppeteer-core is used with the Chrome for Testing binary already on this
// machine; fall back to the full puppeteer package if that is what is installed.
let puppeteer;
try { puppeteer = require('puppeteer-core'); }
catch (e) { puppeteer = require('puppeteer'); }

(async () => {
  const file = process.argv[2];
  const width = parseInt(process.argv[3] || '1280', 10);
  const browser = await puppeteer.launch({
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width, height: 1000 });
  const consoleErrors = [];
  page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('pageerror', e => consoleErrors.push('PAGEERROR ' + e.message));
  // Accept either a local file or a live URL, so the same audit can run
  // against a rendered storefront page and not just a preview render.
  const target = /^https?:\/\//.test(file) ? file : 'file://' + file;
  await page.goto(target, { waitUntil: 'networkidle0', timeout: 60000 });

  const report = await page.evaluate(() => {
    const parse = c => {
      const m = c.match(/rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?/);
      return m ? [+m[1], +m[2], +m[3], m[4] === undefined ? 1 : +m[4]] : null;
    };
    const lum = ([r, g, b]) => {
      const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
      return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
    };
    const ratio = (a, b) => {
      const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x);
      return (l1 + 0.05) / (l2 + 0.05);
    };
    const over = (fg, bg) => {
      const a = fg[3];
      return [0, 1, 2].map(i => Math.round(fg[i] * a + bg[i] * (1 - a)));
    };
    const effectiveBg = el => {
      let n = el;
      let acc = [11, 13, 18];
      const stack = [];
      while (n && n !== document.documentElement) {
        const c = parse(getComputedStyle(n).backgroundColor);
        if (c && c[3] > 0) stack.push(c);
        n = n.parentElement;
      }
      const bodyBg = parse(getComputedStyle(document.body).backgroundColor);
      if (bodyBg && bodyBg[3] > 0) stack.push(bodyBg);
      acc = stack.length ? stack[stack.length - 1].slice(0, 3) : acc;
      for (let i = stack.length - 2; i >= 0; i--) acc = over(stack[i], acc);
      return acc;
    };

    const visible = el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false;
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    };

    const out = { contrast: [], headings: [], names: [], targets: [], targetsExemptInline: [], focus: [], images: [], overflow: null };

    // ---- contrast on every element with a direct text node ----------------
    document.querySelectorAll('*').forEach(el => {
      const direct = Array.from(el.childNodes)
        .filter(n => n.nodeType === 3 && n.textContent.trim().length > 1);
      if (!direct.length || !visible(el)) return;
      const cs = getComputedStyle(el);
      const fg = parse(cs.color);
      if (!fg) return;
      const bg = effectiveBg(el);
      const composited = fg[3] < 1 ? over(fg, bg) : fg.slice(0, 3);
      const r = ratio(composited, bg);
      const size = parseFloat(cs.fontSize);
      const bold = parseInt(cs.fontWeight, 10) >= 700;
      const large = size >= 24 || (bold && size >= 18.66);
      const need = large ? 3 : 4.5;
      if (r < need) {
        out.contrast.push({
          sel: el.tagName + '.' + (el.className || '').toString().trim().split(/\s+/)[0],
          text: direct.map(n => n.textContent.trim()).join(' ').slice(0, 45),
          ratio: +r.toFixed(2), need, fontSize: +size.toFixed(1), bold,
        });
      }
    });

    // ---- headings ---------------------------------------------------------
    const hs = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6')).filter(visible);
    const h1s = hs.filter(h => h.tagName === 'H1');
    if (h1s.length !== 1) out.headings.push(`h1 count is ${h1s.length}, expected exactly 1`);
    let prev = 0;
    hs.forEach(h => {
      const lvl = +h.tagName[1];
      if (prev && lvl > prev + 1) {
        out.headings.push(`skipped level: h${prev} -> h${lvl} at "${h.textContent.trim().slice(0, 40)}"`);
      }
      prev = lvl;
    });

    // ---- accessible names on interactive elements -------------------------
    const accName = el => {
      // aria-label
      let n = (el.getAttribute('aria-label') || '').trim();
      if (n) return n;
      // aria-labelledby
      const lb = el.getAttribute('aria-labelledby');
      if (lb) {
        n = lb.split(/\s+/).map(id => (document.getElementById(id) || {}).textContent || '')
              .join(' ').trim();
        if (n) return n;
      }
      // associated <label for=""> or wrapping <label>
      if (el.id) {
        const lab = document.querySelector('label[for="' + CSS.escape(el.id) + '"]');
        if (lab && lab.textContent.trim()) return lab.textContent.trim();
      }
      const wrap = el.closest('label');
      if (wrap && wrap.textContent.trim()) return wrap.textContent.trim();
      // title, then visible text / value
      return (el.getAttribute('title') || el.textContent || el.value || '').trim();
    };

    // An element inside an aria-hidden subtree is not in the accessibility
    // tree at all, so "it has no accessible name" says nothing about it. The
    // guide cards wrap their thumbnail in exactly that: an aria-hidden,
    // tabindex="-1" duplicate of the heading link, so the image is clickable
    // without adding a second unlabelled stop to the tab order. Reporting
    // those buried the one real finding on the page.
    const hiddenFromA11y = el => !!el.closest('[aria-hidden="true"]');

    document.querySelectorAll('a,button,input,select,textarea,[role="button"]').forEach(el => {
      if (!visible(el)) return;
      if (el.type === 'hidden') return;
      if (hiddenFromA11y(el)) {
        if (el.tabIndex >= 0) {
          // Hidden from screen readers but still reachable by keyboard: that
          // combination IS a fault, and a real one.
          out.names.push('FOCUSABLE INSIDE aria-hidden: ' + el.tagName +
                         ' ' + (el.getAttribute('href') || ''));
        }
        return;
      }
      if (!accName(el)) out.names.push(el.tagName + '#' + (el.id || '') +
                                       '.' + (el.className || '').toString().split(' ')[0]);
    });

    // ---- tap targets (WCAG 2.2 2.5.8: 24x24 minimum) ----------------------
    // SC 2.5.8 exempts targets "in a sentence or its size is otherwise
    // constrained by the line-height of non-target text". An inline <a> inside
    // a paragraph is that case: its box is the font's content height whatever
    // the line-height, so reporting it produces noise that hides real findings.
    // The exception is applied only to genuinely inline elements that share
    // their parent with other text — a standalone link in an empty container
    // is still reported.
    const inlineExempt = el => {
      if (getComputedStyle(el).display !== 'inline') return false;
      const p = el.parentElement;
      if (!p) return false;
      const siblingText = Array.from(p.childNodes)
        .filter(n => n !== el)
        .map(n => n.textContent || '')
        .join('')
        .trim();
      return siblingText.length > 0;
    };
    document.querySelectorAll('a,button,input,select').forEach(el => {
      if (!visible(el)) return;
      const r = el.getBoundingClientRect();
      if (r.width < 24 || r.height < 24) {
        if (el.tagName === 'A' && inlineExempt(el)) {
          out.targetsExemptInline.push(`${el.tagName} ${Math.round(r.width)}x${Math.round(r.height)} "${(el.textContent||'').trim().slice(0,40)}"`);
          return;
        }
        out.targets.push(`${el.tagName}.${(el.className || '').toString().split(' ')[0]} ${Math.round(r.width)}x${Math.round(r.height)} "${(el.textContent||'').trim().slice(0,40)}"`);
      }
    });

    // ---- focus indicator --------------------------------------------------
    const focusables = Array.from(document.querySelectorAll('a[href],button,input,select,textarea,[tabindex]'))
      .filter(visible).slice(0, 40);
    focusables.forEach(el => {
      el.focus();
      const cs = getComputedStyle(el);
      const hasOutline = cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0;
      const hasShadow = cs.boxShadow && cs.boxShadow !== 'none';
      if (!hasOutline && !hasShadow) {
        out.focus.push(el.tagName + '.' + (el.className || '').toString().split(' ')[0]);
      }
      el.blur();
    });

    // ---- images -----------------------------------------------------------
    document.querySelectorAll('img').forEach(img => {
      if (img.getAttribute('alt') === null) out.images.push(img.src.slice(-50));
    });

    // ---- overflow ---------------------------------------------------------
    const de = document.documentElement;
    out.overflow = {
      scrollW: Math.max(de.scrollWidth, document.body.scrollWidth),
      clientW: de.clientWidth,
    };
    return out;
  });

  report.consoleErrors = consoleErrors;
  console.log(JSON.stringify(report, null, 2));
  await browser.close();
})();
