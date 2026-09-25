/* app.js — views and interaction for the Launch Readiness Analyzer. */
(function () {
  'use strict';
  var CFG = window.LRA_CONFIG, Q = window.LRA_QUESTIONS, E = window.LRA_ENGINE, A = window.LRA_ANALYTICS;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var money = '$' + CFG.product.price.toFixed(2);

  /* ---- state (persisted; never anything about the user's code) ------------ */
  var KEY = 'lra-state';
  function load() { try { var v = JSON.parse(window.localStorage.getItem(KEY)); return v && typeof v === 'object' ? v : null; } catch (e) { return null; } }
  var saved = load();
  var state = Object.assign({ view: 'hero', step: 0, projectType: null, usage: null, answers: {}, completed: false, startedAt: null, completedAt: null, lastScore: null, reportFormat: 'md' }, saved || {});
  if (typeof state.answers !== 'object' || !state.answers) state.answers = {};
  function save() { try { window.localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }

  var caps = { downloads: null, ready: false };
  if (window.claude && typeof window.claude.use === 'function') window.claude.use('downloads').then(function (d) { caps.downloads = d; caps.ready = true; if (state.view === 'report') render(); }, function () { caps.ready = true; });
  else caps.ready = true;

  /* ---- routing ------------------------------------------------------------- */
  function go(view) { state.view = view; save(); render(); window.scrollTo({ top: 0, behavior: 'auto' }); }
  function render() {
    var main = $('#app');
    main.innerHTML = { hero: hero, assess: assess, report: report }[state.view]();
    $('[data-nav-product]').setAttribute('href', A.productUrl('header'));
    var h = $('#app h1, #app h2'); if (h && state.view !== 'hero') { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
  }

  /* ---- hero ---------------------------------------------------------------- */
  function hero() {
    var back = state.completed && state.lastScore != null;
    return '<section class="hero">' +
      (back ? '<div class="welcome" role="status"><p><strong>Welcome back</strong> — your previous launch assessment is available (' + state.lastScore + ' / 100).</p><div class="row"><button type="button" class="btn btn-primary" data-view-report>View report</button><button type="button" class="btn btn-ghost" data-retake>Retake assessment</button></div></div>' : '') +
      '<p class="eyebrow">Launch readiness estimate</p><h1>Is your Claude Code website actually ready to launch?</h1>' +
      '<p class="lede">Claude Code can build a website quickly. Production readiness requires more than generated code.</p><p class="lede">Take this short assessment to identify gaps across architecture, SEO, security, accessibility, deployment and launch operations.</p>' +
      '<p class="cred">Free assessment • No account required • Takes about 2 minutes</p>' +
      '<div class="row"><button type="button" class="btn btn-primary btn-lg" data-start>Analyze my website project</button></div>' +
      '<p class="fine">You\'ll receive a personalized launch-readiness report and recommended next steps. Answers stay in this browser; nothing is sent anywhere.</p>' +
      '<ol class="areas" aria-label="Areas assessed">' + Q.CATEGORIES.map(function (c) { return '<li>' + esc(c[1]) + '</li>'; }).join('') + '</ol></section>';
  }

  /* ---- assessment ------------------------------------------------------------ */
  var ANSWERS = [['yes', 'Yes'], ['partial', 'Partially'], ['no', 'No'], ['notsure', 'Not sure']];
  function stepQuestions(i) { var st = Q.STEPS[i]; return Q.QUESTIONS.filter(function (q) { return st.cats && st.cats.indexOf(q.cat) !== -1 && Q.applies(q, state.projectType || 'new'); }); }
  function assess() {
    var i = state.step, st = Q.STEPS[i];
    var head = '<nav class="progress" aria-label="Assessment progress"><ol>' + Q.STEPS.map(function (s, n) { return '<li class="' + (n === i ? 'is-current' : n < i ? 'is-done' : '') + '"><span>' + esc(s.title) + '</span></li>'; }).join('') + '<li class="report-step"><span>Report</span></li></ol><p class="stepcount">Step ' + (i + 1) + ' of ' + Q.STEPS.length + '</p></nav>';
    var body;
    if (i === 0) {
      body = '<h2>What are you building?</h2><div class="opts" role="radiogroup" aria-label="Project type">' + Q.PROJECT_TYPES.map(function (p) { return '<button type="button" class="opt' + (state.projectType === p[0] ? ' is-on' : '') + '" role="radio" aria-checked="' + (state.projectType === p[0]) + '" data-type="' + p[0] + '">' + esc(p[1]) + '</button>'; }).join('') + '</div>' +
        '<h2 class="mt">How are you currently using Claude Code?</h2><div class="opts opts-1" role="radiogroup" aria-label="Claude Code usage">' + Q.USAGE.map(function (u) { return '<button type="button" class="opt' + (state.usage === u[0] ? ' is-on' : '') + '" role="radio" aria-checked="' + (state.usage === u[0]) + '" data-usage="' + u[0] + '">' + esc(u[1]) + '</button>'; }).join('') + '</div>';
    } else {
      var qs = stepQuestions(i);
      body = '<h2>' + esc(st.heading) + '</h2><p class="fine">' + (i === 1 ? 'Answer for the project as it is today, not as you intend it to be.' : '"Not sure" is a real answer; it scores as a small credit and shows up as something to find out.') + '</p>' +
        '<div class="qs">' + qs.map(function (q) {
          var a = state.answers[q.id];
          return '<fieldset class="q' + (q.weight > 1 ? ' q-hi' : '') + '"><legend>' + esc(q.text) + (q.label ? ' <span class="qlabel">(' + esc(q.label) + ')</span>' : '') + (q.weight > 1 ? ' <span class="qweight" title="Weighted higher: a missing item here is a significant production risk">weighted</span>' : '') + '</legend><div class="ans" role="radiogroup">' +
            ANSWERS.map(function (o) { return '<button type="button" class="ans-btn' + (a === o[0] ? ' is-on' : '') + '" role="radio" aria-checked="' + (a === o[0]) + '" data-q="' + q.id + '" data-a="' + o[0] + '">' + o[1] + '</button>'; }).join('') + '</div></fieldset>';
        }).join('') + '</div>';
    }
    var canNext = i === 0 ? !!(state.projectType && state.usage) : true;
    var unanswered = i > 0 ? stepQuestions(i).filter(function (q) { return !state.answers[q.id]; }).length : 0;
    var nav = '<div class="navrow"><button type="button" class="btn btn-ghost" data-back ' + (i === 0 ? 'disabled' : '') + '>Back</button>' +
      (unanswered ? '<span class="fine">' + unanswered + ' unanswered — unanswered counts as "No"</span>' : '') +
      '<button type="button" class="btn btn-primary" data-next ' + (canNext ? '' : 'disabled') + '>' + (i === Q.STEPS.length - 1 ? 'Generate my report' : 'Continue') + '</button></div>';
    return '<section class="assess">' + head + body + nav + '</section>';
  }

  /* ---- report -------------------------------------------------------------- */
  function compute() {
    var sc = E.score(state.answers, state.projectType || 'new');
    return { sc: sc, risks: E.topRisks(state.answers, state.projectType || 'new', sc, 3), plan: E.plan(state.answers, state.projectType || 'new', sc), prompts: E.prompts(sc, 3), mapping: E.mapping(state.answers, state.projectType || 'new', sc) };
  }
  function typeLabel() { return (Q.PROJECT_TYPES.filter(function (p) { return p[0] === state.projectType; })[0] || ['', 'website'])[1]; }
  function bandClass(s) { return s >= 75 ? 'good' : s >= 60 ? 'ok' : s >= 40 ? 'warn' : 'bad'; }
  function cta(loc, label, cls) { return '<a class="btn ' + (cls || 'btn-primary') + '" href="' + esc(A.productUrl(loc)) + '" target="_blank" rel="noopener" data-cta="' + esc(loc) + '">' + esc(label) + '</a>'; }
  function report() {
    if (!state.completed) return hero();
    var r = compute(), sc = r.sc;
    var html = '<section class="report">';
    html += '<div class="rhead"><div><p class="eyebrow">Launch readiness estimate · ' + esc(typeLabel()) + '</p><h2>Your launch readiness</h2><p class="lede">Based on the answers you supplied. Use it to prioritise, not to certify: a high score does not guarantee a successful launch — it indicates that more of the common production-readiness areas in this assessment have been addressed.</p></div>' +
      '<div class="bigscore ' + bandClass(sc.overall) + '"><span class="num">' + sc.overall + '<span class="of"> / 100</span></span><span class="band">' + esc(sc.band) + '</span></div></div>';
    html += '<div class="cats">' + Object.keys(sc.categories).map(function (k) { var c = sc.categories[k]; return '<div class="cat"><div class="cat-h"><span>' + esc(c.name) + '</span><span class="num">' + (c.score == null ? '—' : c.score) + '</span></div><div class="bar" role="img" aria-label="' + esc(c.name) + ' ' + (c.score == null ? 'not applicable' : c.score + ' out of 100') + '"><span class="fill ' + bandClass(c.score || 0) + '" style="width:' + (c.score || 0) + '%"></span></div></div>'; }).join('') + '</div>';
    html += '<div class="toolbar"><button type="button" class="btn btn-ghost" data-copy-plan>Copy launch plan</button><button type="button" class="btn btn-ghost" data-copy-prompts>Copy Claude Code prompts</button>' + (caps.downloads ? '<button type="button" class="btn btn-ghost" data-download>Download report</button>' : '') + '<button type="button" class="btn btn-ghost" data-retake>Start over</button><span class="fine" id="tb-status" role="status"></span></div>';
    // risks
    html += '<h2 class="sec">Your top 3 launch risks</h2>' + (r.risks.length ? '<ol class="risks">' + r.risks.map(function (g) {
      return '<li class="risk"><div class="risk-h"><span class="pill ' + (g.q.weight > 1 ? 'pill-hi' : '') + '">' + esc(sc.categories[g.q.cat].name) + '</span><h3>' + esc(riskTitle(g)) + '</h3><span class="ans-tag">you answered: ' + esc({ no: 'No', notsure: 'Not sure', partial: 'Partially', unanswered: 'unanswered' }[g.answer] || g.answer) + '</span></div><dl><dt>Why it matters</dt><dd>' + esc(g.q.why) + '</dd><dt>What to do</dt><dd>' + esc(g.q.do) + '</dd><dt>What to validate</dt><dd>' + esc(g.q.validate) + '</dd></dl></li>';
    }).join('') + '</ol>' : '<p class="good-note">No gaps recorded: every applicable item was answered "Yes". Re-check the weighted items on the production host on launch day.</p>');
    // plan
    html += '<h2 class="sec">Your personalized launch sequence</h2><p class="fine">Phases are built from your gaps; a phase with nothing missing becomes a confirmation.</p><ol class="phases">' + r.plan.map(function (ph) {
      return '<li class="phase' + (ph.confirm ? ' is-clear' : '') + '"><h3><span class="ph-n">Phase ' + ph.number + '</span> ' + esc(ph.title) + '</h3>' + (ph.confirm ? '<p class="confirm">' + esc(ph.confirm) + '</p>' : '<ul>' + ph.items.map(function (it) { return '<li' + (it.weight > 1 ? ' class="hi"' : '') + '>' + esc(it.text) + ' <span class="src">(' + esc(it.item) + ')</span></li>'; }).join('') + (ph.more ? '<li class="more">+ ' + ph.more + ' more in the copied plan</li>' : '') + '</ul>') + '</li>';
    }).join('') + '</ol>';
    // prompts
    html += '<h2 class="sec">Try these with Claude Code</h2><p class="fine">Three starter prompts for your weakest areas. Each is read-only by design: it reports and changes nothing, so the record of what was wrong survives the fix.</p><div class="prompts">' + r.prompts.map(function (p) {
      return '<article class="prompt"><div class="prompt-h"><h3>' + esc(p.title) + '</h3><span class="fine">' + esc(p.name) + ' · ' + (p.score == null ? '—' : p.score) + '</span></div><pre>' + esc(p.text) + '</pre><button type="button" class="btn btn-ghost btn-sm" data-copy-prompt="' + esc(p.cat) + '">Copy prompt</button></article>';
    }).join('') + '</div>';
    // conversion
    html += '<section class="convert" data-recommendation><p class="eyebrow">What comes next</p><h2>You have the launch plan. Now you need the system.</h2><p class="lede">The assessment identified what needs attention. ' + esc(CFG.product.productName) + ' provides the structured prompts, workflows, templates, audits and checklists for executing that work with Claude Code — the difference between Claude Code as an ad-hoc website generator and Claude Code as a repeatable production workflow.</p>' +
      (r.mapping.length ? '<div class="maps">' + r.mapping.map(function (m) { return '<div class="map"><h3>' + esc(m.title) + '</h3><p>' + esc(m.body) + '</p><p class="mod">' + esc(m.module) + '</p></div>'; }).join('') + '</div>' : '<p>Your answers show few gaps; the system is still the fastest way to keep the process repeatable across projects.</p>') +
      '<div class="row">' + cta('module_mapping', 'Get the complete Launch System — ' + money) + '</div></section>';
    // product card
    html += '<section class="product"><div class="pcard"><p class="eyebrow">The product</p><h2>' + esc(CFG.product.productName) + '</h2><p class="lede">' + esc(CFG.product.description) + '</p><ul class="feats">' + CFG.product.features.map(function (f) { return '<li><strong>' + esc(f[0]) + '</strong><span>' + esc(f[1]) + '</span></li>'; }).join('') + '</ul><p class="price">' + money + '</p><div class="row">' + cta('result_primary', 'Get the complete Launch System — ' + money) + '</div><p class="micro"><strong>Instant digital download • One payment • No subscription</strong></p><p class="fine">Requires Claude Code. This system provides workflows and guidance; it does not guarantee search rankings, traffic, revenue, or business results.</p></div>' +
      '<div class="compare"><h2>Instead of building your process from scratch</h2><div class="cmp"><div><h3>Starting from scratch</h3><ul><li>Decide how to structure prompts</li><li>Create your own CLAUDE.md</li><li>Develop your own launch process</li><li>Create SEO checks</li><li>Create security checks</li><li>Create accessibility checks</li><li>Create deployment procedures</li><li>Create launch checklists</li><li>Create post-launch procedures</li></ul></div><div class="with"><h3>With the Launch System</h3><ul><li>Follow an existing structured workflow</li><li>Use reusable prompts and templates</li><li>Work through defined development stages</li><li>Run specialized audits</li><li>Use launch checklists</li><li>Reuse the system across projects</li></ul></div></div></div></section>';
    html += '<section class="final"><h2>Turn your launch checklist into a repeatable system</h2><p class="lede">You already know where your project needs work. ' + esc(CFG.product.productName) + ' gives you the prompts, workflows, templates, audits and checklists to work through those areas systematically.</p><div class="row">' + cta('final_cta', 'Get ' + CFG.product.productName + ' — ' + money) + '<a class="link" href="' + esc(A.productUrl('final_review')) + '" target="_blank" rel="noopener" data-cta="final_review">Review everything included</a></div></section>';
    return html + '</section>';
  }
  function riskTitle(g) {
    var t = g.q.text.replace(/^(A|An) /, '').replace(/ \(.*\)$/, '');
    // Lowercase the first word only when it is an ordinary word, never an
    // acronym or a file name (CLAUDE.md, SEO, HTTPS, DNS, CI/CD).
    if (!/^[A-Z][A-Z0-9./-]/.test(t)) t = t.charAt(0).toLowerCase() + t.slice(1);
    return (g.answer === 'notsure' ? 'Unknown: ' : g.answer === 'partial' ? 'Incomplete: ' : 'Missing: ') + t;
  }

  /* ---- markdown export ---------------------------------------------------- */
  function planMarkdown(r) {
    var L = ['# Launch readiness report — ' + typeLabel(), '', 'Launch Readiness Estimate: **' + r.sc.overall + ' / 100 — ' + r.sc.band + '**  ', 'Generated ' + new Date().toISOString().slice(0, 10) + ' from your own answers. A high score does not guarantee a successful launch; it indicates more of the common production-readiness areas have been addressed.', '', '## Category scores', ''];
    Object.keys(r.sc.categories).forEach(function (k) { var c = r.sc.categories[k]; L.push('- ' + c.name + ': ' + (c.score == null ? 'n/a' : c.score + ' / 100')); });
    L.push('', '## Top launch risks', '');
    r.risks.forEach(function (g, i) { L.push((i + 1) + '. **' + riskTitle(g) + '** (' + r.sc.categories[g.q.cat].name + ')', '   - Why it matters: ' + g.q.why, '   - What to do: ' + g.q.do, '   - What to validate: ' + g.q.validate, ''); });
    L.push('## Launch sequence', '');
    E.plan(state.answers, state.projectType || 'new', r.sc).forEach(function (ph) {
      L.push('### Phase ' + ph.number + ' — ' + ph.title, '');
      if (ph.confirm) L.push(ph.confirm, ''); else { E.gaps(state.answers, state.projectType || 'new', r.sc).filter(function (g) { return ['foundation', 'validate', 'discovery', 'launch', 'post'].indexOf(ph.id) !== -1 && ph.catScores.some(function (c) { return c.key === g.q.cat; }); }).forEach(function (g) { L.push('- [ ] ' + g.q.do + '  _(' + g.q.text + '; validate: ' + g.q.validate + ')_'); }); L.push(''); }
    });
    return L.join('\n');
  }
  function promptsMarkdown(r) { return r.prompts.map(function (p) { return '## ' + p.title + ' (' + p.name + ')\n\n' + p.text + '\n'; }).join('\n'); }
  function fullReport(r) { return planMarkdown(r) + '\n## Claude Code prompts for your weakest areas\n\n' + promptsMarkdown(r) + '\n---\n\nNext: ' + CFG.product.productName + ' — ' + A.productUrl('report') + '\n'; }
  function copy(text, done) {
    var st = $('#tb-status');
    (navigator.clipboard && navigator.clipboard.writeText ? navigator.clipboard.writeText(text) : Promise.reject()).then(function () { if (st) st.textContent = done; }, function () {
      try { var ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.top = '-1000px'; document.body.appendChild(ta); ta.select(); var ok = document.execCommand('copy'); ta.remove(); if (st) st.textContent = ok ? done : 'Copy failed — select the text and copy it.'; } catch (e) { if (st) st.textContent = 'Copy failed — select the text and copy it.'; }
    });
  }

  /* ---- events -------------------------------------------------------------- */
  function props(extra) { var sc = state.completed ? E.score(state.answers, state.projectType || 'new') : null; return Object.assign({ project_type: state.projectType, claude_usage: state.usage, readiness_score_band: sc ? E.bandKey(sc.overall) : undefined, lowest_category: sc ? E.lowestCategory(sc) : undefined }, extra || {}); }
  document.addEventListener('click', function (ev) {
    var t = ev.target.closest('[data-start],[data-view-report],[data-retake],[data-type],[data-usage],[data-q],[data-back],[data-next],[data-copy-plan],[data-copy-prompts],[data-copy-prompt],[data-download],[data-cta]');
    if (!t) return;
    if (t.hasAttribute('data-cta')) { A.track('product_cta_clicked', props({ cta_location: t.getAttribute('data-cta'), product_url: CFG.product.productUrl })); return; }
    if (t.hasAttribute('data-start')) { state.step = 0; if (!state.startedAt) state.startedAt = Date.now(); go('assess'); return; }
    if (t.hasAttribute('data-view-report')) { go('report'); return; }
    if (t.hasAttribute('data-retake')) { if (state.completed && !window.confirm('Start over? Your previous answers and report will be cleared.')) return; state = { view: 'assess', step: 0, projectType: null, usage: null, answers: {}, completed: false, startedAt: Date.now(), completedAt: null, lastScore: null, reportFormat: 'md' }; save(); render(); window.scrollTo(0, 0); return; }
    if (t.hasAttribute('data-type')) { var first = !state.projectType && !state.usage; state.projectType = t.getAttribute('data-type'); save(); render(); if (first) A.track('assessment_started', props()); return; }
    if (t.hasAttribute('data-usage')) { var f2 = !state.projectType && !state.usage; state.usage = t.getAttribute('data-usage'); save(); render(); if (f2) A.track('assessment_started', props()); return; }
    if (t.hasAttribute('data-q')) { state.answers[t.getAttribute('data-q')] = t.getAttribute('data-a'); save(); var fs = t.closest('fieldset'); $$('.ans-btn', fs).forEach(function (b) { var on = b === t; b.classList.toggle('is-on', on); b.setAttribute('aria-checked', on); }); var un = stepQuestions(state.step).filter(function (q) { return !state.answers[q.id]; }).length; var note = $('.navrow .fine'); if (note) note.textContent = un ? un + ' unanswered — unanswered counts as "No"' : ''; return; }
    if (t.hasAttribute('data-back')) { state.step = Math.max(0, state.step - 1); go('assess'); return; }
    if (t.hasAttribute('data-next')) {
      A.track('assessment_step_completed', props({ step: Q.STEPS[state.step].id, step_index: state.step + 1 }));
      if (state.step < Q.STEPS.length - 1) { state.step++; go('assess'); return; }
      state.completed = true; state.completedAt = Date.now(); var sc = E.score(state.answers, state.projectType || 'new'); state.lastScore = sc.overall; save();
      A.track('assessment_completed', props()); A.track('report_generated', props());
      go('report'); observeRecommendation(); return;
    }
    if (t.hasAttribute('data-copy-plan')) { copy(planMarkdown(compute()), 'Launch plan copied as Markdown.'); A.track('launch_plan_copied', props()); return; }
    if (t.hasAttribute('data-copy-prompts')) { copy(promptsMarkdown(compute()), 'Prompts copied.'); A.track('claude_prompt_copied', props({ prompt_category: 'all' })); return; }
    if (t.hasAttribute('data-copy-prompt')) { var cat = t.getAttribute('data-copy-prompt'); var p = compute().prompts.filter(function (x) { return x.cat === cat; })[0]; if (!p) return; copy(p.text, 'Prompt copied: ' + p.title + '.'); t.textContent = 'Copied'; setTimeout(function () { t.textContent = 'Copy prompt'; }, 1800); A.track('claude_prompt_copied', props({ prompt_category: cat })); return; }
    if (t.hasAttribute('data-download')) {
      var st = $('#tb-status'); var name = 'launch-readiness-report-' + new Date().toISOString().slice(0, 10) + '.md';
      st.textContent = 'Preparing ' + name + '…';
      caps.downloads.save({ filename: name, data: fullReport(compute()) }).then(function () { st.textContent = 'Saved ' + name + '.'; A.track('report_downloaded', props({ report_format: 'markdown' })); }, function (e) { st.textContent = e && e.code === 'declined' ? 'Download cancelled.' : 'Download not available here — use Copy launch plan instead.'; });
      return;
    }
  });
  function observeRecommendation() {
    var el = $('[data-recommendation]'); if (!el) return;
    if (!('IntersectionObserver' in window)) { A.track('product_recommendation_viewed', props()); return; }
    var io = new IntersectionObserver(function (entries) { if (entries.some(function (e) { return e.isIntersecting; })) { A.track('product_recommendation_viewed', props()); io.disconnect(); } }, { threshold: 0.3 });
    io.observe(el);
  }

  /* ---- boot --------------------------------------------------------------- */
  function boot() {
    if (state.view === 'assess' && !(state.projectType || state.usage || Object.keys(state.answers).length)) state.view = 'hero';
    if (state.view === 'report' && !state.completed) state.view = 'hero';
    if (state.view === 'assess' && state.step >= Q.STEPS.length) state.step = Q.STEPS.length - 1;
    render();
    if (state.view === 'report') observeRecommendation();
    A.track('artifact_opened', props({ is_returning: A.isReturning }));
    if (A.isReturning) A.track('returning_artifact_session', props());
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
