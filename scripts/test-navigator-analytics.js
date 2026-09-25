/* Tests for the SEO Audit Navigator's analytics subsystem
 * (artifacts/seo-audit-navigator/analytics/*.js) and recommendation data,
 * run in a sandbox with fake storage:
 *   - canonical names only; unknown names are dropped
 *   - props reduced to the allowlist (no typed text, no URL of the site)
 *   - artifact_opened / audit_started / audit_completed once per session
 *   - a refresh in the same tab is NOT a new session; a visit after the idle
 *     window IS, and marks the visitor returning
 *   - the upgrade link carries utm_*, artifact_ref and coarse segments only
 *   - the local provider journals when no store analytics exists; the
 *     shopify provider publishes when it does
 */
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const DIR = path.join(__dirname, '..', 'artifacts', 'seo-audit-navigator');
const read = (p) => fs.readFileSync(path.join(DIR, p), 'utf8');
let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d && !ok ? '  -> ' + String(d).slice(0, 300) : ''}`); };

function boot(opts) {
  opts = opts || {};
  const local = opts.local || {}; const session = opts.session || {};
  const published = [];
  const mk = (store, throws) => ({ getItem: (k) => { if (throws) throw new Error('blocked'); return Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null; }, setItem: (k, v) => { if (throws) throw new Error('blocked'); store[k] = String(v); }, removeItem: (k) => { delete store[k]; } });
  const win = { localStorage: mk(local, opts.blocked), sessionStorage: mk(session), location: { search: opts.search || '', hash: '' }, crypto: { getRandomValues: (a) => { for (let i = 0; i < a.length; i++) a[i] = Math.floor(Math.random() * 256); return a; } }, console, matchMedia: () => ({ matches: false }) };
  if (opts.shopify) win.Shopify = { analytics: { publish: (n, p) => published.push([n, p]) } };
  const sb = { window: win, document: { referrer: opts.referrer || '' }, URL, URLSearchParams, Date: opts.Date || Date, Math, JSON, Object, Array, String, Number, Boolean, RegExp, Error, Uint8Array, console };
  vm.createContext(sb);
  ['config.js', 'analytics/storage.js', 'analytics/events.js', 'analytics/session.js', 'analytics/attribution.js', 'analytics/analytics.js', 'data.js'].forEach((f) => vm.runInContext(read(f), sb));
  return { A: win.SBSAnalytics, S: win.SBSAnalyticsSession, ATTR: win.SBSAnalyticsAttribution, D: win.SBSNAV_DATA, local, session, published };
}

{
  const { A, S, local } = boot({ search: '?utm_source=newsletter&utm_campaign=sept&foo=bar', referrer: 'https://news.example/post' });
  check('first visit: visitor minted, visit_count 1, not returning', S.visitor().visit_count === 1 && S.isNewVisitor && !S.isReturning);
  check('unknown event name is dropped', A.track('audit_clicked', {}) === false && A.journal().length === 0);
  check('artifact_opened journals with allowlisted base props', A.track('artifact_opened', { referrer: 'news.example' }) === true && A.journal().length === 1 && A.journal()[0].p.utm_source === 'newsletter' && A.journal()[0].p.utm_campaign === 'sept');
  check('artifact_opened a second time in the same session is dropped', A.track('artifact_opened', {}) === false && A.journal().length === 1);
  const r = A.track('audit_completed', { audit_id: 'a_1', platform: 'shopify', primary_problem: 'not-indexed', symptom_count: 2, data_sources: ['gsc', 'sitemap'], critical_recommendations: 2, website: 'https://client.example', description: 'my store lost traffic', email: 'x@y.z' });
  const p = A.journal()[1].p;
  check('props reduced to the allowlist: no website, description or email; arrays joined', r && p.platform === 'shopify' && p.data_sources === 'gsc,sitemap' && !('website' in p) && !('description' in p) && !('email' in p), JSON.stringify(p));
  check('audit_completed for the same audit_id is sent once; a new audit_id is sent', A.track('audit_completed', { audit_id: 'a_1' }) === false && A.track('audit_completed', { audit_id: 'a_2' }) === true);
  check('repeatable events (upgrade clicks) are not deduplicated', A.track('upgrade_button_clicked', { cta_location: 'navigation' }) && A.track('upgrade_button_clicked', { cta_location: 'navigation' }));
  check('environment is claude_artifact with the local provider when no store analytics exists', A.environment === 'claude_artifact' && A.providers.join() === 'local');
}
{
  const b = boot({ search: '?utm_source=newsletter' });
  const url = new URL(b.ATTR.productUrl('audit_results', { platform: 'shopify', primary_problem: 'not-indexed', stage: 'audit_completed' }));
  const q = Object.fromEntries(url.searchParams.entries());
  check('upgrade link: real product URL with campaign params, artifact_ref and coarse segments', url.origin + url.pathname === 'https://sitebuilderstack.com/products/claude-code-seo-website-audit-toolkit' && q.utm_source === 'claude_artifact' && q.utm_medium === 'interactive_tool' && q.utm_campaign === 'sitebuilder_seo_audit_navigator' && q.utm_content === 'audit_results' && /^v_[a-f0-9]{24}$/.test(q.artifact_ref) && q.sbs_pf === 'shopify' && q.sbs_pp === 'not-indexed' && q.sbs_st === 'audit_completed', url.toString());
  check('upgrade link carries nothing else (no inbound utm, no text)', Object.keys(q).sort().join() === 'artifact_ref,sbs_pf,sbs_pp,sbs_st,utm_campaign,utm_content,utm_medium,utm_source');
  check('an unsafe cta location is not written into the URL', new URL(b.ATTR.productUrl('<script>', {})).searchParams.get('utm_content') === 'unknown');
  check('inbound attribution is kept for the visitor', b.ATTR.inbound().utm_source === 'newsletter');
}
{
  // same tab refresh: same session; after idle: new session and returning
  const local = {}, session = {};
  const b1 = boot({ local, session }); const sid = b1.S.session().session_id;
  const b2 = boot({ local, session });
  check('refresh in the same tab keeps the session and is not a return', b2.S.session().session_id === sid && !b2.S.isReturning && b2.S.visitor().visit_count === 1);
  const fakeNow = Date.now() + 45 * 60 * 1000;
  const FakeDate = class extends Date { constructor(...a) { super(...(a.length ? a : [fakeNow])); } static now() { return fakeNow; } };
  const b3 = boot({ local, session, Date: FakeDate });
  check('after 45 idle minutes: new session, visit_count 2, returning', b3.S.session().session_id !== sid && b3.S.isReturning && b3.S.visitor().visit_count === 2);
  check('days_since_previous_session is computed from the previous session end', typeof b3.S.daysSincePrevious() === 'number' && b3.S.daysSincePrevious() >= 0);
  const b4 = boot({ local, session: {}, Date: FakeDate });
  check('a new tab within the idle window is not a new session', b4.S.visitor().visit_count === 2 && !b4.S.isReturning);
}
{
  const b = boot({ shopify: true });
  b.A.track('artifact_opened', {});
  check('on sitebuilderstack.com the shopify provider publishes and the journal still records', b.published.length === 1 && b.published[0][0] === 'artifact_opened' && b.A.journal().length === 1 && b.A.environment === 'sitebuilderstack');
}
{
  const b = boot({ blocked: true });
  check('blocked storage: analytics still works in memory and reports storage unavailable', b.A.track('artifact_opened', {}) === true && b.A.storageAvailable() === false);
}
{
  const { D } = boot();
  const r = D.recommend({ problem: 'not-indexed', platform: 'shopify', symptoms: ['missing-urls', 'canonical'], data: ['sitemap'] });
  check('recommendation: indexation and technical are CRITICAL for missing pages + canonical symptom; GSC raised because it is missing', r[0].priority === 'CRITICAL' && r.filter((x) => x.priority === 'CRITICAL').map((x) => x.key).sort().join() === 'indexation,technical' && r.find((x) => x.key === 'gsc').priority === 'HIGH');
  const m = D.recommend({ problem: 'migration', platform: 'wordpress', symptoms: [], data: ['gsc'] });
  check('recommendation: a migration leads with launch validation and technical; GSC is not raised when present', m[0].key === 'launch' || m[0].key === 'technical', m.map((x) => x.key).join());
  check('every recommendation has the seven required parts', r.every((x) => x.priority && x.problem && x.why && x.investigate.length && x.evidence.length && x.module && x.next));
  check('four fictional samples, each labelled with a non-existent host and scored categories', D.SAMPLES.length === 4 && D.SAMPLES.every((s) => /\.example$/.test(s.host) && Object.keys(s.scores).length === 7 && s.findings.length >= 6));
  check('fourteen toolkit modules with description, problems and an example', D.MODULES.length === 14 && D.MODULES.every((x) => x.short && x.problems.length >= 3 && x.example));
}
console.log(`\n${failures} failure(s)`);
process.exit(failures ? 1 : 0);
