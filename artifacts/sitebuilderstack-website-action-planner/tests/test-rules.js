#!/usr/bin/env node
/* tests/test-rules.js — the decision engine, exercised directly.
 *
 * Scenarios 1–12 are the ones named in the brief. Everything after them
 * covers the qualification rules, the bundle arithmetic, price freshness,
 * answer hygiene and the export. No browser, no network.
 *
 *   node tests/test-rules.js
 */
'use strict';
const path = require('path');
const R = require(path.join(__dirname, '..', 'recommendation-rules.js'));
const CAT = require(path.join(__dirname, '..', 'products.json'));
const TODAY = CAT.snapshot.verifiedOn;              // prices fresh
const STALE = '2027-01-01';                          // far outside the window

let pass = 0, fail = 0;
const failures = [];
function t(name, fn) {
  try { fn(); pass++; console.log('  ✓ ' + name); }
  catch (e) { fail++; failures.push(name + '\n      ' + e.message); console.log('  ✗ ' + name + '\n      ' + e.message); }
}
function eq(a, b, m) { if (a !== b) throw new Error((m || '') + ' expected ' + JSON.stringify(b) + ', got ' + JSON.stringify(a)); }
function ok(v, m) { if (!v) throw new Error(m || 'expected truthy, got ' + JSON.stringify(v)); }
function no(v, m) { if (v) throw new Error(m || 'expected falsy, got ' + JSON.stringify(v)); }
function has(hay, needle, m) { if (String(hay).toLowerCase().indexOf(String(needle).toLowerCase()) === -1) throw new Error((m || '') + ' expected to contain ' + JSON.stringify(needle)); }
function hasnt(hay, needle, m) { if (String(hay).toLowerCase().indexOf(String(needle).toLowerCase()) !== -1) throw new Error((m || '') + ' expected NOT to contain ' + JSON.stringify(needle)); }

const d = (answers, today) => R.decide(answers, CAT, { today: today || TODAY });
const base = { readiness: 'using', owns: ['none'] };
const A = (o) => Object.assign({}, base, o);

console.log('\nThe twelve named scenarios\n');

t('1. New Shopify store → Launch System, not the Automation Toolkit', () => {
  const r = d(A({ goal: 'build', platform: 'shopify', stage: 'idea', build_blocker: 'no_plan' }));
  eq(r.primary.id, 'website-launch-system');
  no(r.complementary && r.complementary.id === 'shopify-automation', 'automation must not be offered');
  eq(r.mode, 'recommend');
  const all = JSON.stringify(r);
  hasnt(r.primary.product.title, 'Automation');
});

t('1b. Shopify + building, still the Launch System', () => {
  const r = d(A({ goal: 'build', platform: 'shopify', stage: 'building', build_blocker: 'quality' }));
  eq(r.primary.id, 'website-launch-system');
});

t('2. Existing WordPress site with little search traffic → SEO Toolkit', () => {
  const r = d(A({ goal: 'seo', platform: 'wordpress', stage: 'live_no_traffic', seo_symptom: 'never_audited' }));
  eq(r.primary.id, 'seo-audit-toolkit');
  eq(r.mode, 'recommend');
});

t('3. Existing traffic with a conversion goal → Conversion Toolkit', () => {
  const r = d(A({ goal: 'convert', platform: 'shopify', stage: 'live_traffic', conv_measurement: 'yes' }));
  eq(r.primary.id, 'conversion-toolkit');
  no(r.flags.convert_no_traffic);
  no(r.flags.convert_not_live);
});

t('4. Live site with maintenance needs → Operations System', () => {
  const r = d(A({ goal: 'maintain', platform: 'wordpress', stage: 'live_traffic', maintain_checks: ['none'] }));
  eq(r.primary.id, 'operations-system');
  ok(r.actions.some(a => /restore/i.test(a.what)), 'untested backups should surface a restore action');
});

t('5. Shopify inventory / bulk-admin problem → Automation Toolkit', () => {
  const r = d(A({ goal: 'shopify_admin', platform: 'shopify', stage: 'live_traffic', admin_task: 'inventory_pricing' }));
  eq(r.primary.id, 'shopify-automation');
  has(r.actions[0].what, 'Export');
});

