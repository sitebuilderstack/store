/* engine.js — scoring and recommendation logic. Pure functions over the
 * answers; no DOM, so scripts/test-launch-analyzer.js can exercise them. */
window.LRA_ENGINE = (function () {
  'use strict';
  var Q = window.LRA_QUESTIONS, CFG = window.LRA_CONFIG;
  var VALUE = { yes: 1, partial: 0.5, notsure: 0.25, no: 0 };
  var BANDS = [[90, 'Highly Prepared'], [75, 'Strong Foundation'], [60, 'Approaching Launch Readiness'], [40, 'Foundation In Progress'], [0, 'Major Launch Gaps']];

  function applicable(projectType) { return Q.QUESTIONS.filter(function (q) { return Q.applies(q, projectType); }); }

  function score(answers, projectType) {
    var cats = {}, totalEarned = 0, totalMax = 0;
    Q.CATEGORIES.forEach(function (c) { cats[c[0]] = { key: c[0], name: c[1], earned: 0, max: 0, answered: 0, count: 0 }; });
    applicable(projectType).forEach(function (q) {
      var c = cats[q.cat]; var a = answers[q.id]; var v = VALUE[a];
      c.max += q.weight; c.count++;
      if (v !== undefined) { c.earned += q.weight * v; c.answered++; }
      totalMax += q.weight; if (v !== undefined) totalEarned += q.weight * v;
    });
    var out = {};
    Object.keys(cats).forEach(function (k) { var c = cats[k]; c.score = c.max ? Math.round(c.earned / c.max * 100) : null; out[k] = c; });
    var overall = totalMax ? Math.round(totalEarned / totalMax * 100) : 0;
    return { overall: overall, band: band(overall), categories: out, answeredCount: Object.keys(answers).length, questionCount: totalMax ? applicable(projectType).length : 0 };
  }
  function band(s) { for (var i = 0; i < BANDS.length; i++) if (s >= BANDS[i][0]) return BANDS[i][1]; return BANDS[BANDS.length - 1][1]; }
  function bandKey(s) { return s >= 90 ? 'highly-prepared' : s >= 75 ? 'strong' : s >= 60 ? 'approaching' : s >= 40 ? 'in-progress' : 'major-gaps'; }

  /* Gaps: applicable questions answered no / notsure / partial, ordered by
     (weight × missing value), then category weakness. */
  function gaps(answers, projectType, sc) {
    return applicable(projectType).map(function (q) {
      var v = VALUE[answers[q.id]]; if (v === undefined) v = 0;
      return { q: q, missing: (1 - v) * q.weight, answer: answers[q.id] || 'unanswered', catScore: sc.categories[q.cat].score };
    }).filter(function (g) { return g.missing > 0; }).sort(function (a, b) { return b.missing - a.missing || (a.catScore || 0) - (b.catScore || 0) || a.q.id.localeCompare(b.q.id); });
  }
  function topRisks(answers, projectType, sc, n) {
    var seenCat = {}, out = [], all = gaps(answers, projectType, sc);
    // prefer one risk per category so the three are not all "SEO"
    all.forEach(function (g) { if (out.length < (n || 3) && !seenCat[g.q.cat]) { seenCat[g.q.cat] = true; out.push(g); } });
    all.forEach(function (g) { if (out.length < (n || 3) && out.indexOf(g) === -1) out.push(g); });
    return out;
  }

  /* Launch plan: five phases, each populated only with this project's gaps;
     a phase with nothing missing becomes a short confirmation. */
  var PHASES = [
    { id: 'foundation', title: 'Fix the foundation', cats: ['planning', 'claude'], confirm: 'Planning and Claude Code configuration are in place. Keep CLAUDE.md true as the project changes.' },
    { id: 'validate', title: 'Validate the build', cats: ['testing', 'security', 'a11y'], confirm: 'Testing, security and accessibility have been covered. Re-run the checks after the last change before launch.' },
    { id: 'discovery', title: 'Prepare discovery', cats: ['seo'], confirm: 'SEO groundwork is done. Verify canonicals and robots on the production host on launch day.' },
    { id: 'launch', title: 'Production launch', cats: ['deployment'], confirm: 'Deployment is repeatable. Rehearse the rollback once more before go.' },
    { id: 'post', title: 'Post-launch', cats: ['launch'], confirm: 'Launch operations are planned. Put the 24-hour, 7-day and 30-day reviews in the calendar.' },
  ];
  function plan(answers, projectType, sc) {
    var g = gaps(answers, projectType, sc);
    return PHASES.map(function (ph, i) {
      var items = g.filter(function (x) { return ph.cats.indexOf(x.q.cat) !== -1; }).sort(function (a, b) { return b.missing - a.missing; });
      return { number: i + 1, id: ph.id, title: ph.title, items: items.slice(0, 8).map(function (x) { return { text: x.q.do, item: x.q.text, weight: x.q.weight, answer: x.answer }; }), more: Math.max(0, items.length - 8), confirm: items.length ? null : ph.confirm, catScores: ph.cats.map(function (c) { return sc.categories[c]; }) };
    });
  }

  /* Prompts: one per category, chosen from the three weakest categories. */
  var PROMPTS = {
    planning: { title: 'Planning and architecture review', text: 'Review this repository\'s project documentation (brief, requirements, architecture, stack decisions). List what is missing or ambiguous for a production launch: pages and URL structure, data sources, content management, acceptance conditions per requirement, and a definition of done. Do not change any file; output a prioritised list with a one-line reason each and the question I need to answer for each gap.' },
    claude: { title: 'CLAUDE.md audit', text: 'Audit this repository\'s CLAUDE.md and project documentation. Identify missing project constraints, commands (build, test, lint, deploy), coding standards, testing requirements, deployment rules, things that must never be done, and definition-of-done criteria. Run each command the file names and report whether it works. Do not edit CLAUDE.md; output the gaps as a checklist I can work through.' },
    seo: { title: 'Technical SEO readiness audit', text: 'Audit this website for technical SEO readiness. Inspect crawlability, indexability, canonicalization, metadata (titles, descriptions, headings), structured data, internal linking, sitemap configuration, robots.txt, and performance risks. Read rendered output, not templates. Change nothing. For every finding give the URL, the observed value, why it matters, and what to verify after a fix.' },
    security: { title: 'Production-readiness security review', text: 'Perform a production-readiness security review of this application. Check dependency risk, secret exposure (repository and history), authentication and authorization boundaries, security headers, HTTPS and redirect configuration, environment configuration and debug settings, backup and restore, and common OWASP-related weaknesses. Read-only: report findings with evidence (file:line, header, command output), severity and a recommended fix; make no changes.' },
    a11y: { title: 'Accessibility audit (WCAG 2.2 AA)', text: 'Audit the key pages of this site against WCAG 2.2 AA: keyboard operability of every control, visible focus, semantic structure (landmarks, heading order), image alt text, form labels and error messages, colour contrast, and accessible names and roles on custom components. Change nothing. Output a table: page, criterion, element, observed, fix. Then list what an automated check cannot verify and needs a manual pass.' },
    testing: { title: 'Pre-launch test plan', text: 'Write a pre-launch test plan for this site and then execute what can be executed locally against the production build: the flows that convert (forms with a marked submission, primary calls to action landing where their labels promise), error states (empty, invalid, failed request), responsive layout at 390, 820 and 1280 px, broken internal links, and the production build served locally. Report each check as pass/fail with the observed value; do not fix anything in the same run.' },
    deployment: { title: 'Deployment and rollback review', text: 'Review how this project is deployed: the deployment procedure, CI/CD pipeline and what it checks before deploying, environment separation (preview/staging vs production), environment-variable handling, DNS and caching configuration, monitoring, and the rollback procedure. Identify every step that lives only in someone\'s head and write it down. Then draft the rollback steps as exact commands and say how to verify a rollback worked. Do not deploy or change configuration.' },
    launch: { title: 'Launch and post-launch checklist', text: 'Build a launch checklist for this site with an evidence column per line: production robots.txt and homepage head (no noindex), canonicals on the production host, sitemap served and submitted, analytics firing once per key event, forms delivering, redirects landing in one hop, 404 log review, and the 24-hour, 7-day and 30-day review items. For each line say what to fetch or observe and what "pass" looks like. Do not tick anything; I will.' },
  };
  function prompts(sc, n) {
    var order = Object.keys(sc.categories).sort(function (a, b) { return (sc.categories[a].score || 0) - (sc.categories[b].score || 0); });
    return order.slice(0, n || 3).map(function (k) { return { cat: k, name: sc.categories[k].name, score: sc.categories[k].score, title: PROMPTS[k].title, text: PROMPTS[k].text }; });
  }

  /* Product mapping: weaknesses → the product's own module names. Only
     mappings relevant to this visitor are returned. */
  function mapping(answers, projectType, sc) {
    var M = CFG.modules, out = [];
    var g = gaps(answers, projectType, sc);
    // A category is relevant when its score is below 75, or when it holds a
    // weighted item answered No or Not sure — one missing rollback matters
    // more than the category average suggests.
    var weak = function (k, t) { return (sc.categories[k].score || 0) < (t || 75) || g.some(function (x) { return x.q.cat === k && x.q.weight > 1 && x.missing >= 1.5; }); };
    if (weak('planning')) out.push({ title: 'Your report identified planning and architecture gaps.', body: 'The Launch System starts with a discovery, planning and roadmap chain and a staged master build prompt, so the structure is decided before the code is generated.', module: M.master });
    if (weak('claude')) out.push({ title: 'Your report identified Claude Code configuration gaps.', body: 'It includes a production-grade CLAUDE.md template and a guide to how memory files load, what belongs in them and why shorter files are followed more reliably.', module: M.claude });
    if (weak('seo')) out.push({ title: 'Your report identified SEO gaps.', body: 'The SEO System covers search architecture, the technical audit, keyword research and intent, content clusters, internal linking, schema, sitemaps, robots.txt and llms.txt.', module: M.seo });
    if (weak('security')) out.push({ title: 'Your report identified production-security gaps.', body: 'The Security module covers secret scanning, dependency auditing, OWASP review, HTTP security headers and a production security checklist.', module: M.security });
    if (weak('a11y')) out.push({ title: 'Your report identified accessibility gaps.', body: 'The Accessibility module is a WCAG 2.2 AA audit with keyboard navigation and screen-reader testing workflows and a working checklist.', module: M.a11y });
    if (weak('deployment')) out.push({ title: 'Your report identified deployment gaps.', body: 'The Deployment modules cover GitHub repository setup, the CI/CD workflow with four working GitHub Actions files, and Cloudflare DNS, Pages, caching and security.', module: M.deploy });
    var idx = answers.indexing, gsc = answers.gsc, bing = answers.bing;
    if ([idx, gsc, bing].some(function (a) { return a && a !== 'yes'; })) out.push({ title: 'Your report identified indexing gaps.', body: 'The Search Engines module covers Google Search Console, Bing Webmaster Tools and IndexNow, with honest expectations about what submission does and does not do.', module: M.engines });
    if (weak('launch')) out.push({ title: 'Your report identified launch-process gaps.', body: 'The Checklists module has the pre-launch, launch-day, first-24-hours, 7-day and 30-day reviews.', module: M.checklists });
    var platform = { shopify: M.shopify, wordpress: M.wordpress, astro: M.astro, saas: M.saas, landing: M.landing }[projectType];
    if (platform) out.push({ title: 'You are building a ' + { shopify: 'Shopify store', wordpress: 'WordPress site', astro: 'Astro site', saas: 'SaaS application', landing: 'landing page' }[projectType] + '.', body: 'The platform system for it has its own build prompt, audits and launch checklist.', module: platform });
    if (projectType === 'redesign' || projectType === 'improve') out.push({ title: 'You are working on an existing site.', body: 'The bonus prompts cover website rescue, existing-site audit, redesign, competitor analysis and AI code review.', module: M.bonus });
    var smallGaps = g.filter(function (x) { return x.q.weight === 1; }).length;
    if (smallGaps >= 8) out.push({ title: 'Your report found many smaller gaps.', body: 'The Prompt Library is 100 single-purpose prompts across eleven categories, ready to save as slash commands, so each small gap is one command away.', module: M.prompts });
    return out;
  }
  function lowestCategory(sc) { return Object.keys(sc.categories).sort(function (a, b) { return (sc.categories[a].score || 0) - (sc.categories[b].score || 0); })[0]; }

  return { VALUE: VALUE, score: score, band: band, bandKey: bandKey, gaps: gaps, topRisks: topRisks, plan: plan, prompts: prompts, mapping: mapping, lowestCategory: lowestCategory, applicable: applicable };
})();
