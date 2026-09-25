/* Tests for the engagement layer that can run without a browser:
 *   - the "Try this" generators (theme/dev/assets/sbs-engage.js): output is
 *     built from the inputs, blanks are marked rather than invented, unsafe
 *     URLs are dropped, filenames are useful
 *   - the analytics allowlist in sbs.js: engagement events carry only
 *     public identifiers and one-shot events are sent once
 *   - the snippet, the graph and the generators agree on module ids and
 *     next-step destinations
 * The browser journey (real clicks, clipboard, downloads, storage) is
 * scripts/test-engagement-browser.js.
 */
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const read = (p) => fs.readFileSync(path.join(ROOT, p), 'utf8');

let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d && !ok ? '  -> ' + String(d).slice(0, 300) : ''}`); };

// ---- generators -------------------------------------------------------------
function loadEngage() {
  const sandbox = { window: {}, document: { querySelectorAll: () => [] }, navigator: {}, console, Date, Array, String, RegExp, Math, JSON, Object };
  vm.createContext(sandbox);
  vm.runInContext(read('theme/dev/assets/sbs-engage.js'), sandbox);
  return sandbox.window.SBSEngage.GEN;
}
const fakeRoot = (values) => ({ querySelector: (sel) => { const m = /name="([^"]+)"/.exec(sel); return m && Object.prototype.hasOwnProperty.call(values, m[1]) ? { value: values[m[1]] } : null; } });
const GEN = loadEngage();
const graph = JSON.parse(read('content/content-graph.json'));

check('every module in the graph has a generator, and vice versa', Object.keys(graph.modules).sort().join() === Object.keys(GEN).sort().join(), Object.keys(GEN).join());

{
  const r = GEN['claude-md-section'](fakeRoot({ name: 'Northgate', commands: 'npm test\nnpm run build', prohibitions: 'never edit vendor/', done: '' }));
  check('claude-md: real commands appear as code, blank "done" is marked not invented', /`npm test`/.test(r.text) && /never edit vendor\//.test(r.text) && /_Not stated\./.test(r.text) && !/npm run lint/.test(r.text), r.text);
  check('claude-md: filename derived from the project name', r.file === 'CLAUDE-section-northgate.md', r.file);
  const e = GEN['claude-md-section'](fakeRoot({ name: '', commands: '', prohibitions: '', done: '' }));
  check('claude-md: all blank → every section says so rather than guessing', /_No commands given/.test(e.text) && /_No prohibitions given/.test(e.text));
}
{
  const r = GEN['seo-audit-prompt'](fakeRoot({ platform: 'Shopify', pages: '/products/a\n/collections/all', access: 'Public pages only' }));
  check('seo prompt: scoped to the listed pages, read-only rule present', /- \/products\/a/.test(r.text) && /Read-only\. Fetch pages and files; run no mutation/.test(r.text) && /not invented/.test(r.text));
  const e = GEN['seo-audit-prompt'](fakeRoot({ platform: '', pages: '', access: '' }));
  check('seo prompt: no pages → says so, no invented scope', /_No pages listed/.test(e.text));
}
{
  const t = GEN['shopify-next-workflow'](fakeRoot({ kind: 'theme', goal: 'size guide', risk: 'add to cart' }));
  check('shopify theme: observe → change on dev theme → verify names the risk → rollback', /## 1\. Observe/.test(t.text) && /development theme only/.test(t.text) && /confirm "add to cart" still works/.test(t.text) && /rollback/i.test(t.text));
  const c = GEN['shopify-next-workflow'](fakeRoot({ kind: 'catalogue', goal: '', risk: '' }));
  check('shopify catalogue: dry run and export-as-rollback, no theme steps', /Dry run first/.test(c.text) && /export from step 1 is the rollback/.test(c.text) && !/development theme only/.test(c.text));
  check('shopify: payments/domains kept manual', /Payments, tax, domains and app installs stay in the admin/.test(t.text));
}
{
  const r = GEN['landing-validation'](fakeRoot({ url: 'javascript:alert(1)', cta: 'Book now', destination: 'the booking form', devices: 'iPhone' }));
  check('landing: javascript: URL dropped, CTA and destination used, devices used', /_not stated/.test(r.text) && !/javascript:/.test(r.text) && /"Book now" lands on the booking form/.test(r.text) && /iPhone: CTA visible/.test(r.text));
  const ok = GEN['landing-validation'](fakeRoot({ url: 'https://staging.example/offer', cta: '', destination: '', devices: '' }));
  check('landing: https URL kept, blank CTA marked not stated', /Page: https:\/\/staging\.example\/offer/.test(ok.text) && /"not stated" → not stated/.test(ok.text));
}
{
  const r = GEN['maintenance-checklist'](fakeRoot({ name: 'Harbourline', platform: 'shopify', forms: 'Contact form\nQuote request' }));
  check('maintenance: each named form becomes a weekly check; hosted items marked (host); report template attached', /Form "Contact form"/.test(r.text) && /Form "Quote request"/.test(r.text) && /\(host\)/.test(r.text) && /# Maintenance report — Harbourline/.test(r.text) && /Backup: not "the job says success"/.test(r.text));
  const w = GEN['maintenance-checklist'](fakeRoot({ name: '', platform: 'wordpress', forms: '' }));
  check('maintenance: wordpress gets dependency updates not apps; no forms → prompt to add one', /Dependencies: platform, plugins/.test(w.text) && /_No forms listed/.test(w.text) && !/ \(host\)$/m.test(w.text));
}
{
  const r = GEN['migration-verification'](fakeRoot({ kind: 'domain', source: 'https://old.example', target: 'https://new.example', pages: '/about\nhttps://old.example/contact' }));
  check('migration: domain move adds DNS rows; paths are joined to the source; absolute rows kept', /MX, SPF, DKIM/.test(r.text) && /https:\/\/old\.example\/about,,KEEP,200,,/.test(r.text) && /https:\/\/old\.example\/contact,,KEEP,200,,/.test(r.text));
  const s = GEN['migration-verification'](fakeRoot({ kind: 'redesign', source: 'ftp://x', target: '', pages: '' }));
  check('migration: non-http source dropped; redesign has no DNS change; example row labelled as such', /Source: _not stated_/.test(s.text) && /DNS: no change planned/.test(s.text) && /example row — replace/.test(s.text));
}
{
  const r = GEN['regression-plan'](fakeRoot({ flows: 'Contact form submits\nCTA lands on booking', target: 'staging', tool: 'Playwright' }));
  check('regression: one numbered entry per flow with asserts/setup/out-of-scope; mocked-vs-real caveat; cannot-establish list', /1\. \*\*Contact form submits\*\*/.test(r.text) && /2\. \*\*CTA lands on booking\*\*/.test(r.text) && /mocked submission proves the page posts, not that anyone received it/.test(r.text) && /cannot establish/.test(r.text));
  const e = GEN['regression-plan'](fakeRoot({ flows: '', target: '', tool: '' }));
  check('regression: no flows → asks for them, no invented flows', /_No flows listed/.test(e.text) && !/1\. \*\*/.test(e.text));
}
for (const id of Object.keys(GEN)) {
  const r = GEN[id](fakeRoot({}));
  check(`generator ${id} runs on an empty form and returns a .md filename`, typeof r.text === 'string' && r.text.length > 200 && /\.md$/.test(r.file), r.file);
}

// ---- snippet / graph agreement ---------------------------------------------
{
  const snip = read('theme/dev/snippets/sbs-try.liquid');
  const pages = read('scripts/publish-pages.py');
  for (const [id, m] of Object.entries(graph.modules)) {
    const inCase = new RegExp(`when '${id}'`).test(snip);
    const url = m.next.kind === 'lab' ? `/pages/${graph.labs[m.next.id].handle}` : m.next.kind === 'page' ? `/pages/${m.next.id}` : m.next.kind === 'challenge' ? `/blogs/weekly-fix/${graph.challenges[m.next.id].handle}` : `/blogs/guides/${m.next.id}`;
    const block = snip.split(`when '${id}'`)[1] || '';
    const nextOk = new RegExp(`t_next_url = '${url.replace(/[/]/g, '\\/')}'`).test(block.split('{%- when')[0]);
    check(`snippet renders ${id} with next → ${url}`, inCase && nextOk);
  }
  const articles = Object.entries(graph.articles).filter(([, a]) => a.module);
  check('at least six existing guides carry a module', articles.length >= 6, articles.length);
  const manifest = JSON.parse(read('content/articles.json')).articles;
  for (const [h, a] of articles) {
    const entry = manifest.find((x) => x.handle === h);
    const html = entry ? read('content/articles/' + entry.file) : '';
    check(`${h}: body carries exactly one module slot`, (html.match(/data-sbs-try-slot/g) || []).length === 1);
  }
  check('sbs-article.liquid swaps the slot for the module', /replace: try_slot, try_html/.test(read('theme/dev/sections/sbs-article.liquid')) && /render 'sbs-try'/.test(read('theme/dev/sections/sbs-article.liquid')));
  check('landing layout registers the three lazy bundles', /id="sbs-assets"/.test(read('theme/dev/layout/landing.liquid')) && /sbs-engage\.js/.test(read('theme/dev/layout/landing.liquid')) && /sbs-labs\.js/.test(read('theme/dev/layout/landing.liquid')));
  check('publish-graph writes sbs.try from the module', /add\("try", a\["module"\]\)/.test(read('scripts/publish-graph.py')));
}

// ---- analytics allowlist in sbs.js ------------------------------------------
{
  const sent = [];
  const sandbox = {
    window: { Shopify: { analytics: { publish: (n, p) => sent.push([n, p]) } }, setTimeout, matchMedia: () => ({ matches: false, addEventListener() {} }) },
    document: { readyState: 'loading', addEventListener() {}, createElement: () => ({ setAttribute() {}, style: {} }), body: { appendChild() {} }, querySelector: () => null, querySelectorAll: () => [], getElementById: () => null },
    navigator: {}, console, Date, Array, String, RegExp, Math, JSON, Object, Promise, setTimeout, clearTimeout,
  };
  sandbox.window.document = sandbox.document;
  vm.createContext(sandbox);
  vm.runInContext(read('theme/dev/assets/sbs.js'), sandbox);
  const T = sandbox.window.SBS.track;
  T('artifact_saved', { module: 'seo-audit-prompt', guide: 'claude-code-technical-seo-audit', project: 'Northgate Physio', url: 'https://northgate.example', text: 'secret prompt', score: 3 });
  check('engagement event keeps only allowlisted id fields', sent.length === 1 && JSON.stringify(sent[0][1]) === '{"module":"seo-audit-prompt","guide":"claude-code-technical-seo-audit"}', JSON.stringify(sent));
  T('artifact_saved', { module: 'Not An Id!' });
  check('an id that is not [a-z0-9-] is dropped', JSON.stringify(sent[1][1]) === '{}');
  T('engagement_module_started', { module: 'x', guide: 'g' }); T('engagement_module_started', { module: 'x', guide: 'g' }); T('engagement_module_started', { module: 'y', guide: 'g' });
  check('one-shot events are deduplicated per subject', sent.filter((e) => e[0] === 'engagement_module_started').length === 2);
  T('artifact_copied', { module: 'x' }); T('artifact_copied', { module: 'x' });
  check('repeatable events (copy) are not deduplicated', sent.filter((e) => e[0] === 'artifact_copied').length === 2);
  T('tool_started', { label: 'legacy label' });
  check('non-engagement events pass through unchanged', sent[sent.length - 1][1].label === 'legacy label');
  const src = read('theme/dev/assets/sbs.js');
  const listed = /var ENGAGE_EVENTS = \{([\s\S]*?)\};/.exec(src)[1].match(/[a-z_]+(?=:)/g).sort();
  const spec = ('engagement_module_started artifact_generated artifact_copied artifact_exported artifact_saved lab_started lab_completed challenge_started challenge_completed project_created project_resumed related_product_clicked ' +
    /* monetization layer, docs/monetization/ */
    'monetization_offer_view monetization_cta_click monetization_lead_submitted affiliate_link_clicked').split(' ').sort();
  check('allowlist matches the documented event set exactly', listed.join() === spec.join(), listed.join());
}

// ---- lab scoring ------------------------------------------------------------
{
  const sandbox = { window: {}, document: { querySelectorAll: () => [] }, navigator: {}, console, Date, Array, String, RegExp, Math, JSON, Object };
  vm.createContext(sandbox);
  vm.runInContext(read('theme/dev/assets/sbs-labs.js'), sandbox);
  const score = sandbox.window.SBSLabs.score;
  const labs = fs.readdirSync(path.join(ROOT, 'content/labs')).filter((f) => f.endsWith('.json')).map((f) => JSON.parse(read('content/labs/' + f)));
  check('four labs are defined', labs.length === 4, labs.length);
  for (const lab of labs) {
    const right = {}; lab.steps.forEach((s) => { right[s.id] = [s.decision.correct]; });
    const r = score(lab, right);
    check(`${lab.id}: all correct first time → verified ${lab.steps.length}/${lab.steps.length}`, r.verified && r.first === lab.steps.length && r.solved === lab.steps.length);
    const wrong = {}; lab.steps.forEach((s) => { wrong[s.id] = [s.decision.options.find((o) => o.id !== s.decision.correct).id]; });
    const w = score(lab, wrong);
    check(`${lab.id}: a deliberately wrong answer on every step fails (not verified, 0 first-time)`, !w.verified && w.first === 0 && w.solved === 0, JSON.stringify(w));
    const retry = {}; lab.steps.forEach((s, i) => { const bad = s.decision.options.find((o) => o.id !== s.decision.correct).id; retry[s.id] = i === 0 ? [bad, s.decision.correct] : [s.decision.correct]; });
    const t = score(lab, retry);
    check(`${lab.id}: a retry resolves the step but the first attempt is what the score records`, t.verified && t.first === lab.steps.length - 1 && t.solved === lab.steps.length);
    check(`${lab.id}: an unanswered step is not verified`, !score(lab, {}).verified);
    // every wrong option has an explanation, so a wrong answer is never met with silence
    const silent = lab.steps.filter((s) => s.decision.options.some((o) => o.id !== s.decision.correct && !s.decision.explain.wrong[o.id]));
    check(`${lab.id}: every wrong option carries an explanation`, silent.length === 0, silent.map((s) => s.id).join());
    check(`${lab.id}: declares its sample data and links guide, module and product`, /fixture/i.test(lab.sample.note) && lab.guide.url && lab.module.url && lab.product.handle);
  }
  const fixtures = read('theme/dev/snippets/sbs-lab-fixtures.liquid');
  const blocks = fixtures.split('data-lab-fixture>').slice(1).map((b) => b.slice(0, b.indexOf('</script>')));
  check('generated fixtures snippet never closes the script element early', blocks.length === labs.length && blocks.every((b) => !/<\/script/.test(b) && JSON.parse(b).steps.length >= 3));
  check('fixtures snippet carries a static version with every answer for no-JS visitors', (fixtures.match(/Answer and explanation/g) || []).length === labs.reduce((n, l) => n + l.steps.length, 0));
}

console.log(`\n${failures} failure(s)`);
process.exit(failures ? 1 : 0);