t('6. Website moving platforms → Migration System', () => {
  const r = d(A({ goal: 'migrate', platform: 'wordpress', stage: 'live_traffic', migrate_from: 'wordpress', migrate_to: 'astro' }));
  eq(r.primary.id, 'migration-system');
  has(r.actions[0].what, 'Inventory');
});

t('7. Client scoping or handoff problem → Agency System', () => {
  const r = d(A({ goal: 'agency', platform: 'undecided', stage: 'multi_site', agency_problem: 'scoping' }));
  eq(r.primary.id, 'agency-system');
  has(r.actions[0].what, 'scope');
});

t('8. Relevant multi-product need → accurate bundle comparison', () => {
  const C = R.indexCatalogue(CAT), ps = R.priceState(C, TODAY);
  const three = R.bundleComparison(C, ['website-launch-system', 'seo-audit-toolkit', 'conversion-toolkit'], [], ps);
  eq(three.verdict, 'bundle_cheaper');
  eq(three.individualTotal, 59.97);
  eq(three.bundlePrice, 39.99);
  eq(three.difference, 19.98);
  has(three.statement, '$59.97'); has(three.statement, '$39.99'); has(three.statement, '$19.98');

  const two = R.bundleComparison(C, ['website-launch-system', 'seo-audit-toolkit'], [], ps);
  eq(two.verdict, 'individual_cheaper');
  eq(two.individualTotal, 39.98);
  eq(two.difference, -0.01);
  has(two.statement, 'cheaper');
  hasnt(two.statement, 'save');

  const one = R.bundleComparison(C, ['seo-audit-toolkit'], [], ps);
  eq(one.verdict, 'single_product');
  has(one.statement, 'more');

  // A visitor whose two goals map into two bundle members must NOT be sold the bundle.
  const r = d(A({ goal: 'seo', goal_secondary: 'convert', platform: 'wordpress', stage: 'live_traffic', seo_symptom: 'indexed_no_rank', conv_measurement: 'yes' }));
  eq(r.primary.id, 'seo-audit-toolkit');
  eq(r.complementary.id, 'conversion-toolkit');
  eq(r.offerBundle, false, 'two products must not trigger a bundle offer');
  eq(r.bundle.verdict, 'individual_cheaper');
  eq(r.bundle.individualTotal, 39.98);
  eq(r.bundle.bundlePrice, 39.99);

  // Two goals that qualify down to the same product are one product, not two.
  const collapsed = d(A({ goal: 'build', goal_secondary: 'seo', platform: 'astro', stage: 'idea', build_blocker: 'no_plan', seo_symptom: 'never_audited' }));
  eq(collapsed.primary.id, 'website-launch-system');
  eq(collapsed.complementary, null);
  eq(collapsed.bundle.verdict, 'single_product');
  eq(collapsed.offerBundle, false);
});

t('8b. Bundle offered only when the arithmetic supports it', () => {
  const C = R.indexCatalogue(CAT), ps = R.priceState(C, TODAY);
  const owned = R.bundleComparison(C, ['website-launch-system', 'seo-audit-toolkit', 'conversion-toolkit'], ['seo-audit-toolkit'], ps);
  eq(owned.unowned.length, 2);
  eq(owned.individualTotal, 39.98);
  eq(owned.verdict, 'individual_cheaper');
  has(owned.statement, 'already own');
  const all = R.bundleComparison(C, ['website-launch-system', 'seo-audit-toolkit'], ['complete-stack'], ps);
  eq(all.verdict, 'already_owned');
});

t('9. Existing owner → no duplicate-purchase recommendation', () => {
  const r = d(A({ goal: 'seo', platform: 'wordpress', stage: 'live_traffic', seo_symptom: 'indexed_no_rank', owns: ['seo-audit-toolkit'] }));
  no(r.primary && r.primary.id === 'seo-audit-toolkit', 'must not re-sell an owned product');
  eq(r.ownership.ownedPrimary, 'seo-audit-toolkit');
  has(r.ownership.notes.join(' '), 'already own');
  eq(r.offerBundle, false);
});

