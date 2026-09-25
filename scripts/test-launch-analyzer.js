/* Tests for artifacts/launch-readiness-analyzer: scoring, bands,
 * project-type scoping, weighting, risks, plan, prompts, product mapping,
 * analytics dedupe/allowlist and the attribution URL. */
const fs = require('fs'), vm = require('vm'), path = require('path');
const DIR = path.join(__dirname, '..', 'artifacts', 'launch-readiness-analyzer');
let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d && !ok ? '  -> ' + String(d).slice(0, 300) : ''}`); };
function boot(opts) {
  opts = opts || {}; const local = {}, session = {};
  const mk = (s) => ({ getItem: (k) => (k in s ? s[k] : null), setItem: (k, v) => { s[k] = String(v); }, removeItem: (k) => { delete s[k]; } });
  const win = { localStorage: mk(local), sessionStorage: mk(session), location: { search: opts.search || '' }, crypto: { getRandomValues: (a) => { for (let i = 0; i < a.length; i++) a[i] = (Math.random() * 256) | 0; return a; } } };
  const sb = { window: win, document: { referrer: '' }, URL, URLSearchParams, Date, Math, JSON, Object, Array, String, Number, Uint8Array, console };
  vm.createContext(sb);
  ['config.js', 'questions.js', 'engine.js', 'analytics.js'].forEach((f) => vm.runInContext(fs.readFileSync(path.join(DIR, f), 'utf8'), sb));
  return { Q: win.LRA_QUESTIONS, E: win.LRA_ENGINE, A: win.LRA_ANALYTICS, C: win.LRA_CONFIG };
}
const { Q, E, A, C } = boot();
const all = (v, t) => { const a = {}; E.applicable(t).forEach((q) => { a[q.id] = v; }); return a; };
check('all yes scores 100 and Highly Prepared', E.score(all('yes', 'new'), 'new').overall === 100 && E.band(100) === 'Highly Prepared');
check('all no scores 0 and Major Launch Gaps', E.score(all('no', 'new'), 'new').overall === 0 && E.band(0) === 'Major Launch Gaps');
check('all partial ≈ 50; all not-sure ≈ 25', E.score(all('partial', 'new'), 'new').overall === 50 && E.score(all('notsure', 'new'), 'new').overall === 25);
check('unanswered counts as no', E.score({}, 'new').overall === 0);
check('bands: 39→Major, 40→Foundation, 60→Approaching, 75→Strong, 90→Highly', [E.band(39), E.band(40), E.band(60), E.band(75), E.band(90)].join('|') === 'Major Launch Gaps|Foundation In Progress|Approaching Launch Readiness|Strong Foundation|Highly Prepared');
{
  const yes = all('yes', 'new'); yes.https = 'no'; const y2 = all('yes', 'new'); y2.caching = 'no';
  check('a weighted item (HTTPS) costs more than a weight-1 item (caching)', E.score(yes, 'new').overall < E.score(y2, 'new').overall);
}
check('landing page is not asked SaaS tenancy, backups or CI/CD; SaaS is', !E.applicable('landing').some((q) => ['saasdata', 'billing', 'backup', 'cicd'].includes(q.id)) && E.applicable('saas').some((q) => q.id === 'billing') && E.applicable('saas').some((q) => q.id === 'observability'));
check('shopify gets the checkout question; wordpress does not', E.applicable('shopify').some((q) => q.id === 'shopcheckout') && !E.applicable('wordpress').some((q) => q.id === 'shopcheckout'));
check('every category scores for every project type', Q.PROJECT_TYPES.every(([t]) => Object.values(E.score(all('yes', t), t).categories).every((c) => c.score === 100)));
{
  const a = all('yes', 'saas'); a.claudemd = 'no'; a.secrets = 'notsure'; a.rollback = 'no'; a.alt = 'partial';
  const sc = E.score(a, 'saas'); const risks = E.topRisks(a, 'saas', sc, 3);
  check('top risks: weighted gaps first, one per category', risks.length === 3 && risks.map((r) => r.q.id).sort().join() === 'claudemd,rollback,secrets' && new Set(risks.map((r) => r.q.cat)).size === 3, risks.map((r) => r.q.id).join());
  const plan = E.plan(a, 'saas', sc);
  check('plan: phases with no gaps become confirmations; phases with gaps list them', plan[2].confirm && plan[4].confirm && plan[0].items.some((i) => i.item.indexOf('CLAUDE.md') !== -1) && plan[3].items.length === 1, JSON.stringify(plan.map((p) => [p.title, p.items.length, !!p.confirm])));
  const pr = E.prompts(sc, 3);
  check('prompts come from the three weakest categories', pr.length === 3 && pr.map((p) => p.cat).sort().join() === 'claude,deployment,security', pr.map((p) => p.cat).join());
  const map = E.mapping(a, 'saas', sc);
  check('mapping: only relevant modules — claude config, deployment, security, SaaS platform; no SEO', map.some((m) => /Claude Code configuration/.test(m.title)) && map.some((m) => /deployment/.test(m.title)) && map.some((m) => /security/.test(m.title)) && map.some((m) => /SaaS/.test(m.title)) && !map.some((m) => /SEO gaps/.test(m.title)), map.map((m) => m.title).join(' | '));
}
{
  const a = all('yes', 'redesign'); a.keywords = 'no'; a.seoarch = 'no'; a.canonical = 'no'; a.gsc = 'no'; a.indexing = 'partial';
  const sc = E.score(a, 'redesign'); const map = E.mapping(a, 'redesign', sc);
  check('mapping: SEO + indexing + existing-site bonus for a redesign with SEO gaps', map.some((m) => /SEO gaps/.test(m.title)) && map.some((m) => /indexing/.test(m.title)) && map.some((m) => /existing site/.test(m.title)), map.map((m) => m.title).join(' | '));
  const many = all('partial', 'new'); const m2 = E.mapping(many, 'new', E.score(many, 'new'));
  check('mapping: many small gaps → prompt library', m2.some((m) => /smaller gaps/.test(m.title)));
}
check('every question has why/do/validate text', Q.QUESTIONS.every((q) => q.why && q.do && q.validate));
// analytics
check('unknown event dropped; artifact_opened once per session; step events repeat', A.track('nope', {}) === false && A.track('artifact_opened', {}) === true && A.track('artifact_opened', {}) === false && A.track('assessment_step_completed', { step: 'seo' }) && A.track('assessment_step_completed', { step: 'security' }));
const j = A.journal(); const last = j[j.length - 1].p;
check('props reduced to the allowlist (no answers, no free text)', A.track('assessment_completed', { project_type: 'saas', readiness_score_band: 'strong', lowest_category: 'seo', answers: { x: 1 }, notes: 'my repo' }) && !('answers' in A.journal().slice(-1)[0].p) && !('notes' in A.journal().slice(-1)[0].p) && A.journal().slice(-1)[0].p.project_type === 'saas');
const u = new URL(A.productUrl('final_cta')); const qs = Object.fromEntries(u.searchParams);
check('product URL: real product page + campaign params + artifact_ref, nothing else', u.origin + u.pathname === C.product.productUrl && qs.utm_source === 'claude_artifact' && qs.utm_medium === 'interactive_tool' && qs.utm_campaign === 'launch_readiness_analyzer' && qs.utm_content === 'final_cta' && /^v_[a-f0-9]{20}$/.test(qs.artifact_ref) && Object.keys(qs).length === 5, u.toString());
check('product facts: $19.99, 17 modules, 113 files, 100 prompts', C.product.price === 19.99 && C.product.features.some((f) => f[0] === '17 modules') && C.product.features.some((f) => f[0] === '113 files') && C.product.features.some((f) => f[0] === '100 reusable prompts'));
console.log(`\n${failures} failure(s)`); process.exit(failures ? 1 : 0);
