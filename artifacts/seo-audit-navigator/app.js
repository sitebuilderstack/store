/* app.js — SiteBuilder SEO Audit Navigator.
 * Routing (hash-based, no reload), state, views and the report generator.
 * Every analytics call goes through window.SBSAnalytics.track(). */
(function () {
  'use strict';
  var CFG = window.SBSNAV_CONFIG, D = window.SBSNAV_DATA, A = window.SBSAnalytics, EV = A.events;
  var SESSION = window.SBSAnalyticsSession, ATTR = window.SBSAnalyticsAttribution, S = window.SBSAnalyticsStorage;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function money(n) { return '$' + Number(n).toFixed(2); }

  /* ---- state ------------------------------------------------------------ */
  var STATE_KEY = 'sbsnav-state';
  var state = Object.assign({
    step: 0, problem: null, platform: null, symptoms: [], data: [], plan: null, auditStartedAt: null, auditId: null,
    sample: null, sampleRun: false, category: null, finding: null, breakTest: 'pass',
    planner: { platform: '', pages: '', problem: '', text: '' }, plannerResult: null, reportFormat: 'md', reportGenerated: false,
  }, S.get(STATE_KEY, {}));
  function save() { S.set(STATE_KEY, state); }
  function segments(stage) { return { platform: state.platform, primary_problem: state.problem, stage: stage || currentStage() }; }
  function currentStage() {
    var ses = SESSION.session();
    if (ses.report_status === 'downloaded') return 'report_downloaded';
    if (ses.audit_status === 'completed') return 'audit_completed';
    if (ses.audit_status === 'in-progress') return 'audit_started';
    return 'opened';
  }
  function upgradeUrl(loc) { return ATTR.productUrl(loc, segments()); }
  function trackUpgrade(loc) {
    SESSION.touch({ upgrade_status: 'clicked' });
    A.track(EV.UPGRADE_BUTTON_CLICKED, { audit_id: state.auditId, cta_location: loc, product_identifier: CFG.product.identifier, product_price: CFG.product.price, currency: CFG.product.currency, platform: state.platform, primary_problem: state.problem });
  }
  function ctaHtml(loc, label, cls) {
    return '<a class="btn ' + (cls || 'btn-accent') + '" href="' + esc(upgradeUrl(loc)) + '" target="_blank" rel="noopener" data-upgrade="' + esc(loc) + '">' + esc(label || ('Get ' + CFG.product.shortName + ' — ' + money(CFG.product.price))) + '</a>';
  }

  /* ---- capabilities (light up when available) --------------------------- */
  var caps = { downloads: null, sample: null, ready: false };
  function loadCaps() {
    if (!window.claude || typeof window.claude.use !== 'function') { caps.ready = true; renderCapsDependent(); return; }
    Promise.all([
      window.claude.use('downloads').catch(function () { return null; }),
      window.claude.use('sample').catch(function () { return null; }),
    ]).then(function (r) { caps.downloads = r[0]; caps.sample = r[1]; caps.ready = true; renderCapsDependent(); });
  }
  function renderCapsDependent() { if (route === 'report' || route === 'planner' || route === 'results') render(); }

  /* ---- routing ---------------------------------------------------------- */
  var ROUTES = ['start', 'sample', 'planner', 'toolkit', 'upgrade', 'results', 'report', 'finding', 'evidence', 'breaktest', 'help'];
  var route = 'start';
  function go(r, opts) {
    if (ROUTES.indexOf(r) === -1) r = 'start';
    route = r;
    if (location.hash !== '#' + r) history.replaceState(null, '', '#' + r);
    render();
    if (!(opts && opts.keepScroll)) window.scrollTo({ top: 0, behavior: 'auto' });
  }
  window.addEventListener('hashchange', function () { var r = location.hash.replace('#', ''); if (r !== route) go(r); });

  /* ---- views ------------------------------------------------------------ */
  var views = {};

  views.start = function () {
    var steps = ['Problem', 'Platform', 'Symptoms', 'Data', 'Plan'];
    var head = '<div class="stepper" aria-label="Audit steps">' + steps.map(function (s, i) { return '<span class="step' + (i === state.step ? ' is-current' : i < state.step ? ' is-done' : '') + '"><span class="step-n">' + (i + 1) + '</span>' + s + '</span>'; }).join('') + '</div>';
    var body = '';
    if (state.step === 0) {
      body = '<h1>What\'s happening with your website?</h1><p class="lede">Pick the one that describes it best. The plan is built from your answers, so an honest "not sure" beats a guess.</p>' +
        '<div class="cards" role="radiogroup" aria-label="Primary problem">' + D.PROBLEMS.map(function (p) { return '<button type="button" class="card-opt' + (state.problem === p.id ? ' is-on' : '') + '" role="radio" aria-checked="' + (state.problem === p.id) + '" data-problem="' + p.id + '"><strong>' + esc(p.label) + '</strong><span>' + esc(p.hint) + '</span></button>'; }).join('') + '</div>' +
        '<div class="actions"><button type="button" class="btn btn-primary" data-next ' + (state.problem ? '' : 'disabled') + '>Continue</button></div>';
    } else if (state.step === 1) {
      body = '<h1>What platform powers your website?</h1><p class="lede">Each platform breaks SEO in its own way; the plan includes the checks specific to yours.</p>' +
        '<div class="cards cards-3" role="radiogroup" aria-label="Platform">' + D.PLATFORMS.map(function (p) { return '<button type="button" class="card-opt' + (state.platform === p.id ? ' is-on' : '') + '" role="radio" aria-checked="' + (state.platform === p.id) + '" data-platform="' + p.id + '"><strong>' + esc(p.label) + '</strong></button>'; }).join('') + '</div>' +
        '<div class="actions"><button type="button" class="btn btn-ghost" data-back>Back</button><button type="button" class="btn btn-primary" data-next ' + (state.platform ? '' : 'disabled') + '>Continue</button></div>';
    } else if (state.step === 2) {
      body = '<h1>What symptoms are you seeing?</h1><p class="lede">Select everything that applies. Symptoms raise the priority of the areas that explain them.</p>' +
        '<div class="chips" role="group" aria-label="Symptoms">' + D.SYMPTOMS.map(function (s) { var on = state.symptoms.indexOf(s.id) !== -1; return '<button type="button" class="chip' + (on ? ' is-on' : '') + '" aria-pressed="' + on + '" data-symptom="' + s.id + '">' + esc(s.label) + '</button>'; }).join('') + '</div>' +
        '<div class="actions"><button type="button" class="btn btn-ghost" data-back>Back</button><button type="button" class="btn btn-primary" data-next>Continue</button></div>';
    } else if (state.step === 3) {
      body = '<h1>What SEO data do you currently have?</h1><p class="lede">The plan says what each area needs as evidence; this tells it what you can supply today.</p>' +
        '<div class="chips" role="group" aria-label="Data sources">' + D.DATA_SOURCES.map(function (s) { var on = state.data.indexOf(s.id) !== -1; return '<button type="button" class="chip' + (on ? ' is-on' : '') + '" aria-pressed="' + on + '" data-source="' + s.id + '">' + esc(s.label) + '</button>'; }).join('') + '</div>' +
        '<div class="actions"><button type="button" class="btn btn-ghost" data-back>Back</button><button type="button" class="btn btn-primary" data-finish>Build my audit plan</button></div>';
    } else {
      return views.results();
    }
    return head + body;
  };

  function prioCounts(list) { var c = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 }; list.forEach(function (r) { c[r.priority]++; }); return c; }

  views.results = function () {
    if (!state.plan) { state.step = 0; save(); return views.start(); }
    var c = prioCounts(state.plan);
    var plat = (D.PLATFORMS.filter(function (p) { return p.id === state.platform; })[0] || {}).label;
    var prob = (D.PROBLEMS.filter(function (p) { return p.id === state.problem; })[0] || {}).label;
    var html = '<div class="results-head"><div><p class="eyebrow">Your recommended SEO audit plan</p><h1>' + esc(prob) + '</h1><p class="lede">' + esc(plat) + ' · ' + state.symptoms.length + ' symptom' + (state.symptoms.length === 1 ? '' : 's') + ' · ' + state.data.length + ' data source' + (state.data.length === 1 ? '' : 's') + '. Ordered by what to investigate first. Nothing below is a finding about your site — it is where to look and what evidence to capture.</p></div>' +
      '<div class="prio-strip">' + ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(function (p) { return '<div class="prio-tile p-' + p.toLowerCase() + '"><span class="num">' + c[p] + '</span><span class="lab">' + p + '</span></div>'; }).join('') + '</div></div>' +
      '<div class="actions actions-top"><button type="button" class="btn btn-primary" data-go="report">Generate my SEO audit report</button><button type="button" class="btn btn-ghost" data-restart>Start over</button></div>' +
      '<ol class="recs">' + state.plan.map(function (r) {
        return '<li class="rec p-' + r.priority.toLowerCase() + '"><div class="rec-head"><span class="pill pill-' + r.priority.toLowerCase() + '">' + r.priority + '</span><h2>' + esc(r.module.name) + ' audit</h2><span class="mod-id">' + r.module.id + ' · toolkit area</span></div>' +
          '<dl class="rec-body"><dt>Why</dt><dd>' + esc(r.reason || r.problem) + '</dd><dt>Problem</dt><dd>' + esc(r.problem) + '</dd><dt>Why it matters</dt><dd>' + esc(r.why) + '</dd><dt>Investigate</dt><dd><ul>' + r.investigate.map(function (i) { return '<li>' + esc(i) + '</li>'; }).join('') + '</ul></dd><dt>Evidence required</dt><dd><ul>' + r.evidence.map(function (i) { return '<li>' + esc(i) + '</li>'; }).join('') + '</ul></dd><dt>Next action</dt><dd>' + esc(r.next) + '</dd></dl>' +
          '<p class="rec-foot">Toolkit area: <button type="button" class="link" data-toolkit="' + r.module.key + '">' + r.module.id + ' — ' + esc(r.module.name) + '</button></p></li>';
      }).join('') + '</ol>' +
      '<aside class="upsell"><p class="eyebrow">Going further</p><p>This plan tells you where to look. The complete toolkit gives you the audit workflow for each of these ' + state.plan.length + ' areas — the prompts, the evidence checklist and the report format — for every site you look after.</p>' + ctaHtml('audit_results', 'Unlock the complete ' + CFG.product.shortName) + '</aside>';
    return html;
  };

  views.sample = function () {
    var s = state.sample && D.SAMPLES.filter(function (x) { return x.id === state.sample; })[0];
    var html = '<p class="eyebrow">Sample audit</p><h1>See what an evidence-first audit finds</h1><p class="lede">Four fictional sites, each with faults planted the way they happen in practice. Pick one and run the audit.</p>' +
      '<div class="notice"><strong>Sample data — not a live website scan.</strong> These sites do not exist; nothing here was fetched from the internet. The findings show the <em>shape</em> of an audit result.</div>' +
      '<div class="cards cards-2" role="radiogroup" aria-label="Sample site">' + D.SAMPLES.map(function (x) { return '<button type="button" class="card-opt' + (state.sample === x.id ? ' is-on' : '') + '" role="radio" aria-checked="' + (state.sample === x.id) + '" data-sample="' + x.id + '"><strong>' + esc(x.name) + '</strong><span>' + esc(x.blurb) + '</span><span class="meta">' + esc(x.host) + ' · ' + x.pages + ' URLs · ' + esc((D.PLATFORMS.filter(function (p) { return p.id === x.platform; })[0] || {}).label) + '</span></button>'; }).join('') + '</div>' +
      '<div class="actions"><button type="button" class="btn btn-primary" data-run-sample ' + (s ? '' : 'disabled') + '>Run sample audit</button></div>' +
      '<div id="sample-progress" class="progress" hidden aria-live="polite"></div>' +
      (s && state.sampleRun ? dashboardHtml(s) : '');
    return html;
  };

  function scoreColor(v) { return v >= 80 ? 'good' : v >= 65 ? 'warn' : 'bad'; }
  function dashboardHtml(s) {
    var vals = D.CATS.map(function (c) { return s.scores[c[0]]; });
    var overall = Math.round(vals.reduce(function (a, b) { return a + b; }, 0) / vals.length);
    var counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 }; s.findings.forEach(function (f) { counts[f.priority]++; });
    var cat = state.category;
    var list = s.findings.filter(function (f) { return !cat || f.category === cat; });
    return '<section class="dash" aria-labelledby="dash-h"><div class="dash-head"><div><p class="eyebrow">SEO health · sample data, not a live scan</p><h2 id="dash-h">' + esc(s.name) + ' <span class="dim">' + esc(s.host) + '</span></h2></div><div class="overall ' + scoreColor(overall) + '"><span class="num">' + overall + '</span><span class="lab">/ 100 overall</span></div></div>' +
      '<div class="scores">' + D.CATS.map(function (c) { var v = s.scores[c[0]]; return '<button type="button" class="score' + (cat === c[0] ? ' is-on' : '') + '" data-category="' + c[0] + '" aria-pressed="' + (cat === c[0]) + '"><span class="lab">' + esc(c[1]) + '</span><span class="bar"><span class="fill ' + scoreColor(v) + '" style="width:' + v + '%"></span></span><span class="num">' + v + '</span></button>'; }).join('') + '</div>' +
      '<div class="prio-strip">' + ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(function (p) { return '<div class="prio-tile p-' + p.toLowerCase() + '"><span class="num">' + counts[p] + '</span><span class="lab">' + p + '</span></div>'; }).join('') + '</div>' +
      '<h3>' + (cat ? esc(D.CATS.filter(function (c) { return c[0] === cat; })[0][1]) + ' findings' : 'All findings') + (cat ? ' <button type="button" class="link" data-category="">show all</button>' : '') + '</h3>' +
      '<ul class="findings">' + list.map(function (f, i) { return '<li><button type="button" class="finding-row" data-finding="' + s.findings.indexOf(f) + '"><span class="pill pill-' + f.priority.toLowerCase() + '">' + f.priority + '</span><span class="f-title">' + esc(f.title) + '</span><span class="f-url">' + esc(f.url) + '</span></button></li>'; }).join('') + '</ul>' +
      '<aside class="upsell"><p class="eyebrow">What the toolkit adds</p><p>Each of these findings comes from one of the fourteen audit modules. The toolkit is the workflow that produces them on your own site: the checks in order, the evidence to capture for each, and the report they go into.</p>' + ctaHtml('audit_results', 'Unlock the complete ' + CFG.product.shortName) + '</aside></section>';
  }

  views.finding = function () {
    var s = D.SAMPLES.filter(function (x) { return x.id === state.sample; })[0];
    var f = s && s.findings[state.finding];
    if (!f) return views.sample();
    var m = D.MODULE_BY_KEY[f.module];
    return '<p class="eyebrow">Finding · sample data, not a live scan</p><div class="rec p-' + f.priority.toLowerCase() + '"><div class="rec-head"><span class="pill pill-' + f.priority.toLowerCase() + '">' + f.priority + '</span><h1>' + esc(f.title) + '</h1></div>' +
      '<dl class="rec-body"><dt>URL / file</dt><dd><code>' + esc(f.url) + '</code></dd><dt>Problem</dt><dd>' + esc(f.title) + '</dd><dt>Evidence</dt><dd><pre class="evidence">' + esc(f.evidence) + '</pre></dd><dt>Why this matters</dt><dd>' + esc(f.why) + '</dd><dt>Recommended investigation</dt><dd>' + esc(f.action) + '</dd><dt>Suggested next action</dt><dd>Record the evidence above in the report before changing anything. A fix made before the intended state is decided cannot be verified.</dd><dt>Toolkit module</dt><dd><button type="button" class="link" data-toolkit="' + m.key + '">' + m.id + ' — ' + esc(m.name) + '</button></dd></dl></div>' +
      '<p class="fine">The audit does not assume a fix is appropriate. Every finding names what to determine first.</p>' +
      '<div class="actions"><button type="button" class="btn btn-ghost" data-go="sample">Back to the dashboard</button></div>';
  };

  views.evidence = function () {
    return '<p class="eyebrow">Evidence-first</p><h1>Don\'t trust a green checkmark</h1><p class="lede">Two audits of the same page. One reassures. One can be re-checked next month.</p>' +
      '<div class="compare"><section class="cmp weak" aria-labelledby="weak-h"><h2 id="weak-h">Weak SEO audit</h2><ul class="ticks"><li>✓ Sitemap looks good</li><li>✓ Canonicals look good</li><li>✓ Site looks healthy</li></ul><p class="verdict bad">Evidence captured: <strong>NONE</strong></p><p>Three ticks, three opinions. If any of them is wrong, nothing here would show it.</p></section>' +
      '<section class="cmp strong" aria-labelledby="strong-h"><h2 id="strong-h">Evidence-based audit</h2><pre class="evidence">URL:         /blog/docker-production/\nHTTP status: 200\nCanonical:   https://example.com/blog/docker-production/\nRobots:      index,follow\nSitemap:     present\n\nResult:      PASS\nEvidence:    CAPTURED</pre><p>Five observed values. If the canonical changes, next month\'s capture will not match this one, and the difference is the finding.</p></section></div>' +
      '<p class="explain">A trustworthy audit provides the evidence behind every important finding rather than a green checkmark. The tick says "someone believed this"; the capture says "this is what the server returned, at this time". Only the second can be wrong in a way you can detect.</p>' +
      '<div class="actions"><button type="button" class="btn btn-primary" data-go="breaktest">Next: can the check detect a failure?</button></div>';
  };

  views.breaktest = function () {
    var broken = state.breakTest === 'fail';
    return '<p class="eyebrow">Break the test</p><h1>Can this SEO check detect a failure?</h1><p class="lede">A check you have never seen fail is not yet a check. Introduce the fault, watch the result change, restore it.</p>' +
      '<div class="bt ' + (broken ? 'is-fail' : 'is-pass') + '" aria-live="polite"><pre class="evidence">URL:        /products/example/\nIndexable:  ' + (broken ? 'NO   ← meta name="robots" content="noindex"' : 'YES') + '\nSitemap:    PRESENT\n\nResult:     ' + (broken ? 'FAIL' : 'PASS') + '</pre>' +
      (broken ? '<div class="conflict"><h2>Conflict detected</h2><p>A noindexed URL is being submitted through the sitemap. The sitemap asks the engine to index a page whose own head refuses — the check compares the two and fails on the contradiction.</p></div>' : '<p class="ok-note">Both signals agree: the URL asks to be indexed and the sitemap lists it.</p>') +
      '<div class="actions">' + (broken ? '<button type="button" class="btn btn-primary" data-break="pass">Restore test</button>' : '<button type="button" class="btn btn-primary" data-break="fail">Introduce SEO error</button>') + '</div></div>' +
      '<p class="explain">Deliberately verifying that a check detects a failure is what makes its passes worth anything. A green result has three possible causes — the condition held, the check looked at the wrong thing, or the check never ran — and they are indistinguishable until you have watched the same check go red on purpose. Every automated check in the toolkit is built to be broken this way first.</p>' +
      '<aside class="upsell"><p class="eyebrow">In the toolkit</p><p>Module 03 (Indexation) and 12 (Launch Validation) run this comparison across a whole sitemap, with the conflicting URLs listed as evidence.</p>' + ctaHtml('break_test', 'Get ' + CFG.product.shortName + ' — ' + money(CFG.product.price)) + '</aside>';
  };

  views.planner = function () {
    var p = state.planner;
    var r = state.plannerResult;
    return '<p class="eyebrow">Audit planner</p><h1>Build my SEO audit plan</h1><p class="lede">Describe the situation in your own words. The plan is a structured sequence — what to check, in what order, with what evidence — not a diagnosis.</p>' +
      '<form id="planner-form" class="form" novalidate><div class="grid-2"><div class="field"><label for="pl-platform">Website platform</label><select id="pl-platform" name="platform"><option value="">Choose…</option>' + D.PLATFORMS.map(function (x) { return '<option value="' + x.id + '"' + (p.platform === x.id ? ' selected' : '') + '>' + esc(x.label) + '</option>'; }).join('') + '</select></div>' +
      '<div class="field"><label for="pl-pages">Approximate number of pages</label><select id="pl-pages" name="pages"><option value="">Choose…</option>' + ['under 50', '50–500', '500–5,000', 'over 5,000'].map(function (x) { return '<option value="' + x + '"' + (p.pages === x ? ' selected' : '') + '>' + x + '</option>'; }).join('') + '</select></div></div>' +
      '<div class="field"><label for="pl-problem">Primary SEO problem</label><select id="pl-problem" name="problem"><option value="">Choose…</option>' + D.PROBLEMS.map(function (x) { return '<option value="' + x.id + '"' + (p.problem === x.id ? ' selected' : '') + '>' + esc(x.label) + '</option>'; }).join('') + '</select></div>' +
      '<div class="field"><label for="pl-text">Describe what\'s happening</label><textarea id="pl-text" name="text" rows="5" maxlength="1200" placeholder="My Shopify store contains approximately 500 products. Google has indexed only around 180 pages and organic traffic has declined during the last three months.">' + esc(p.text) + '</textarea><p class="hint">Stays in this page. Do not paste credentials, customer data or Search Console exports.</p></div>' +
      '<div class="actions"><button type="submit" class="btn btn-primary" data-plan-build>Build my audit plan</button>' + (caps.sample ? '<button type="button" class="btn btn-ghost" data-plan-ai>Ask Claude to refine it <span class="fine">(uses your Claude usage)</span></button>' : '') + '</div><p id="planner-status" class="status" role="status" hidden></p></form>' +
      (r ? plannerResultHtml(r) : '');
  };
  function plannerResultHtml(r) {
    return '<section class="plan-out" aria-labelledby="plan-h"><h2 id="plan-h">Your audit sequence' + (r.source === 'claude' ? ' <span class="pill pill-medium">refined by Claude</span>' : '') + '</h2><p class="lede">' + esc(r.summary) + '</p><ol class="seq">' + r.steps.map(function (s) { return '<li><div class="seq-head"><span class="pill pill-' + s.priority.toLowerCase() + '">' + s.priority + '</span><strong>' + esc(s.title) + '</strong><span class="mod-id">' + esc(s.module) + '</span></div><p>' + esc(s.what) + '</p><p class="ev"><span>Evidence:</span> ' + esc(s.evidence) + '</p></li>'; }).join('') + '</ol>' +
      (r.notes ? '<p class="fine">' + esc(r.notes) + '</p>' : '') +
      '<aside class="upsell"><p class="eyebrow">Run it</p><p>The plan names the modules; the toolkit is what runs inside each one.</p>' + ctaHtml('audit_planner', 'Get ' + CFG.product.shortName + ' — ' + money(CFG.product.price)) + '</aside></section>';
  }
  function deterministicPlan(p) {
    var recs = D.recommend({ problem: p.problem || 'unsure', platform: p.platform, symptoms: inferSymptoms(p.text), data: [] });
    var size = p.pages || 'unknown size';
    return {
      source: 'rules',
      summary: 'A ' + (recs.length) + '-step sequence for a ' + (D.PLATFORMS.filter(function (x) { return x.id === p.platform; })[0] || { label: 'site' }).label + ' site (' + size + '), starting with the areas your description points at. Each step names the evidence to capture before anything is changed.',
      steps: recs.slice(0, 8).map(function (r, i) { return { priority: r.priority, title: r.module.name, module: r.module.id + ' — ' + r.module.name, what: r.investigate.slice(0, 3).join('; ') + '.', evidence: r.evidence.slice(0, 2).join('; ') }; }),
      notes: 'Built from rules, not from your site: it reflects what you described, and nothing has been checked.',
    };
  }
  function inferSymptoms(text) {
    var t = (text || '').toLowerCase(), out = [];
    [['index', 'missing-urls'], ['traffic', 'traffic-decline'], ['rank', 'ranking-decline'], ['duplicate', 'dup-content'], ['canonical', 'canonical'], ['crawl', 'crawl'], ['broken', 'broken-links'], ['slow', 'slow'], ['vitals', 'cwv'], ['schema', 'schema'], ['structured', 'schema'], ['orphan', 'orphans'], ['link', 'poor-linking'], ['ctr', 'low-ctr'], ['migrat', 'migration'], ['sitemap', 'sitemap'], ['robots', 'robots']].forEach(function (p) { if (t.indexOf(p[0]) !== -1) out.push(p[1]); });
    return out;
  }
  function aiPlan(p) {
    var status = $('#planner-status'); status.hidden = false; status.textContent = 'Asking Claude… (you can keep using the page)';
    var prompt = 'You are an SEO auditor who insists on evidence. Build an audit SEQUENCE (not a diagnosis) for this situation. Platform: ' + (p.platform || 'unknown') + '. Size: ' + (p.pages || 'unknown') + '. Primary problem: ' + (p.problem || 'unknown') + '. Description: """' + (p.text || '').slice(0, 1200) + '""". Use ONLY these module names: ' + D.MODULES.map(function (m) { return m.id + ' ' + m.name; }).join('; ') + '. Return JSON: {"summary": string (<= 60 words), "steps": [{"priority": "CRITICAL"|"HIGH"|"MEDIUM"|"LOW", "title": string, "module": "NN — Name", "what": string (what to check, <= 40 words), "evidence": string (what to capture, <= 25 words)}] (4 to 8 steps), "notes": string}. Never claim anything was checked. Never invent numbers.';
    caps.sample.json(prompt, { modelTier: 'quick' }).then(function (j) {
      if (!j || !Array.isArray(j.steps) || !j.steps.length) throw new Error('shape');
      var ok = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
      state.plannerResult = { source: 'claude', summary: String(j.summary || '').slice(0, 600), steps: j.steps.slice(0, 8).map(function (s) { return { priority: ok.indexOf(s.priority) !== -1 ? s.priority : 'MEDIUM', title: String(s.title || '').slice(0, 120), module: String(s.module || '').slice(0, 60), what: String(s.what || '').slice(0, 400), evidence: String(s.evidence || '').slice(0, 300) }; }), notes: 'Refined by Claude from your description. It is a sequence to run, not a finding: nothing about your site has been checked.' };
      save(); render();
    }).catch(function (e) {
      var code = e && e.code;
      status.hidden = false;
      status.textContent = code === 'not_granted' || code === 'cancelled' ? 'Claude was not used. The rules-based plan below stands.' : code === 'rate_limited' ? 'Claude is busy; try again in a minute. The rules-based plan stands.' : 'Claude could not refine the plan; the rules-based plan stands.';
    });
  }

  views.toolkit = function () {
    return '<p class="eyebrow">Toolkit explorer</p><h1>Fourteen audit modules</h1><p class="lede">What each area covers, the problems it is for, and one example of the kind of thing it finds. The modules themselves — the workflows, prompts, checklists and report templates — are the product.</p>' +
      '<div class="modules">' + D.MODULES.map(function (m) { return '<article class="module" id="mod-' + m.key + '"><p class="mod-id">' + m.id + '</p><h2>' + esc(m.name) + '</h2><p>' + esc(m.short) + '</p><h3>Problems addressed</h3><ul>' + m.problems.map(function (p) { return '<li>' + esc(p) + '</li>'; }).join('') + '</ul><h3>Example</h3><p class="example">' + esc(m.example) + '</p></article>'; }).join('') + '</div>' +
      '<aside class="upsell"><p class="eyebrow">All fourteen</p><p>One purchase, every module, for every site you audit.</p>' + ctaHtml('toolkit_explorer') + '</aside>';
  };

  views.upgrade = function () {
    return '<div class="upgrade-hero"><p class="eyebrow">Ready to go deeper?</p><h1>' + esc(CFG.product.name) + '</h1><p class="price"><span class="amount">' + money(CFG.product.price) + '</span><span class="terms">One-time purchase · ' + CFG.product.currency + '</span></p>' +
      '<p class="lede">This navigator shows you where to look. The toolkit is what you run when you get there: the fourteen audit modules as Claude Code workflows, each in a read-only mode that changes nothing and produces findings with evidence, plus the report format they feed.</p>' +
      '<div class="grid-2 what"><section><h2>You get</h2><ul><li>All fourteen modules — Technical SEO through Reporting — as runnable Claude Code workflows</li><li>Evidence checklists per module: what to capture, from where, in what form</li><li>Checks built to be broken first, so a pass means something</li><li>Platform-specific passes for Shopify, WordPress, Astro, Next.js and static sites</li><li>The launch go/no-go pass and the redirect check for migrations</li><li>Report and baseline templates you can re-run next month</li><li>Use on every site you own or manage, including client work</li></ul></section>' +
      '<section><h2>This free navigator</h2><ul><li>A personalised plan: which areas, in what order, with what evidence</li><li>Four sample audits showing the shape of the findings</li><li>The evidence-first and break-the-test demonstrations</li><li>A downloadable report of your plan</li><li>No account, no email, nothing sent anywhere</li></ul></section></div>' +
      '<div class="actions">' + ctaHtml('upgrade_page') + '</div><p class="fine">The link opens the product page on sitebuilderstack.com. Payment is by Shopify checkout; the download is delivered after purchase. No results are promised or implied — this is a system for directing Claude Code through an audit; the work still has to be reviewed by you.</p></div>';
  };

  views.help = function () {
    var j = A.journal();
    var v = SESSION.visitor(), s = SESSION.session();
    return '<p class="eyebrow">Help / about</p><h1>How this navigator works</h1>' +
      '<div class="prose"><h2>What it is</h2><p>A free diagnostic from <a href="' + esc(CFG.site) + '" target="_blank" rel="noopener">Site Builder Stack</a>: answer four questions and get an ordered SEO audit plan with the evidence each area needs; run a sample audit on a fictional site; see why an audit without evidence is not worth much. It demonstrates the method behind the paid toolkit and is useful on its own.</p>' +
      '<h2>What it does not do</h2><p>It does not scan your website. Sample results are fictional and labelled as such. The plan it builds is where to look, not what was found. Nothing you type is transmitted.</p>' +
      '<h2>Privacy and analytics</h2><p>The navigator keeps an anonymous visitor id and a session id in your browser to count opens, audits, reports and upgrade clicks — nothing that identifies you, nothing you typed. ' +
      (A.environment === 'claude_artifact' ? 'Inside the Claude artifact sandbox no request can leave the page, so these events are kept only in your browser (below) and are never sent anywhere. When you click an upgrade link, the anonymous id and three coarse facts — platform, problem type, and whether you downloaded a report — travel in the link so the store can count how many visitors arrived from here.' : 'On sitebuilderstack.com they are sent to the store\'s own analytics (Shopify and Plausible) with no personal data.') + '</p>' +
      '<details><summary>Your visit, as this page recorded it (' + j.length + ' event' + (j.length === 1 ? '' : 's') + ')</summary><p class="fine">Visitor ' + esc(v.anonymous_visitor_id) + ' · session ' + esc(s.session_id) + ' · visit ' + v.visit_count + ' · storage ' + (A.storageAvailable() ? 'available' : 'unavailable (memory only)') + ' · providers: ' + esc(A.providers.join(', ')) + '</p><pre class="evidence small">' + esc(j.map(function (e) { return e.p.timestamp + '  ' + e.e + '  ' + Object.keys(e.p).filter(function (k) { return ['cta_location', 'primary_problem', 'platform', 'report_format', 'visit_count', 'audit_id'].indexOf(k) !== -1; }).map(function (k) { return k + '=' + e.p[k]; }).join(' '); }).join('\n') || '(none yet)') + '</pre><button type="button" class="btn btn-ghost" data-clear-journal>Clear this log</button></details>' +
      '<h2>Version</h2><p>' + esc(CFG.artifact.name) + ' ' + esc(CFG.artifact.version) + '. Built by Site Builder Stack. Site Builder Stack is an independent product and is not affiliated with, sponsored by, or endorsed by Anthropic.</p></div>';
  };

  /* ---- report ------------------------------------------------------------ */
  function reportData() {
    var plat = (D.PLATFORMS.filter(function (p) { return p.id === state.platform; })[0] || {}).label || 'Not stated';
    var prob = (D.PROBLEMS.filter(function (p) { return p.id === state.problem; })[0] || {}).label || 'Not stated';
    var sym = state.symptoms.map(function (s) { return D.SYMPTOMS.filter(function (x) { return x.id === s; })[0].label; });
    var data = state.data.map(function (s) { return D.DATA_SOURCES.filter(function (x) { return x.id === s; })[0].label; });
    var plan = state.plan || [];
    return { date: new Date().toISOString().slice(0, 10), platform: plat, problem: prob, symptoms: sym, data: data, plan: plan, critical: plan.filter(function (r) { return r.priority === 'CRITICAL'; }), high: plan.filter(function (r) { return r.priority === 'HIGH'; }), modules: plan.map(function (r) { return r.module; }) };
  }
  function reportMarkdown() {
    var r = reportData(), L = [];
    L.push('# SEO Audit Plan — ' + r.date, '', 'Generated by the SiteBuilder SEO Audit Navigator from the answers given. This is a plan of where to look and what evidence to capture; it is not a scan of the website and contains no findings about it.', '');
    L.push('## Executive summary', '', 'Primary problem: **' + r.problem + '** on a **' + r.platform + '** site. ' + r.plan.length + ' audit areas recommended: ' + r.critical.length + ' critical, ' + r.high.length + ' high priority. Start with the critical areas; capture the evidence each one lists before changing anything.', '');
    L.push('## Website platform', '', r.platform, '', '## Primary problem', '', r.problem, '', '## Symptoms', '', r.symptoms.length ? r.symptoms.map(function (s) { return '- ' + s; }).join('\n') : '- None reported', '', '## Available data', '', r.data.length ? r.data.map(function (s) { return '- ' + s; }).join('\n') : '- None yet', '');
    L.push('## Priority audit areas', '', '| Priority | Area | Toolkit module | Next action |', '|---|---|---|---|');
    r.plan.forEach(function (x) { L.push('| ' + x.priority + ' | ' + x.module.name + ' | ' + x.module.id + ' | ' + x.next + ' |'); });
    L.push('');
    function section(title, list) { L.push('## ' + title, ''); if (!list.length) { L.push('_None._', ''); return; } list.forEach(function (x) { L.push('### ' + x.priority + ' — ' + x.module.name + ' audit', '', '**Why:** ' + (x.reason || x.problem), '', '**Why it matters:** ' + x.why, '', '**Investigate:**', ''); x.investigate.forEach(function (i) { L.push('- ' + i); }); L.push('', '**Evidence required:**', ''); x.evidence.forEach(function (i) { L.push('- ' + i); }); L.push('', '**Next action:** ' + x.next, '', '**Toolkit module:** ' + x.module.id + ' — ' + x.module.name, ''); }); }
    section('Critical recommendations', r.critical); section('High-priority recommendations', r.high);
    L.push('## Recommended toolkit modules', '', r.modules.map(function (m) { return '- ' + m.id + ' — ' + m.name; }).join('\n'), '');
    L.push('## Next steps', '', '1. Work the critical areas first; capture the evidence listed before any change.', '2. Record each finding with its URL, the observed value and the time.', '3. Re-run the same checks after each change; a check that was never seen failing is not yet a check.', '4. The complete workflow for every module above: ' + CFG.product.name + ' — ' + ATTR.productUrl('report', segments()), '', '---', '', '_' + CFG.artifact.name + ' ' + CFG.artifact.version + ' · Nothing in this report was fetched from the website; it reflects the answers given._', '');
    return L.join('\n');
  }
  function reportHtml() {
    var md = reportMarkdown();
    // Minimal, safe Markdown → HTML for our own generated text (headings, lists, tables, bold, paragraphs).
    var lines = md.split('\n'), out = [], inList = false, inTable = false;
    function inline(s) { return esc(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/_(.+?)_/g, '<em>$1</em>').replace(/(https?:\/\/[^\s)]+)/g, '<a href="$1">$1</a>'); }
    lines.forEach(function (l) {
      if (/^\|/.test(l)) { if (!inTable) { out.push('<table>'); inTable = true; } if (/^\|\s*-/.test(l)) return; var cells = l.split('|').slice(1, -1).map(function (c) { return c.trim(); }); out.push('<tr>' + cells.map(function (c) { return '<td>' + inline(c) + '</td>'; }).join('') + '</tr>'); return; }
      if (inTable) { out.push('</table>'); inTable = false; }
      if (/^- /.test(l)) { if (!inList) { out.push('<ul>'); inList = true; } out.push('<li>' + inline(l.slice(2)) + '</li>'); return; }
      if (inList) { out.push('</ul>'); inList = false; }
      if (/^\d+\. /.test(l)) { out.push('<p>' + inline(l) + '</p>'); return; }
      var h = /^(#{1,3}) (.*)/.exec(l); if (h) { out.push('<h' + h[1].length + '>' + inline(h[2]) + '</h' + h[1].length + '>'); return; }
      if (l === '---') { out.push('<hr>'); return; }
      if (l.trim()) out.push('<p>' + inline(l) + '</p>');
    });
    if (inList) out.push('</ul>'); if (inTable) out.push('</table>');
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SEO Audit Plan — ' + reportData().date + '</title><style>body{font:16px/1.6 system-ui,sans-serif;max-width:52rem;margin:2rem auto;padding:0 1rem;color:#1a1d24}h1,h2,h3{line-height:1.25}table{border-collapse:collapse;width:100%;font-size:.9rem}td{border:1px solid #cbd0da;padding:.4rem .6rem;vertical-align:top}pre{white-space:pre-wrap}</style></head><body>' + out.join('\n') + '</body></html>';
  }

  views.report = function () {
    if (!state.plan) return '<h1>No audit yet</h1><p class="lede">Complete the audit first; the report is generated from its plan.</p><div class="actions"><button type="button" class="btn btn-primary" data-go="start">Start audit</button></div>';
    var r = reportData();
    var md = reportMarkdown();
    var canDownload = !!caps.downloads;
    return '<p class="eyebrow">Report</p><h1>Your SEO audit report</h1><p class="lede">' + r.problem + ' · ' + r.platform + ' · ' + r.plan.length + ' areas. Generated from your answers; it contains no findings about your site.</p>' +
      '<div class="report-actions"><fieldset class="fmt"><legend>Format</legend><label><input type="radio" name="fmt" value="md"' + (state.reportFormat === 'md' ? ' checked' : '') + '> Markdown (.md)</label><label><input type="radio" name="fmt" value="html"' + (state.reportFormat === 'html' ? ' checked' : '') + '> HTML (.html)</label></fieldset>' +
      (canDownload ? '<button type="button" class="btn btn-primary" data-download>Download report</button>' : (caps.ready ? '<button type="button" class="btn btn-primary" data-copy-report>Copy report text</button><p class="hint">Downloads are not available in this view; the report text can be copied instead.</p>' : '<button type="button" class="btn btn-primary" disabled>Checking download support…</button>')) +
      '<p id="report-status" class="status" role="status" hidden></p></div>' +
      '<pre class="report-preview" tabindex="0" aria-label="Report preview">' + esc(md) + '</pre>' +
      '<aside class="upsell"><p class="eyebrow">Next</p><p>The report names the modules. The toolkit runs them.</p>' + ctaHtml('report') + '</aside>';
  };

  function doDownload() {
    var fmt = state.reportFormat, status = $('#report-status');
    var name = 'seo-audit-plan-' + reportData().date + (fmt === 'html' ? '.html' : '.md');
    var data = fmt === 'html' ? reportHtml() : reportMarkdown();
    status.hidden = false; status.textContent = 'Preparing ' + name + '…';
    caps.downloads.save({ filename: name, data: data }).then(function () {
      status.textContent = 'Saved ' + name + '.';
      SESSION.touch({ report_status: 'downloaded' });
      A.track(EV.REPORT_DOWNLOADED, { audit_id: state.auditId, report_format: fmt === 'html' ? 'html' : 'markdown', platform: state.platform, primary_problem: state.problem });
      render();
    }).catch(function (e) {
      var code = e && e.code;
      status.textContent = code === 'declined' ? 'Download cancelled.' : code === 'rate_limited' ? 'A download prompt is already open; try again in a moment.' : 'The download could not be saved here. You can copy the text from the preview.';
    });
  }

  /* ---- shell + render ----------------------------------------------------- */
  var NAV = [['start', 'Start audit'], ['sample', 'Sample audit'], ['planner', 'Audit planner'], ['toolkit', 'Toolkit explorer'], ['upgrade', 'Upgrade']];
  function render() {
    var main = $('#view');
    var fn = views[route] || views.start;
    main.innerHTML = '<div class="view-inner">' + fn() + '</div>';
    $$('.nav a').forEach(function (a) { var on = a.getAttribute('data-route') === (route === 'results' || route === 'report' ? 'start' : route === 'finding' ? 'sample' : route); a.classList.toggle('is-on', on); if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    var dl = $('[data-nav-report]'); if (dl) dl.hidden = !state.plan;
    $('[data-nav-upgrade]').setAttribute('href', upgradeUrl('navigation'));
    $('[data-footer-upgrade]').setAttribute('href', upgradeUrl('footer'));
    var h1 = $('#view h1'); if (h1 && document.activeElement !== document.body) { h1.setAttribute('tabindex', '-1'); h1.focus({ preventScroll: true }); }
  }

  /* ---- events ------------------------------------------------------------- */
  document.addEventListener('click', function (ev) {
    var t = ev.target.closest('[data-route],[data-go],[data-problem],[data-platform],[data-symptom],[data-source],[data-next],[data-back],[data-finish],[data-restart],[data-sample],[data-run-sample],[data-category],[data-finding],[data-toolkit],[data-break],[data-upgrade],[data-download],[data-copy-report],[data-plan-ai],[data-clear-journal],[data-nav-restart]');
    if (!t) return;
    if (t.hasAttribute('data-route')) { ev.preventDefault(); go(t.getAttribute('data-route')); return; }
    if (t.hasAttribute('data-go')) { go(t.getAttribute('data-go')); return; }
    if (t.hasAttribute('data-upgrade')) { trackUpgrade(t.getAttribute('data-upgrade')); return; } // link proceeds
    if (t.hasAttribute('data-problem')) {
      var first = !state.auditId;
      state.problem = t.getAttribute('data-problem'); if (first) { state.auditId = SESSION.newAuditId(); state.auditStartedAt = Date.now(); }
      SESSION.touch({ primary_problem: state.problem });
      save(); render();
      if (first) A.track(EV.AUDIT_STARTED, { audit_id: state.auditId, primary_problem: state.problem, platform: state.platform, traffic_source: ATTR.trafficSource() });
      return;
    }
    if (t.hasAttribute('data-platform')) { state.platform = t.getAttribute('data-platform'); SESSION.touch({ platform: state.platform }); save(); render(); return; }
    if (t.hasAttribute('data-symptom')) { var s = t.getAttribute('data-symptom'), i = state.symptoms.indexOf(s); if (i === -1) state.symptoms.push(s); else state.symptoms.splice(i, 1); save(); render({ keepScroll: true }); return; }
    if (t.hasAttribute('data-source')) { var d = t.getAttribute('data-source'), j = state.data.indexOf(d); if (j === -1) state.data.push(d); else state.data.splice(j, 1); save(); render({ keepScroll: true }); return; }
    if (t.hasAttribute('data-next')) { state.step = Math.min(3, state.step + 1); save(); go('start'); return; }
    if (t.hasAttribute('data-back')) { state.step = Math.max(0, state.step - 1); save(); go('start'); return; }
    if (t.hasAttribute('data-finish')) {
      state.plan = D.recommend({ problem: state.problem, platform: state.platform, symptoms: state.symptoms, data: state.data });
      state.step = 4; save();
      var c = prioCounts(state.plan);
      SESSION.touch({ audit_status: 'completed' });
      A.track(EV.AUDIT_COMPLETED, { audit_id: state.auditId, platform: state.platform, primary_problem: state.problem, symptom_count: state.symptoms.length, data_sources: state.data, critical_recommendations: c.CRITICAL, high_recommendations: c.HIGH, medium_recommendations: c.MEDIUM, low_recommendations: c.LOW, audit_duration_seconds: state.auditStartedAt ? Math.round((Date.now() - state.auditStartedAt) / 1000) : undefined });
      go('results'); return;
    }
    if (t.hasAttribute('data-restart') || t.hasAttribute('data-nav-restart')) {
      if (state.plan && !window.confirm('Start over? Your current plan will be cleared (download the report first if you want it).')) return;
      state.step = 0; state.problem = null; state.platform = null; state.symptoms = []; state.data = []; state.plan = null; state.auditId = null; state.auditStartedAt = null; state.reportGenerated = false;
      SESSION.touch({ audit_id: null, audit_status: 'not-started', report_status: 'none', platform: null, primary_problem: null });
      save(); go('start'); return;
    }
    if (t.hasAttribute('data-sample')) { state.sample = t.getAttribute('data-sample'); state.sampleRun = false; state.category = null; save(); render({ keepScroll: true }); return; }
    if (t.hasAttribute('data-run-sample')) { runSample(); return; }
    if (t.hasAttribute('data-category')) { state.category = t.getAttribute('data-category') || null; save(); render({ keepScroll: true }); var dash = $('.dash'); if (dash) dash.scrollIntoView({ block: 'start', behavior: 'smooth' }); return; }
    if (t.hasAttribute('data-finding')) { state.finding = parseInt(t.getAttribute('data-finding'), 10); save(); go('finding'); return; }
    if (t.hasAttribute('data-toolkit')) { go('toolkit'); var el = document.getElementById('mod-' + t.getAttribute('data-toolkit')); if (el) { el.scrollIntoView({ block: 'start' }); el.classList.add('is-hi'); } return; }
    if (t.hasAttribute('data-break')) { state.breakTest = t.getAttribute('data-break'); save(); render({ keepScroll: true }); return; }
    if (t.hasAttribute('data-download')) { doDownload(); return; }
    if (t.hasAttribute('data-copy-report')) { var txt = state.reportFormat === 'html' ? reportHtml() : reportMarkdown(); var st = $('#report-status'); st.hidden = false; (navigator.clipboard && navigator.clipboard.writeText ? navigator.clipboard.writeText(txt) : Promise.reject()).then(function () { st.textContent = 'Report copied to the clipboard.'; }, function () { st.textContent = 'Copying failed; select the preview text and copy it.'; }); return; }
    if (t.hasAttribute('data-plan-ai')) { readPlanner(); if (!state.planner.text.trim() && !state.planner.problem) { var ps = $('#planner-status'); ps.hidden = false; ps.textContent = 'Describe the situation or choose a problem first.'; return; } if (!state.plannerResult) state.plannerResult = deterministicPlan(state.planner); save(); aiPlan(state.planner); return; }
    if (t.hasAttribute('data-clear-journal')) { A.clearJournal(); render(); return; }
  });
  document.addEventListener('submit', function (ev) {
    if (ev.target.id !== 'planner-form') return;
    ev.preventDefault(); readPlanner();
    var st = $('#planner-status');
    if (!state.planner.problem && !state.planner.text.trim()) { st.hidden = false; st.textContent = 'Choose a primary problem or describe what is happening — one of the two is enough.'; return; }
    state.plannerResult = deterministicPlan(state.planner); save(); render({ keepScroll: true });
    var out = $('.plan-out'); if (out) out.scrollIntoView({ block: 'start', behavior: 'smooth' });
  });
  document.addEventListener('change', function (ev) {
    if (ev.target.name === 'fmt') { state.reportFormat = ev.target.value; save(); }
    if (ev.target.closest && ev.target.closest('#planner-form')) readPlanner();
  });
  document.addEventListener('input', function (ev) { if (ev.target.closest && ev.target.closest('#planner-form')) readPlanner(); });
  function readPlanner() {
    var f = $('#planner-form'); if (!f) return;
    state.planner = { platform: f.elements.platform.value, pages: f.elements.pages.value, problem: f.elements.problem.value, text: f.elements.text.value.slice(0, 1200) };
    save();
  }
  function runSample() {
    var box = $('#sample-progress'); if (!box) return;
    box.hidden = false; box.innerHTML = '<p class="progress-h">Analyzing… <span class="fine">(sample data — not a live website scan)</span></p><ul class="checks">' + D.CHECK_SEQUENCE.map(function (c) { return '<li>' + esc(c) + '</li>'; }).join('') + '</ul>';
    var items = $$('#sample-progress .checks li'), i = 0;
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function step() {
      if (i < items.length) { items[i].classList.add('is-done'); i++; setTimeout(step, reduce ? 0 : 140); }
      else { state.sampleRun = true; save(); render({ keepScroll: true }); var dash = $('.dash'); if (dash) dash.scrollIntoView({ block: 'start', behavior: 'smooth' }); }
    }
    setTimeout(step, reduce ? 0 : 200);
  }

  /* ---- boot --------------------------------------------------------------- */
  function boot() {
    route = ROUTES.indexOf(location.hash.replace('#', '')) !== -1 ? location.hash.replace('#', '') : 'start';
    render(); loadCaps();
    if (window.matchMedia && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) document.documentElement.classList.add('motion-ok');
    // artifact_opened: once per session (the analytics layer dedupes), never on rerender.
    A.track(EV.ARTIFACT_OPENED, { referrer: ATTR.inbound().referrer, is_returning_user: SESSION.isReturning || SESSION.visitor().visit_count > 1, visit_count: SESSION.visitor().visit_count });
    if (SESSION.isReturning) A.track(EV.RETURNING_USER_SESSION, { visit_count: SESSION.visitor().visit_count, days_since_previous_session: SESSION.daysSincePrevious(), previous_session_timestamp: SESSION.visitor().previous_session && SESSION.visitor().previous_session.ended ? new Date(SESSION.visitor().previous_session.ended).toISOString() : undefined });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