t('10. Beginner not ready for Claude Code → useful free starting path', () => {
  const r = d(A({ goal: 'build', platform: 'shopify', stage: 'idea', build_blocker: 'no_plan', readiness: 'exploring' }));
  eq(r.mode, 'free_first');
  ok(r.primary.deEmphasised, 'the product must be de-emphasised, not pushed');
  eq(r.freeStep.resource.id, 'free-terminal-setup');
  has(r.actions[0].what, 'Install Claude Code');
  has(r.qualificationNotes.join(' '), 'terminal');
});

t('11. Unknown or conflicting answers → a qualified result, not false certainty', () => {
  // Shopify automation selected, but the platform is not Shopify.
  const r1 = d(A({ goal: 'shopify_admin', platform: 'wordpress', stage: 'live_traffic', admin_task: 'inventory_pricing' }));
  eq(r1.mode, 'qualified');
  eq(r1.primary, null);
  has(r1.qualificationNotes.join(' '), 'only applies to a Shopify store');

  // On Shopify, but bulk admin is explicitly not the problem.
  const r2 = d(A({ goal: 'shopify_admin', platform: 'shopify', stage: 'live_traffic', admin_task: 'none' }));
  eq(r2.mode, 'qualified');
  eq(r2.primary, null);
  has(r2.qualificationNotes.join(' '), 'not on its own a reason');
  eq(r2.freeStep.resource.id, 'free-shopify-hub');

  // Nothing selected at all.
  const r3 = d({ owns: [] });
  eq(r3.mode, 'qualified');
  eq(r3.primary, null);
  has(r3.actions[0].why, 'will not invent a diagnosis');

  // "Not sure" everywhere that allows it.
  const r4 = d(A({ goal: 'seo', platform: 'undecided', stage: 'live_traffic', seo_symptom: 'notsure', owns: ['notsure'] }));
  eq(r4.primary.id, 'seo-audit-toolkit');
  ok(r4.ownership.unknown);
  has(r4.ownership.notes.join(' '), 'order confirmation');
});

t('12. Relevant products already owned → a usage plan, not a forced sale', () => {
  const r = d(A({ goal: 'build', platform: 'astro', stage: 'building', build_blocker: 'stalled', owns: ['website-launch-system'] }));
  eq(r.mode, 'use_what_you_own');
  eq(r.primary, null);
  eq(r.complementary, null);
  eq(r.offerBundle, false);
  has(r.headline, 'already own');
  eq(r.actions.length, 3);
  ok(r.freeStep, 'a free next step is still offered');
});

t('12b. Owning the bundle counts as owning its three members', () => {
  const r = d(A({ goal: 'convert', platform: 'shopify', stage: 'live_traffic', conv_measurement: 'yes', owns: ['complete-stack'] }));
  eq(r.mode, 'use_what_you_own');
  eq(r.primary, null);
});

console.log('\nQualification rules\n');

t('Conversion is not recommended for a site that is not live', () => {
  ['idea', 'building'].forEach(stage => {
    const r = d(A({ goal: 'convert', platform: 'astro', stage, conv_measurement: 'no' }));
    eq(r.primary.id, 'website-launch-system', 'stage=' + stage);
    ok(r.flags.convert_not_live);
    has(r.qualificationNotes.join(' '), 'needs a site that is live');
  });
});

t('Conversion is not recommended to a site with no traffic', () => {
  const r = d(A({ goal: 'convert', platform: 'wordpress', stage: 'live_no_traffic', conv_measurement: 'yes' }));
  eq(r.primary.id, 'seo-audit-toolkit');
  ok(r.flags.convert_no_traffic);
  has(r.summary, 'discovery');
});

t('Unknown measurement produces a measurement check, not a diagnosis', () => {
  ['no', 'notsure', 'partial'].forEach(m => {
    const r = d(A({ goal: 'convert', platform: 'saas', stage: 'live_traffic', conv_measurement: m }));
    eq(r.primary.id, 'conversion-toolkit');
    has(r.actions[0].what, 'verify the conversion event', 'measurement=' + m);
  });
  const known = d(A({ goal: 'convert', platform: 'saas', stage: 'live_traffic', conv_measurement: 'yes' }));
  has(known.actions[0].what, 'Build the funnel');
});

