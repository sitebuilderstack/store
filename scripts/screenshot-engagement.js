/* Screenshots of the engagement pages at phone, tablet and desktop widths,
 * plus the four-state walkthrough of each lab (start, a wrong answer, the
 * right answer, the corrected version) at desktop width.
 *
 * Usage: node scripts/screenshot-engagement.js <outDir> [--preview <themeId>] [--origin URL]
 * Output: <outDir>/<page>-<width>.png and <outDir>/walkthrough-<lab>-<n>.png
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');
const EXE = process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium-browser';
const out = process.argv[2] || 'docs/engagement/screenshots';
const pIdx = process.argv.indexOf('--preview');
const preview = pIdx > -1 ? process.argv[pIdx + 1] : null;
const oIdx = process.argv.indexOf('--origin');
const ORIGIN = oIdx > -1 ? process.argv[oIdx + 1] : 'https://sitebuilderstack.com';
fs.mkdirSync(out, { recursive: true });

const PAGES = {
  'guide-module': '/blogs/guides/claude-code-technical-seo-audit#try-seo-audit-prompt',
  'labs-hub': '/pages/labs',
  'my-projects': '/pages/my-projects',
  'weekly-fix': '/pages/weekly-fix',
  'challenge-1': '/blogs/weekly-fix/does-your-contact-form-actually-deliver',
  'guide-maintenance': '/blogs/guides/claude-code-website-maintenance',
};
const LABS = ['launch-readiness', 'technical-seo', 'conversion-functionality', 'website-operations'];
const WIDTHS = [390, 820, 1280];

const hidePreviewBar = () => {
  const add = () => { const st = document.createElement('style'); st.textContent = '#PBarNextFrame, #preview-bar-iframe { display: none !important; }'; (document.head || document.documentElement).appendChild(st); };
  if (document.head) add(); else document.addEventListener('DOMContentLoaded', add);
};

(async () => {
  const browser = await puppeteer.launch({ executablePath: EXE, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const page = await browser.newPage();
  await page.evaluateOnNewDocument(hidePreviewBar);
  if (preview) await page.goto(`${ORIGIN}/?preview_theme_id=${preview}`, { waitUntil: 'networkidle2' });

  // seed a project so My Projects has something to show
  await page.goto(`${ORIGIN}/blogs/guides/claude-code-technical-seo-audit`, { waitUntil: 'networkidle2' });
  await page.waitForFunction(() => document.querySelector('[data-sbs-try].is-ready'), { timeout: 30000 });
  await page.type('#try-pages', '/services/physiotherapy\n/contact');
  await page.click('[data-sbs-try] button[type="submit"]');
  await page.waitForFunction(() => !document.querySelector('[data-try-result]').hidden);
  await page.$eval('[data-try-save]', (b) => b.scrollIntoView({ block: 'center' }));
  await page.click('[data-try-save]');
  await page.waitForFunction(() => document.querySelector('[data-try-save]').textContent === 'Saved');
  await page.evaluate(() => { window.SBSProjects.update(window.SBSProjects.active().id, { name: 'Harbourline Physio (example)', platform: 'wordpress', objective: 'More assessment bookings from the landing page' }); window.SBSProjects.addTask('Send a marked test through the contact form'); });

  for (const [name, p] of Object.entries(PAGES)) {
    for (const w of WIDTHS) {
      await page.setViewport({ width: w, height: 900, deviceScaleFactor: 1, isMobile: w < 800 });
      await page.goto(`${ORIGIN}${p}`, { waitUntil: 'networkidle2' });
      await page.waitForFunction(() => !document.querySelector('[data-sbs-try]') || document.querySelector('[data-sbs-try].is-ready'), { timeout: 30000 }).catch(() => {});
      await page.waitForFunction(() => !document.querySelector('[data-sbs-projects]') || document.querySelector('[data-sbs-projects].is-ready'), { timeout: 30000 }).catch(() => {});
      if (p.includes('#')) { await page.evaluate(() => { const el = document.querySelector(location.hash); if (el) el.scrollIntoView(); }); await new Promise((r) => setTimeout(r, 300)); }
      const file = path.join(out, `${name}-${w}.png`);
      await page.screenshot({ path: file, fullPage: !p.includes('#') });
      console.log('  ' + file);
    }
  }

  // lab walkthroughs at desktop width
  await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 1 });
  for (const lab of LABS) {
    await page.goto(`${ORIGIN}/pages/lab-${lab}`, { waitUntil: 'networkidle2' });
    await page.waitForFunction(() => document.querySelector('[data-lab-app]') && !document.querySelector('[data-lab-app]').hidden, { timeout: 30000 });
    const fixture = await page.$eval('[data-lab-fixture]', (s) => JSON.parse(s.textContent));
    // The walkthrough frames are the lab element only, not the whole page.
    const shot = async (n) => { const f = path.join(out, `walkthrough-${lab}-${n}.png`); const el = await page.$('[data-lab-app]'); await el.screenshot({ path: f }); console.log('  ' + f); };
    await shot(1);
    const s1 = fixture.steps[0];
    const wrong = s1.decision.options.find((o) => o.id !== s1.decision.correct).id;
    await page.$eval(`#lab-${s1.id}-${wrong}`, (el) => el.click());
    await page.$eval('[data-lab-app] .sbs-lab__actions button', (b) => b.click());
    await page.waitForFunction(() => document.querySelector('.sbs-lab__feedback.is-error'));
    await shot(2);
    await page.$eval(`#lab-${s1.id}-${s1.decision.correct}`, (el) => el.click());
    await page.$eval('[data-lab-app] .sbs-lab__actions button', (b) => b.click());
    await page.waitForFunction(() => document.querySelector('.sbs-lab__feedback.is-ok'));
    await shot(3);
    for (let i = 0; i < fixture.steps.length; i++) {
      await page.$eval('[data-lab-app] .sbs-lab__actions button:nth-of-type(2)', (b) => b.click());
      if (i + 1 < fixture.steps.length) {
        const s = fixture.steps[i + 1];
        await page.waitForSelector(`#lab-${s.id}-${s.decision.correct}`);
        await page.$eval(`#lab-${s.id}-${s.decision.correct}`, (el) => el.click());
        await page.$eval('[data-lab-app] .sbs-lab__actions button', (b) => b.click());
        await page.waitForFunction(() => document.querySelector('.sbs-lab__feedback.is-ok'));
      }
    }
    await page.waitForFunction(() => document.querySelector('.sbs-lab__end'));
    await shot(4);
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