t('An SEO or maintenance goal before launch routes to the build product', () => {
  const seo = d(A({ goal: 'seo', platform: 'astro', stage: 'building', seo_symptom: 'never_audited' }));
  eq(seo.primary.id, 'website-launch-system');
  ok(seo.flags.seo_before_launch);
  const maint = d(A({ goal: 'maintain', platform: 'astro', stage: 'idea', maintain_checks: ['notsure'] }));
  eq(maint.primary.id, 'website-launch-system');
  ok(maint.flags.maintain_not_live);
});

t('Agency alone does not override a stated project problem', () => {
  const r = d(A({ goal: 'agency', goal_secondary: 'migrate', platform: 'wordpress', stage: 'multi_site', migrate_from: 'wordpress', migrate_to: 'shopify', agency_problem: 'scoping' }));
  eq(r.primary.id, 'migration-system', 'the migration leads');
  eq(r.complementary.id, 'agency-system', 'the agency system supports it');
  ok(r.flags.agency_defers);
});

t('Operating several sites does not by itself mean the Agency System', () => {
  const r = d(A({ goal: 'maintain', platform: 'wordpress', stage: 'multi_site', maintain_checks: ['backups'] }));
  eq(r.primary.id, 'operations-system');
});

t('Being on Shopify never by itself produces the Automation Toolkit', () => {
  const goals = ['build', 'seo', 'convert', 'maintain', 'migrate', 'agency'];
  const stages = { build: 'idea', seo: 'live_traffic', convert: 'live_traffic', maintain: 'live_traffic', migrate: 'live_traffic', agency: 'multi_site' };
  goals.forEach(g => {
    const r = d(A({ goal: g, platform: 'shopify', stage: stages[g], seo_symptom: 'never_audited', conv_measurement: 'yes', maintain_checks: ['none'], migrate_from: 'shopify', migrate_to: 'astro', agency_problem: 'qa', build_blocker: 'no_plan' }));
    no(r.primary && r.primary.id === 'shopify-automation', 'goal=' + g + ' must not route to automation');
    no(r.complementary && r.complementary.id === 'shopify-automation', 'goal=' + g + ' complementary');
  });
});

t('An unknown Shopify admin task asks for the task before selling anything', () => {
  const r = d(A({ goal: 'shopify_admin', platform: 'shopify', stage: 'live_traffic', admin_task: 'notsure' }));
  eq(r.primary.id, 'shopify-automation');
  ok(r.flags.shopify_admin_task_unknown);
  has(r.actions[0].what, 'Name the task');
});

t('All seven individual products are reachable from the questionnaire', () => {
  const cases = [
    [{ goal: 'build', platform: 'astro', stage: 'idea', build_blocker: 'no_plan' }, 'website-launch-system'],
    [{ goal: 'seo', platform: 'wordpress', stage: 'live_traffic', seo_symptom: 'not_indexed' }, 'seo-audit-toolkit'],
    [{ goal: 'convert', platform: 'shopify', stage: 'live_traffic', conv_measurement: 'yes' }, 'conversion-toolkit'],
    [{ goal: 'maintain', platform: 'wordpress', stage: 'live_traffic', maintain_checks: ['backups'] }, 'operations-system'],
    [{ goal: 'shopify_admin', platform: 'shopify', stage: 'live_traffic', admin_task: 'catalogue_seo' }, 'shopify-automation'],
    [{ goal: 'migrate', platform: 'wordpress', stage: 'live_traffic', migrate_from: 'wordpress', migrate_to: 'astro' }, 'migration-system'],
    [{ goal: 'agency', platform: 'undecided', stage: 'multi_site', agency_problem: 'handoff' }, 'agency-system'],
  ];
  cases.forEach(([ans, want]) => eq(d(A(ans)).primary.id, want, JSON.stringify(ans.goal)));
});

console.log('\nAnswer hygiene\n');

t('Answers to questions that no longer apply are discarded', () => {
  const n = R.normalize({ goal: 'build', platform: 'shopify', stage: 'idea', conv_measurement: 'yes', admin_task: 'inventory_pricing', agency_problem: 'qa', owns: ['none'] });
  eq(n.conv_measurement, undefined);
  eq(n.admin_task, undefined);
  eq(n.agency_problem, undefined);
  eq(n.build_blocker, undefined);
});

t('A hidden answer cannot change the recommendation', () => {
  const clean = d(A({ goal: 'build', platform: 'shopify', stage: 'idea', build_blocker: 'no_plan' }));
  const dirty = d(A({ goal: 'build', platform: 'shopify', stage: 'idea', build_blocker: 'no_plan', admin_task: 'inventory_pricing', conv_measurement: 'no', agency_problem: 'scoping', migrate_from: 'wordpress' }));
  eq(dirty.primary.id, clean.primary.id);
  eq(JSON.stringify(dirty.actions), JSON.stringify(clean.actions));
});

t('A secondary goal identical to the primary is dropped', () => {
  const n = R.normalize({ goal: 'seo', goal_secondary: 'seo', owns: [] });
  eq(n.goal_secondary, undefined);
});

t('"None" and "not sure" are exclusive ownership answers', () => {
  eq(JSON.stringify(R.normalize({ owns: ['none', 'seo-audit-toolkit'] }).owns), JSON.stringify(['none']));
  eq(JSON.stringify(R.normalize({ owns: ['notsure', 'seo-audit-toolkit'] }).owns), JSON.stringify(['notsure']));
});

t('Contextual questions follow the active goals', () => {
  eq(JSON.stringify(R.relevantContextKeys({ goal: 'migrate' })), JSON.stringify(['migrate_from', 'migrate_to']));
  const both = R.relevantContextKeys({ goal: 'seo', goal_secondary: 'convert' });
  ok(both.indexOf('seo_symptom') !== -1 && both.indexOf('conv_measurement') !== -1);
  eq(R.relevantContextKeys({}).length, 0);
});

console.log('\nPrices, freshness and links\n');

t('An expired snapshot replaces prices with "See current price"', () => {
  const r = d(A({ goal: 'build', platform: 'astro', stage: 'idea', build_blocker: 'no_plan' }), STALE);
  eq(r.priceState.fresh, false);
  eq(r.primary.priceText, 'See current price');
  has(r.priceState.reason, 'days old');
});

t('An expired snapshot claims no bundle saving', () => {
  const C = R.indexCatalogue(CAT), ps = R.priceState(C, STALE);
  const b = R.bundleComparison(C, ['website-launch-system', 'seo-audit-toolkit', 'conversion-toolkit'], [], ps);
  eq(b.verdict, 'prices_unavailable');
  eq(b.difference, null);
  hasnt(b.statement, 'save');
  has(b.statement, 'out of date');
});

t('A fresh snapshot shows the verified price', () => {
  const r = d(A({ goal: 'migrate', platform: 'wordpress', stage: 'live_traffic', migrate_from: 'wordpress', migrate_to: 'shopify' }));
  eq(r.primary.priceText, '$29.99');
  eq(r.priceState.fresh, true);
});

t('Every product in the registry has the facts the result page prints', () => {
  CAT.products.forEach(p => {
    ok(p.id && p.title && p.shortName, p.handle + ' identity');
    ok(/^https:\/\/sitebuilderstack\.com\/products\//.test(p.url), p.handle + ' canonical product URL');
    ok(p.url.endsWith('/' + p.handle), p.handle + ' URL matches handle');
    eq(typeof p.price, 'number', p.handle + ' price');
    eq(p.currency, 'USD', p.handle + ' currency');
    eq(p.verifiedOn, CAT.snapshot.verifiedOn, p.handle + ' verification date');
    ok((p.benefits || []).length >= 3, p.handle + ' three benefits');
    ok((p.exclusions || []).length >= 1, p.handle + ' exclusions');
    ok(p.prerequisites && p.useCase, p.handle + ' prerequisites and use case');
  });
});

t('Every free resource points at a real sitebuilderstack.com path', () => {
  CAT.freeResources.forEach(f => {
    ok(/^https:\/\/sitebuilderstack\.com\/(pages|blogs)\//.test(f.url), f.id + ': ' + f.url);
  });
});

t('The bundle registry matches the verified contents', () => {
  const C = R.indexCatalogue(CAT);
  eq(C.bundleMembers.length, 3);
  eq(JSON.stringify(C.bundleMembers), JSON.stringify(['website-launch-system', 'seo-audit-toolkit', 'conversion-toolkit']));
  hasnt(C.byId['complete-stack'].benefits.join(' '), 'seven');
  has(C.byId['complete-stack'].exclusions.join(' '), 'does NOT include the Operations');
});

console.log('\nThe generated plan\n');

t('Actions carry what, why, deliverable and verification', () => {
  const goals = ['build', 'seo', 'convert', 'maintain', 'shopify_admin', 'migrate', 'agency'];
  const stages = { build: 'idea', seo: 'live_traffic', convert: 'live_traffic', maintain: 'live_traffic', shopify_admin: 'live_traffic', migrate: 'live_traffic', agency: 'multi_site' };
  goals.forEach(g => {
    const r = d(A({ goal: g, platform: g === 'shopify_admin' ? 'shopify' : 'wordpress', stage: stages[g], seo_symptom: 'not_indexed', conv_measurement: 'yes', maintain_checks: ['none'], admin_task: 'redirects', migrate_from: 'wordpress', migrate_to: 'astro', agency_problem: 'qa', build_blocker: 'no_plan' }));
    eq(r.actions.length, 3, g);
    r.actions.forEach((a, i) => {
      ['what', 'why', 'deliverable', 'verify'].forEach(k => ok(a[k] && a[k].length > 30, g + ' action ' + (i + 1) + ' ' + k));
      hasnt(a.what, 'improve seo');
      hasnt(a.what, 'optimize conversions');
    });
  });
});

t('The plan differs between goals', () => {
  const mk = g => JSON.stringify(d(A({ goal: g, platform: 'wordpress', stage: 'live_traffic', seo_symptom: 'not_indexed', conv_measurement: 'yes', maintain_checks: ['none'], migrate_from: 'wordpress', migrate_to: 'astro', agency_problem: 'qa' })).actions);
  const seen = {};
  ['seo', 'convert', 'maintain', 'migrate', 'agency'].forEach(g => { const k = mk(g); ok(!seen[k], g + ' duplicates another goal’s plan'); seen[k] = 1; });
});

t('The plan adapts to stage and to context inside one goal', () => {
  const idea = d(A({ goal: 'build', platform: 'astro', stage: 'idea', build_blocker: 'no_plan' }));
  const building = d(A({ goal: 'build', platform: 'astro', stage: 'building', build_blocker: 'quality' }));
  ok(JSON.stringify(idea.actions) !== JSON.stringify(building.actions));
  const notIndexed = d(A({ goal: 'seo', platform: 'astro', stage: 'live_traffic', seo_symptom: 'not_indexed' }));
  const dropped = d(A({ goal: 'seo', platform: 'astro', stage: 'live_traffic', seo_symptom: 'traffic_dropped' }));
  ok(notIndexed.actions[0].what !== dropped.actions[0].what);
});

t('The starter prompt is bounded, evidence-demanding and stops before changes', () => {
  ['build', 'seo', 'convert', 'maintain', 'shopify_admin', 'migrate', 'agency'].forEach(g => {
    const r = d(A({ goal: g, platform: g === 'shopify_admin' ? 'shopify' : 'wordpress', stage: g === 'build' ? 'idea' : (g === 'agency' ? 'multi_site' : 'live_traffic'), seo_symptom: 'not_indexed', conv_measurement: 'no', maintain_checks: ['none'], admin_task: 'catalogue_seo', migrate_from: 'wordpress', migrate_to: 'astro', agency_problem: 'qa', build_blocker: 'no_plan' }));
    const p = r.prompt.text;
    has(p, 'CONTEXT', g); has(p, 'OBJECTIVE', g); has(p, 'DISCOVERY', g);
    has(p, 'BOUNDARIES', g); has(p, 'EVIDENCE', g); has(p, 'VALIDATION', g); has(p, 'STOP HERE', g);
    has(p, 'Read and report only', g);
    has(p, 'Do not commit, push, deploy', g);
    ok(p.length > 600, g + ' prompt too short to be useful');
  });
});

t('The Shopify prompt forbids printing the access token', () => {
  const r = d(A({ goal: 'shopify_admin', platform: 'shopify', stage: 'live_traffic', admin_task: 'catalogue_seo' }));
  has(r.prompt.text, 'Never print, log or write an API access token');
});

t('The conversion prompt refuses predicted lifts and fake urgency', () => {
  const r = d(A({ goal: 'convert', platform: 'shopify', stage: 'live_traffic', conv_measurement: 'yes' }));
  has(r.prompt.text, 'Nobody can know that in advance');
  has(r.prompt.text, 'countdown timers');
});

t('Every recommendation explains itself and states a limitation', () => {
  const r = d(A({ goal: 'seo', platform: 'wordpress', stage: 'live_traffic', seo_symptom: 'indexed_no_rank' }));
  ok(r.because.length >= 3);
  has(r.because.join(' '), 'improve search visibility');
  has(r.primary.limitation, 'might not be for you yet');
  has(r.primary.freeVsPaid, 'The product adds');
  eq(r.primary.cta, 'View the complete SEO & Website Audit Toolkit');
  hasnt(JSON.stringify(r), '% match');
});

t('A free next step is always offered', () => {
  const cases = [
    A({ goal: 'build', platform: 'shopify', stage: 'idea', build_blocker: 'no_plan' }),
    A({ goal: 'seo', platform: 'wordpress', stage: 'live_traffic', seo_symptom: 'not_indexed' }),
    A({ goal: 'agency', platform: 'undecided', stage: 'multi_site', agency_problem: 'qa' }),
    A({ goal: 'shopify_admin', platform: 'shopify', stage: 'live_traffic', admin_task: 'none' }),
    { owns: [] },
  ];
  cases.forEach(c => { const r = d(c); ok(r.freeStep && r.freeStep.resource.url, JSON.stringify(c.goal)); });
});

console.log('\nThe export\n');

t('The Markdown export carries the plan, the prompt, the link and the caveat', () => {
  const r = d(A({ goal: 'migrate', platform: 'wordpress', stage: 'live_traffic', migrate_from: 'wordpress', migrate_to: 'shopify' }));
  const md = R.toMarkdown(r, CAT);
  has(md, '# Your SiteBuilderStack website action plan');
  has(md, '## Three prioritised actions');
  has(md, '## Free starter Claude Code prompt');
  has(md, '## Recommended toolkit');
  has(md, 'https://sitebuilderstack.com/products/claude-code-website-migration-replatforming-system');
  has(md, 'A free next step');
  has(md, 'self-reported answers');
  has(md, 'nothing about your website was scanned');
  has(md, 'last verified on 2026-09-24');
  hasnt(md, 'utm_');
});

t('The export of an owned-product result sells nothing', () => {
  const r = d(A({ goal: 'build', platform: 'astro', stage: 'building', build_blocker: 'stalled', owns: ['website-launch-system'] }));
  const md = R.toMarkdown(r, CAT);
  hasnt(md, '## Recommended toolkit');
  has(md, '## What you already own');
});

t('Nothing in a result contains a fabricated match score or a guarantee', () => {
  const banned = ['% match', 'guaranteed', 'guarantee ', 'risk-free', 'limited time', 'act now', 'only 3 left'];
  ['build', 'seo', 'convert', 'maintain', 'shopify_admin', 'migrate', 'agency'].forEach(g => {
    const r = d(A({ goal: g, platform: 'shopify', stage: g === 'build' ? 'idea' : 'live_traffic', seo_symptom: 'not_indexed', conv_measurement: 'yes', maintain_checks: ['none'], admin_task: 'redirects', migrate_from: 'shopify', migrate_to: 'astro', agency_problem: 'qa', build_blocker: 'no_plan' }));
    const s = JSON.stringify(r).toLowerCase();
    banned.forEach(b => { if (s.indexOf(b) !== -1) throw new Error(g + ' contains banned phrase ' + JSON.stringify(b)); });
  });
});

console.log('\n' + pass + ' passed, ' + fail + ' failed\n');
if (fail) { failures.forEach(f => console.log('  FAILED: ' + f)); process.exit(1); }
