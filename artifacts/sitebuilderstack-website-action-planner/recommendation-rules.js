/* recommendation-rules.js — the SiteBuilderStack Website Action Planner's
 * decision engine.
 *
 * Pure functions over a plain answers object. No DOM, no network, no storage,
 * no timers. The interface in index.html renders whatever this returns; the
 * Node test suite in tests/test-rules.js exercises it directly. If a routing
 * decision is not expressible here, it does not belong in the UI.
 *
 * The catalogue is passed in (products.json) rather than imported, so the
 * same engine runs against a stale snapshot, a refreshed one, or a fixture.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.SBS_RULES = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* ------------------------------------------------------------------ *
   * Vocabulary. These ids are the contract with the UI and the tests.
   * ------------------------------------------------------------------ */
  var GOALS = [
    ['build', 'Build or launch a website'],
    ['seo', 'Improve search visibility'],
    ['convert', 'Turn existing traffic into more leads or sales'],
    ['maintain', 'Maintain a live website'],
    ['shopify_admin', 'Automate Shopify administration'],
    ['migrate', 'Migrate to another platform'],
    ['agency', 'Improve client-project delivery'],
  ];
  var PLATFORMS = [
    ['shopify', 'Shopify'],
    ['wordpress', 'WordPress / WooCommerce'],
    ['astro', 'Astro or another code-based website'],
    ['saas', 'SaaS / custom web application'],
    ['undecided', 'Other / not decided'],
  ];
  var STAGES = [
    ['idea', 'Idea or planning'],
    ['building', 'Building, but not live'],
    ['live_no_traffic', 'Live, with little or no traffic'],
    ['live_traffic', 'Live, receiving traffic'],
    ['multi_site', 'Operating several websites or client projects'],
  ];
  var READINESS = [
    ['using', 'I already use Claude Code'],
    ['access_help', 'I have access but need help getting started'],
    ['exploring', 'Exploring — not comfortable with a terminal yet'],
  ];

  /* Goal → the product that answers it, before any qualification. */
  var GOAL_PRODUCT = {
    build: 'website-launch-system',
    seo: 'seo-audit-toolkit',
    convert: 'conversion-toolkit',
    maintain: 'operations-system',
    shopify_admin: 'shopify-automation',
    migrate: 'migration-system',
    agency: 'agency-system',
  };

  /* Contextual questions, and the goals that make each one relevant. */
  var CONTEXT = {
    build_blocker: {
      goals: ['build'],
      question: 'What is actually in the way right now?',
      options: [
        ['no_plan', 'There is no written plan or structure yet'],
        ['stalled', 'The build has stalled or keeps being rewritten'],
        ['quality', 'It builds, but I do not trust the quality'],
        ['notsure', 'Not sure'],
      ],
    },
    seo_symptom: {
      goals: ['seo'],
      question: 'Which of these is closest to what you are seeing?',
      options: [
        ['not_indexed', 'Pages are not in the index, or are indexed slowly'],
        ['indexed_no_rank', 'Pages are indexed but rank for nothing'],
        ['traffic_dropped', 'Search traffic dropped'],
        ['never_audited', 'Nothing obvious — it has just never been audited'],
        ['notsure', 'Not sure'],
      ],
    },
    conv_measurement: {
      goals: ['convert'],
      question: 'Is traffic measured, and is the main conversion tracked?',
      options: [
        ['yes', 'Yes — analytics is installed and the conversion event fires'],
        ['partial', 'Analytics is installed, but I do not trust the conversion number'],
        ['no', 'No conversion tracking'],
        ['notsure', 'Not sure'],
      ],
    },
    maintain_checks: {
      goals: ['maintain'],
      multi: true,
      question: 'Which routine checks are already in place?',
      options: [
        ['backups', 'Backups — and a restore has been tested'],
        ['monitoring', 'Uptime, TLS and certificate monitoring'],
        ['updates', 'A dependency / plugin update cadence'],
        ['deploy_gate', 'A check that runs on both sides of a deploy'],
        ['none', 'None of these'],
        ['notsure', 'Not sure'],
      ],
      exclusive: ['none', 'notsure'],
    },
    admin_task: {
      goals: ['shopify_admin'],
      question: 'Which repetitive administrative task is the problem?',
      options: [
        ['catalogue_seo', 'Product titles, descriptions, SEO fields or alt text at scale'],
        ['collections_metafields', 'Collections, metafields or metaobjects'],
        ['inventory_pricing', 'Inventory, variants or pricing across many products'],
        ['redirects', 'Redirects and URL clean-up'],
        ['reporting', 'Exports, audits and catalogue reporting'],
        ['none', 'None — I am on Shopify, but bulk admin is not my problem'],
        ['notsure', 'Not sure'],
      ],
    },
    migrate_from: {
      goals: ['migrate'],
      question: 'What are you moving from?',
      options: [
        ['wordpress', 'WordPress'],
        ['shopify', 'Shopify'],
        ['hosted_builder', 'Wix, Squarespace or another hosted builder'],
        ['custom', 'A custom or static site'],
        ['notsure', 'Not sure yet'],
      ],
    },
    migrate_to: {
      goals: ['migrate'],
      question: 'What are you moving to?',
      options: [
        ['shopify', 'Shopify'],
        ['wordpress', 'WordPress'],
        ['astro', 'Astro or another code-based site'],
        ['saas', 'A custom application'],
        ['same_platform', 'The same platform — new host, theme or domain'],
        ['notsure', 'Not decided'],
      ],
    },
    agency_problem: {
      goals: ['agency'],
      question: 'Where does client work usually go wrong for you?',
      options: [
        ['scoping', 'Scoping and estimating'],
        ['qa', 'Review and QA before the client sees it'],
        ['handoff', 'Handoff and documentation'],
        ['reporting', 'Reporting and retention afterwards'],
        ['notsure', 'Not sure — all of it feels ad hoc'],
      ],
    },
  };

  /* ------------------------------------------------------------------ *
   * Small helpers
   * ------------------------------------------------------------------ */
  function label(pairs, id) {
    for (var i = 0; i < pairs.length; i++) if (pairs[i][0] === id) return pairs[i][1];
    return '';
  }
  function goalLabel(id) { return label(GOALS, id); }
  function platformLabel(id) { return label(PLATFORMS, id); }
  function stageLabel(id) { return label(STAGES, id); }
  function readinessLabel(id) { return label(READINESS, id); }
  function contextLabel(key, id) {
    var c = CONTEXT[key];
    return c ? label(c.options, id) : '';
  }
  function money(n) { return Math.round(n * 100) / 100; }
  function fmt(n, currency) {
    var s = money(n).toFixed(2);
    return (currency === 'USD' ? '$' : (currency || '') + ' ') + s;
  }
  function uniq(a) { var o = [], s = {}; a.forEach(function (x) { if (x && !s[x]) { s[x] = 1; o.push(x); } }); return o; }
  function arr(v) { return Array.isArray(v) ? v : (v === undefined || v === null || v === '' ? [] : [v]); }

  /* ------------------------------------------------------------------ *
   * Catalogue
   * ------------------------------------------------------------------ */
  function indexCatalogue(cat) {
    var by = {};
    (cat.products || []).forEach(function (p) { by[p.id] = p; });
    var bundleKey = Object.keys(cat.bundles || {})[0] || null;
    return {
      raw: cat,
      byId: by,
      bundleProductId: 'complete-stack',
      bundleMembers: bundleKey ? cat.bundles[bundleKey].members.slice() : [],
      bundleNote: bundleKey ? cat.bundles[bundleKey].note : '',
      free: cat.freeResources || [],
      snapshot: cat.snapshot || {},
    };
  }
  function freeById(C, id) {
    for (var i = 0; i < C.free.length; i++) if (C.free[i].id === id) return C.free[i];
    return null;
  }

  /* Price freshness. After the window, exact prices and savings are replaced
     with "See current price" — the store stays the authority. */
  function priceState(C, today) {
    var s = C.snapshot || {};
    if (!s.verifiedOn) return { fresh: false, ageDays: null, reason: 'no verification date in the snapshot' };
    var v = Date.parse(s.verifiedOn + 'T00:00:00Z');
    var t = Date.parse((today || isoToday()) + 'T00:00:00Z');
    if (isNaN(v) || isNaN(t)) return { fresh: false, ageDays: null, reason: 'unreadable verification date' };
    var age = Math.floor((t - v) / 86400000);
    var win = s.freshnessWindowDays || 30;
    return {
      fresh: age >= 0 && age <= win,
      ageDays: age,
      windowDays: win,
      verifiedOn: s.verifiedOn,
      reason: age > win ? 'snapshot is ' + age + ' days old (window ' + win + ')' : (age < 0 ? 'verification date is in the future' : ''),
    };
  }
  function isoToday() { return new Date().toISOString().slice(0, 10); }

  function priceText(C, product, ps) {
    if (!product) return '';
    if (!ps.fresh || product.availableOnDate !== true || typeof product.price !== 'number') return 'See current price';
    return fmt(product.price, product.currency);
  }

  /* ------------------------------------------------------------------ *
   * Which questions apply, given the answers so far
   * ------------------------------------------------------------------ */
  function activeGoals(a) {
    return uniq([a.goal, a.goal_secondary]).filter(function (g) { return g && g !== 'none' && GOAL_PRODUCT[g]; });
  }
  function relevantContextKeys(a) {
    var gs = activeGoals(a), out = [];
    Object.keys(CONTEXT).forEach(function (k) {
      if (CONTEXT[k].goals.some(function (g) { return gs.indexOf(g) !== -1; })) out.push(k);
    });
    return out;
  }
  /* Answers to questions that no longer apply are dropped before anything
     reads them, so a changed earlier answer cannot leak into the result. */
  function normalize(answers) {
    var a = {};
    ['goal', 'goal_secondary', 'platform', 'stage', 'readiness'].forEach(function (k) {
      if (answers[k]) a[k] = answers[k];
    });
    if (a.goal_secondary === a.goal) delete a.goal_secondary;
    var keep = relevantContextKeys(a);
    keep.forEach(function (k) {
      if (answers[k] === undefined || answers[k] === null || answers[k] === '') return;
      a[k] = CONTEXT[k].multi ? arr(answers[k]).slice() : answers[k];
    });
    var owns = arr(answers.owns);
    if (owns.indexOf('none') !== -1) owns = ['none'];
    else if (owns.indexOf('notsure') !== -1) owns = ['notsure'];
    a.owns = owns;
    return a;
  }
  function ownedIds(a) {
    return a.owns.filter(function (x) { return x !== 'none' && x !== 'notsure'; });
  }
  /* Owning the bundle means owning its three members. */
  function expandOwned(C, ids) {
    var out = ids.slice();
    if (ids.indexOf(C.bundleProductId) !== -1) out = out.concat(C.bundleMembers);
    return uniq(out);
  }

  /* ------------------------------------------------------------------ *
   * Qualification. Runs before ranking, as the brief requires.
   * Each gate returns a note the result page prints verbatim, so the
   * visitor can see why they were routed where they were.
   * ------------------------------------------------------------------ */
  function qualify(a) {
    var notes = [], flags = {}, live = a.stage === 'live_no_traffic' || a.stage === 'live_traffic' || a.stage === 'multi_site';
    var route = {};   // goal id → replacement goal id
    var gs = activeGoals(a);

    gs.forEach(function (g) {
      if (g === 'convert') {
        if (a.stage === 'idea' || a.stage === 'building') {
          route.convert = 'build';
          flags.convert_not_live = true;
          notes.push('Conversion work needs a site that is live and receiving traffic. Yours is not live yet, so the plan below finishes the build first.');
        } else if (a.stage === 'live_no_traffic') {
          route.convert = 'seo';
          flags.convert_no_traffic = true;
          notes.push('You said the site is live with little or no traffic. Optimising conversion before anyone arrives changes a percentage of almost nothing, so the plan below works on discovery first.');
        }
      }
      if (g === 'seo' && (a.stage === 'idea' || a.stage === 'building')) {
        route.seo = 'build';
        flags.seo_before_launch = true;
        notes.push('An audit needs something to audit. Until the site is live, the search work belongs inside the build rather than in a separate audit pass.');
      }
      if (g === 'maintain' && (a.stage === 'idea' || a.stage === 'building')) {
        route.maintain = 'build';
        flags.maintain_not_live = true;
        notes.push('There is nothing in production to maintain yet, so the plan below gets you to a launch you can then operate.');
      }
      if (g === 'migrate' && a.stage === 'idea') {
        flags.migrate_nothing_yet = true;
        notes.push('You selected a migration from the planning stage. If there is no existing site with URLs worth preserving, this is a build rather than a migration — say so by changing the stage answer.');
      }
      if (g === 'shopify_admin') {
        if (a.platform && a.platform !== 'shopify') {
          delete route.shopify_admin;
          flags.shopify_admin_wrong_platform = true;
          notes.push('Shopify administration was selected, but the platform answer is ' + platformLabel(a.platform) + '. The Admin API toolkit only applies to a Shopify store, so it is not recommended here.');
        } else if (a.admin_task === 'none') {
          flags.shopify_admin_no_task = true;
          notes.push('Being on Shopify is not on its own a reason to automate it. You said bulk administration is not the problem, so no automation product is recommended.');
        } else if (a.admin_task === 'notsure') {
          flags.shopify_admin_task_unknown = true;
          notes.push('You were not sure which administrative task is the problem. The first action below names it before anything is bought.');
        }
      }
    });

    /* "Agency" is an engagement problem, not a project. If a real project
       problem was also stated, that project leads and the agency system
       supports it. */
    if (a.goal === 'agency' && a.goal_secondary && a.goal_secondary !== 'agency') {
      flags.agency_defers = true;
      notes.push('You lead with client delivery and also named ' + goalLabel(a.goal_secondary).toLowerCase() + '. The delivery system organises the engagement; it does not do the project work, so the project problem is treated as the primary one.');
    }

    if (a.readiness === 'exploring') {
      flags.not_ready = true;
      notes.push('You said you are not comfortable with a terminal yet. Every paid product here is a set of workflows you run inside Claude Code, so the plan below starts with a free path to get there.');
    }

    if (!live && a.stage === 'multi_site') live = true;
    return { notes: notes, flags: flags, route: route, live: live };
  }

  /* Apply the routing table to a goal. */
  function routed(q, g) { return q.route[g] || g; }

  /* ------------------------------------------------------------------ *
   * Product selection
   * ------------------------------------------------------------------ */
  function selectProducts(a, q) {
    var primaryGoal = a.goal, secondaryGoal = a.goal_secondary;
    if (q.flags.agency_defers) { primaryGoal = a.goal_secondary; secondaryGoal = 'agency'; }

    var pg = primaryGoal ? routed(q, primaryGoal) : null;
    var sg = secondaryGoal ? routed(q, secondaryGoal) : null;
    if (sg === pg) sg = null;

    var primary = pg ? GOAL_PRODUCT[pg] : null;
    var secondary = sg ? GOAL_PRODUCT[sg] : null;

    /* Gates that remove a product entirely. */
    if (q.flags.shopify_admin_wrong_platform || q.flags.shopify_admin_no_task) {
      if (primary === 'shopify-automation') { primary = secondary; secondary = null; }
      if (secondary === 'shopify-automation') secondary = null;
    }
    if (secondary === primary) secondary = null;
    return { primaryGoal: pg, secondaryGoal: sg, primary: primary, secondary: secondary, statedGoal: a.goal, statedSecondary: a.goal_secondary };
  }

  /* ------------------------------------------------------------------ *
   * Bundle arithmetic. Always computed, never assumed.
   * `selected` is the set of bundle members the visitor's answers justify,
   * or the set they ticked in the on-demand comparison.
   * ------------------------------------------------------------------ */
  function bundleComparison(C, selectedIds, owned, ps) {
    var bundle = C.byId[C.bundleProductId];
    var members = C.bundleMembers;
    var want = members.filter(function (id) { return selectedIds.indexOf(id) !== -1; });
    var need = want.filter(function (id) { return owned.indexOf(id) === -1; });
    var alreadyOwned = members.filter(function (id) { return owned.indexOf(id) !== -1; });
    var out = {
      bundleProduct: bundle || null,
      members: members.slice(),
      selected: want,
      unowned: need,
      ownedMembers: alreadyOwned,
      bundlePrice: bundle ? bundle.price : null,
      individualTotal: null,
      difference: null,
      verdict: 'not_applicable',
      pricesUsable: !!(ps.fresh && bundle && bundle.availableOnDate === true),
      statement: '',
    };
    if (owned.indexOf(C.bundleProductId) !== -1) {
      out.verdict = 'already_owned';
      out.statement = 'You already own the Complete Site Builder Stack, so all three of its products are yours. Nothing to buy.';
      return out;
    }
    if (!out.pricesUsable) {
      out.verdict = need.length >= 2 ? 'prices_unavailable' : 'not_applicable';
      out.statement = need.length >= 2
        ? 'The price snapshot in this planner is out of date, so no saving is claimed. Open the bundle page and the individual product pages and compare the current prices yourself.'
        : '';
      return out;
    }
    var total = 0;
    need.forEach(function (id) { var p = C.byId[id]; if (p && typeof p.price === 'number') total += p.price; });
    out.individualTotal = money(total);
    out.difference = money(out.individualTotal - bundle.price);

    if (need.length === 0) {
      out.verdict = 'not_applicable';
      out.statement = alreadyOwned.length ? 'You already own everything in the bundle that your answers point to.' : '';
      return out;
    }
    if (need.length === 1) {
      out.verdict = 'single_product';
      out.statement = 'Your answers point to one product in the bundle. Buying it on its own costs ' + fmt(out.individualTotal, bundle.currency) +
        '; the bundle is ' + fmt(bundle.price, bundle.currency) + '. Buying the bundle for one product costs ' + fmt(bundle.price - out.individualTotal, bundle.currency) + ' more.';
      return out;
    }
    if (out.difference > 0) {
      out.verdict = 'bundle_cheaper';
      out.statement = need.length + ' of the bundle’s 3 products individually: ' + fmt(out.individualTotal, bundle.currency) +
        '. The bundle: ' + fmt(bundle.price, bundle.currency) + '. That is ' + fmt(out.difference, bundle.currency) + ' less' +
        (alreadyOwned.length ? ', though it re-delivers ' + alreadyOwned.length + ' product you already own.' : ' and includes the third product as well.');
    } else if (out.difference < 0) {
      out.verdict = 'individual_cheaper';
      out.statement = need.length + ' of the bundle’s 3 products individually: ' + fmt(out.individualTotal, bundle.currency) +
        '. The bundle: ' + fmt(bundle.price, bundle.currency) + '. Buying the two you named is ' + fmt(-out.difference, bundle.currency) +
        ' cheaper. The bundle adds the third product for the difference — worth it only if you will actually use it.';
    } else {
      out.verdict = 'equal';
      out.statement = 'The products you named cost the same individually as the bundle (' + fmt(bundle.price, bundle.currency) +
        '). The bundle includes a third product you did not ask for; that is the only difference.';
    }
    if (alreadyOwned.length && out.verdict !== 'bundle_cheaper') {
      out.statement += ' You already own ' + alreadyOwned.length + ' of the three, and the bundle would deliver ' + (alreadyOwned.length === 1 ? 'it' : 'them') + ' again.';
    }
    return out;
  }

  /* ------------------------------------------------------------------ *
   * Actions. Three per result: what / why / deliverable / verify.
   * Every branch below is reachable from the questionnaire.
   * ------------------------------------------------------------------ */
  var PLATFORM_NOUN = {
    shopify: 'Shopify store', wordpress: 'WordPress site', astro: 'Astro site',
    saas: 'application', undecided: 'site',
  };
  function pn(a) { return PLATFORM_NOUN[a.platform] || 'site'; }

  function actionsFor(a, sel, q) {
    var g = sel.primaryGoal, A;
    if (q.flags.not_ready) return actionsGettingStarted(a);
    switch (g) {
      case 'build': A = actionsBuild(a, q); break;
      case 'seo': A = actionsSeo(a); break;
      case 'convert': A = actionsConvert(a); break;
      case 'maintain': A = actionsMaintain(a); break;
      case 'shopify_admin': A = actionsShopify(a, q); break;
      case 'migrate': A = actionsMigrate(a); break;
      case 'agency': A = actionsAgency(a); break;
      default: A = actionsUnclear(a); break;
    }
    return A.slice(0, 3);
  }

  function actionsGettingStarted(a) {
    return [
      {
        what: 'Install Claude Code and open it once in the folder that holds your ' + pn(a) + ' project (or an empty folder if there is nothing yet).',
        why: 'Every paid workflow on SiteBuilderStack is a prompt you run inside Claude Code. Until it opens and reads a directory, none of them can help you.',
        deliverable: 'A terminal session where Claude Code starts and lists the files it can see.',
        verify: 'Ask it "list the files in this project and tell me what kind of project this is" and check the answer matches reality.',
      },
      {
        what: 'Run one read-only task and nothing else: ask Claude Code to describe what the project does, and explicitly tell it to change no files.',
        why: 'The first thing to learn is that a good session is bounded. A tool that only reads cannot break anything, so it is the safe place to build confidence.',
        deliverable: 'A written description of your project produced without a single file being modified.',
        verify: 'Run `git status` (or look at the folder’s modified dates). Nothing should have changed.',
      },
      {
        what: 'Write a short CLAUDE.md in the project root: what the project is, the commands to build and test it, and two or three things that must never be done.',
        why: 'A memory file is what turns a general assistant into one that knows your project. It is also the single highest-leverage free thing you can do before buying any workflow.',
        deliverable: 'A CLAUDE.md of under a page that a new session reads automatically.',
        verify: 'Start a fresh session and ask "what are the rules for this project?" — it should answer from the file, not from guesswork.',
      },
    ];
  }

  function actionsBuild(a, q) {
    var noun = pn(a);
    if (a.stage === 'idea' || !a.stage) {
      return [
        {
          what: 'Write a one-page brief and a URL map before any code is generated: the pages, their addresses, and what each one is for.',
          why: 'Asked to "build a website", Claude Code will build a different one each time. A URL map is the smallest artefact that makes the output repeatable' + (a.platform === 'undecided' ? ' — and it is also how you find out which platform you actually need.' : '.'),
          deliverable: 'A brief plus a table of every intended URL with its purpose and its primary content.',
          verify: 'Read the map back and check that no page exists twice under two addresses, and that every page has a reason to exist.',
        },
        {
          what: 'Create CLAUDE.md in the repository root with the stack, the build/test/deploy commands, the coding standards, and an explicit list of things that must never be done.',
          why: 'Constraints stated once in a memory file are applied on every later turn. Constraints stated in chat are forgotten at the next session.',
          deliverable: 'A CLAUDE.md under a page long, with every command in it actually runnable.',
          verify: 'Run each command the file names. If one fails or does not exist, the file is already lying to the model.',
        },
        a.platform === 'undecided' ? {
          what: 'Decide the platform against the brief, not against preference: who edits the content, whether you need a checkout, and what you are willing to maintain in two years.',
          why: 'Platform choice determines the whole build system. Choosing it after the first thousand lines exist is a rewrite.',
          deliverable: 'A one-paragraph decision naming the platform and the two constraints that decided it.',
          verify: 'Write down the scenario that would make the decision wrong. If you cannot, you have not compared anything.',
        } : {
          what: 'Set up the repository and the deployment path before the first feature: a git repository, a branch you do not deploy from directly, and a build that runs in CI.',
          why: 'A ' + noun + ' that has never been deployed is not "nearly done". The first deploy finds the problems, and finding them on day one is cheap.',
          deliverable: 'A repository with CI running the build on every push, and one successful deploy to a preview URL.',
          verify: 'Push a deliberate syntax error on a branch. CI must fail. Then remove it.',
        },
      ];
    }
    if (a.stage === 'building') {
      return [
        {
          what: 'Put a gate in front of the build: the project’s build, lint and tests must run and pass before anything is deployed.',
          why: a.build_blocker === 'quality'
            ? 'You said you do not trust the quality of what is being generated. A gate converts that feeling into a specific, repeatable check that either passes or does not.'
            : 'Generated code is fast to produce and slow to review. A gate is what stops speed becoming an outage.',
          deliverable: 'A CI workflow that fails the pipeline on a build, lint or test failure.',
          verify: 'Break one test on a branch on purpose and confirm the pipeline goes red before the deploy step runs.',
        },
        {
          what: 'Run a read-only audit of what has been generated so far against the brief, with an explicit instruction to change nothing and report findings with file and line.',
          why: a.build_blocker === 'stalled'
            ? 'A build that keeps being rewritten usually has no agreed definition of done. An audit against the brief produces that definition as a list.'
            : 'An audit that fixes as it goes leaves a diff across thirty files and no record of what was actually wrong.',
          deliverable: 'A findings list: file, line, what was expected, what is there, severity.',
          verify: 'Confirm `git status` is clean after the audit. If files changed, the audit was not read-only and the findings cannot be trusted.',
        },
        {
          what: 'Work the pre-launch list on the ' + noun + ' while it is still cheap: canonical URLs, robots, redirects, form delivery, a real 404, and analytics that fires once rather than twice.',
          why: 'Every one of these is a five-minute fix before launch and a three-week investigation afterwards.',
          deliverable: 'A checklist with an observed value beside each line, not a tick.',
          verify: 'Fetch the production HTML for two pages and read the head. Do not take the template’s word for it.',
        },
      ];
    }
    /* Live already, but the stated goal is build/relaunch quality. */
    return [
      {
        what: 'Run a read-only audit of the live ' + noun + ' first: rendered head tags, status codes, forms, and the pages that actually get traffic.',
        why: 'Rebuilding before you know what the current site does well is how a relaunch loses traffic it used to have.',
        deliverable: 'A baseline report of the current site: URLs, titles, status codes, and anything already broken.',
        verify: 'Spot-check three URLs from the report by hand. The report and the browser must agree.',
      },
      {
        what: 'Write CLAUDE.md for the existing repository, including the commands that already work and the parts of the codebase that must not be touched.',
        why: 'On an existing project the highest-value memory content is the prohibitions — the things a confident model will otherwise happily rewrite.',
        deliverable: 'A CLAUDE.md that a new session reads before it proposes anything.',
        verify: 'Ask a fresh session to describe the project’s constraints and compare the answer with the file.',
      },
      {
        what: 'Rehearse the rollback before you change anything on production.',
        why: 'A relaunch is a deploy with more surface area. The question is never whether something breaks, only how long it stays broken.',
        deliverable: 'Written rollback steps, as exact commands, with the way to confirm the rollback worked.',
        verify: 'Execute the rollback on a preview environment and confirm the old version serves.',
      },
    ];
  }

  function actionsSeo(a) {
    var s = a.seo_symptom || 'notsure';
    var noun = pn(a);
    var first;
    if (s === 'not_indexed') {
      first = {
        what: 'Take three URLs that are not indexed and read the rendered HTML Google would see: status code, robots meta, X-Robots-Tag, canonical target, and whether the content is in the HTML or only after JavaScript.',
        why: 'Most "not indexed" cases are one of five mechanical causes, and all five are visible in the response. Guessing at content quality before checking them wastes weeks.',
        deliverable: 'A table: URL, status, robots directive, canonical, content-in-HTML yes/no.',
        verify: 'Fetch each URL with a plain HTTP client, not a browser with your session. A 200 in your browser and a 404 for a crawler is a common and invisible failure.',
      };
    } else if (s === 'indexed_no_rank') {
      first = {
        what: 'Export the queries and pages that already get impressions from Search Console, and sort by impressions with a click-through rate near zero.',
        why: 'Pages with impressions and no clicks are the cheapest work on the site: search already shows them, so the gap is the title, the description or the intent match.',
        deliverable: 'A list of the ten pages with the most impressions and the worst click-through rate.',
        verify: 'For each one, read the query it ranks for and the page’s title. If the title does not contain the thing the query asked for, you have found the problem.',
      };
    } else if (s === 'traffic_dropped') {
      first = {
        what: 'Fix the date the drop began, then list every change made to the ' + noun + ' in the two weeks before it — deploys, redirects, canonical or template changes, plugin or theme updates.',
        why: 'A drop with a sharp edge is almost always a change, not an algorithm. The date narrows the suspect list to something you can actually read.',
        deliverable: 'The drop date from Search Console, and a dated change log beside it.',
        verify: 'Compare the rendered head of an affected URL against an archived copy from before the date.',
      };
    } else {
      first = {
        what: 'Run a crawlability and indexability audit of the live ' + noun + ' in read-only mode: robots.txt, sitemap contents versus real URLs, status codes, redirect chains, and canonical targets.',
        why: 'These come first because everything else depends on them. Optimising a title on a URL that is about to be canonicalised away is wasted work.',
        deliverable: 'A findings report with the URL, the observed value and why it matters for each issue.',
        verify: 'Confirm no files were changed during the audit, and re-fetch two of the reported URLs by hand to check the observation.',
      };
    }
    return [
      first,
      {
        what: 'Check that the sitemap and the canonical tags agree with each other and with reality: every URL in the sitemap returns 200 and is self-canonical, and no canonical points at a redirect.',
        why: 'Contradictory signals are resolved by the search engine, not by you, and it usually resolves them the way you did not want.',
        deliverable: 'A list of every sitemap URL with its status code and its canonical target.',
        verify: 'The count of sitemap URLs and the count of 200-and-self-canonical URLs should match. Where they do not, that difference is the work.',
      },
      {
        what: 'Add internal links to the pages you care about from the pages that already get crawled — from within the body copy, with the wording a reader would use.',
        why: 'An orphaned page with no internal links is one a crawler has little reason to prioritise, however good it is. Internal links are the one ranking input entirely under your control.',
        deliverable: 'Three to five new contextual links per target page, from pages with existing impressions.',
        verify: 'Re-crawl and confirm each target page is reachable from the homepage in three clicks or fewer.',
      },
    ];
  }

  function actionsConvert(a) {
    var m = a.conv_measurement || 'notsure';
    var noun = pn(a);
    var unknown = (m === 'no' || m === 'notsure' || m === 'partial');
    var first = unknown ? {
      what: 'Before any diagnosis: verify the conversion event. Complete the action yourself and confirm the event fires exactly once, with the right value, and does not fire on page load or on a back-button return.',
      why: m === 'no'
        ? 'You said there is no conversion tracking. Any conclusion about where visitors are lost would be invented, so measurement is the first piece of work, not the second.'
        : 'A conversion event that fires twice makes every number in the funnel wrong in the same direction, and nothing about the report looks unusual.',
      deliverable: 'A short note: which event, fired from where, observed once per completed action, with the value it carried.',
      verify: 'Do the conversion action three times in a private window and count three events. Then load the confirmation page directly and confirm no event fires.',
    } : {
      what: 'Build the funnel with real numbers: every step from landing to completed conversion, with the count at each step and the drop between them.',
      why: 'The biggest absolute drop is not always the biggest opportunity, but you cannot tell which is which until the steps are counted rather than assumed.',
      deliverable: 'A table of funnel steps with counts and step-to-step drop-off for the last 28 days.',
      verify: 'The top of the funnel should reconcile with your sessions figure. If it does not, the funnel definition is wrong before you interpret it.',
    };
    return [
      first,
      {
        what: 'Functionally test the thing you are asking visitors to do on the ' + noun + ': submit the form or complete the checkout yourself, on a phone, and confirm the submission actually arrives.',
        why: 'A meaningful share of "conversion problems" are delivery problems. A form that posts to nothing looks identical to a form nobody wanted to fill in.',
        deliverable: 'A marked test submission confirmed received, with the date and the route it arrived by.',
        verify: 'Check the destination inbox or the orders list, not the on-page success message. The success message proves the JavaScript ran, nothing more.',
      },
      {
        what: 'Pick one change from the evidence, define what "it worked" means before you ship it, and change one thing.',
        why: 'Shipping five changes at once on ' + (a.stage === 'live_traffic' ? 'a site with traffic' : 'a live site') + ' means learning nothing from any of them.',
        deliverable: 'A one-line hypothesis: the step, the change, the metric, and the number that would count as a result.',
        verify: 'After the change, compare the same metric over the same length of period. If the traffic is too small to separate the change from noise, record that honestly rather than claiming a lift.',
      },
    ];
  }

  function actionsMaintain(a) {
    var have = arr(a.maintain_checks);
    var has = function (k) { return have.indexOf(k) !== -1; };
    var noun = pn(a);
    var list = [];
    if (!has('backups')) {
      list.push({
        what: 'Restore a backup into a throwaway environment and open the restored site.',
        why: 'A backup nobody has restored is a hypothesis. The failure is nearly always discovered on the day it matters.',
        deliverable: 'A restored copy you have actually looked at, and a note of how long the restore took.',
        verify: 'Check the restored copy contains content created in the last week. A backup job that has been silently failing still produces a file.',
      });
    }
    if (!has('monitoring')) {
      list.push({
        what: 'Take an outside baseline of the ' + noun + ': HTTP status and redirect chain, TLS certificate expiry, DNS records as they are today, and the security headers actually served.',
        why: 'Operations starts with knowing the current state. Certificates that stop auto-renewing and DNS that nobody wrote down are the two classic silent failures.',
        deliverable: 'One baseline report, dated, that you can diff against next month.',
        verify: 'Confirm the certificate expiry date and set a calendar reminder two weeks before it.',
      });
    }
    if (!has('deploy_gate')) {
      list.push({
        what: 'Put a check on both sides of every deploy: the build and tests before, and a smoke check of the live URLs after.',
        why: 'The expensive outages are the ones where the deploy succeeded. A post-deploy check is what turns "it deployed" into "it works".',
        deliverable: 'A pre-deploy gate in CI and a post-deploy script that fetches the key URLs and checks status and one string on each.',
        verify: 'Deploy a harmless change and watch both run. Then make the post-deploy check fail on purpose and confirm you find out.',
      });
    }
    if (!has('updates')) {
      list.push({
        what: 'Establish an update cadence: list the dependencies, plugins or themes in use with their current and latest versions, and set a fixed day for applying them behind the gate.',
        why: 'A plugin two majors behind with a published exploit is the most common way a small site is compromised, and it never announces itself.',
        deliverable: 'A dated dependency inventory with a known-vulnerability column.',
        verify: 'Apply one update on a branch, watch the gate run, and confirm the rollback path still works.',
      });
    }
    if (!list.length) {
      list = [
        {
          what: 'Turn the checks you already run into one scheduled report with a score, so a change in the trend is visible without reading four dashboards.',
          why: 'You have the individual checks. What is usually missing is the one page that says whether this month is worse than last month.',
          deliverable: 'A monthly operations report: uptime, certificate status, dependency drift, backup restore date, deploy count, incidents.',
          verify: 'Produce two consecutive months and confirm you can see the difference without interpretation.',
        },
        {
          what: 'Write the incident procedure while nothing is on fire: who is called, where the rollback command lives, and what is checked first.',
          why: 'The decisions made at 18:00 on a Friday are worse than the same decisions made now.',
          deliverable: 'A one-page incident playbook with exact commands.',
          verify: 'Hand it to someone who does not maintain the site and ask them to follow step one.',
        },
        {
          what: 'Re-test the restore. Set a recurring date for it.',
          why: 'A restore that worked in March proves nothing about the backup taken last night.',
          deliverable: 'A dated restore record.',
          verify: 'The restored copy contains this week’s content.',
        },
      ];
    }
    return list;
  }

  function actionsShopify(a, q) {
    var t = a.admin_task || 'notsure';
    var TASK = {
      catalogue_seo: 'product titles, descriptions, SEO fields and alt text',
      collections_metafields: 'collections, metafields and metaobjects',
      inventory_pricing: 'inventory, variants and pricing',
      redirects: 'redirects and URL clean-up',
      reporting: 'catalogue exports, audits and reporting',
      notsure: 'the catalogue work that keeps coming back',
    };
    var task = TASK[t] || TASK.notsure;
    var first = (t === 'notsure' || q.flags.shopify_admin_task_unknown) ? {
      what: 'Name the task before automating anything: write down the last three admin jobs that took more than an hour, how many products each touched, and how often they recur.',
      why: 'Automation is worth it when the work is repetitive, large and recurring. Two of those three is usually a case for doing it by hand once more.',
      deliverable: 'Three named tasks with a product count and a frequency beside each.',
      verify: 'If the largest one touches fewer than about fifty products and happens once a year, the honest answer is that no toolkit is needed.',
    } : {
      what: 'Export the current state of ' + task + ' to a file before touching anything, through the Admin API rather than by hand.',
      why: 'The export is the rollback. A bulk mutation with no export to return to is the single most expensive mistake available in a Shopify admin.',
      deliverable: 'A dated export file covering every product or object the change will touch.',
      verify: 'Open the export and confirm the row count matches the catalogue count in the admin. A silently truncated export is worse than none.',
    };
    return [
      first,
      {
        what: 'Audit the export against explicit rules before writing: what a correct value looks like for ' + task + ', and which records fail that rule.',
        why: 'An audit that reads from a file cannot damage the store, and it turns a vague "the catalogue is a mess" into a countable list.',
        deliverable: 'A list of failing records with the current value and the rule it breaks.',
        verify: 'Pick three failures at random and confirm them in the Shopify admin by hand.',
      },
      {
        what: 'Apply the change to a single product first, read the value back from the API, and only then run the batch.',
        why: 'A preview, a backup and a read-back after every write is the difference between an automated catalogue and a thousand wrong titles by lunchtime.',
        deliverable: 'One product changed, its value read back and confirmed, and the batch script ready but not yet run.',
        verify: 'Read the changed product back through the API, not from the script’s own log. Then check it on the storefront.',
      },
    ];
  }

  function actionsMigrate(a) {
    var from = contextLabel('migrate_from', a.migrate_from) || 'the current platform';
    var to = a.migrate_to === 'same_platform' ? 'the new host or theme' : (contextLabel('migrate_to', a.migrate_to) || 'the destination');
    return [
      {
        what: 'Inventory every URL on the existing site before anything is built: address, status code, title, canonical, and whether it has traffic or inbound links.',
        why: 'Most of what a migration loses was never on anyone’s list. The inventory is the list, and it can only be made while the old site is still up.',
        deliverable: 'One row per URL, exported to a file, taken from a crawl plus Search Console rather than from memory.',
        verify: 'Compare the crawl count with the sitemap count and with Search Console’s indexed count. Three different numbers is normal; understanding why is the point.',
      },
      {
        what: 'Map old URL to new URL for every row, decide explicitly what is being dropped, and test the redirects return a single 301 to a 200.',
        why: 'Redirecting everything that moved to the homepage is the most common migration failure. It reads as "handled" and loses the value of every link.',
        deliverable: 'A redirect map with old, new, and a tested status chain for each.',
        verify: 'Request twenty old URLs and confirm one hop, status 301, landing on 200 — not a chain and not a soft 404.',
      },
      {
        what: 'Record the DNS exactly as it is today before you change a nameserver, and write the cut-over go/no-go from evidence rather than from readiness.',
        why: 'Losing MX records during a nameserver change is silent, classic, and only discovered when someone says they never got your reply. Moving from ' + from + ' to ' + to + ' does not change that.',
        deliverable: 'A full dated record of current DNS, plus a go/no-go scorecard with the checks that must pass.',
        verify: 'After cut-over, re-check mail delivery, the redirect map, and that the destination is not still serving a staging noindex.',
      },
    ];
  }

  function actionsAgency(a) {
    var p = a.agency_problem || 'notsure';
    var first;
    if (p === 'scoping') {
      first = {
        what: 'Turn your next proposal into a scope document with explicit exclusions and a named number of revision rounds.',
        why: 'Scope creep is not caused by difficult clients. It is caused by a scope that said "and anything else needed" and an estimate that was a guess.',
        deliverable: 'A scope with in-scope items, out-of-scope items, assumptions, and the change-order process for anything else.',
        verify: 'Ask someone outside the project to read it and say what is not included. If they cannot, the exclusions are not explicit enough.',
      };
    } else if (p === 'qa') {
      first = {
        what: 'Write the review checklist that runs before a client ever sees the work, and run it on the current project.',
        why: 'The expensive review comments are the ones the client makes about things you would have caught yourself. A checklist moves that discovery earlier.',
        deliverable: 'A pre-client review checklist with an observed value per line.',
        verify: 'Run it on a project you thought was finished. If it finds nothing, it is too shallow.',
      };
    } else if (p === 'handoff') {
      first = {
        what: 'Define the handoff pack once: credentials route, deployment steps, the decisions log, what the client can change safely, and what they should not.',
        why: 'A handoff that is a folder of files becomes a support obligation. A handoff that is a document ends the engagement cleanly.',
        deliverable: 'A handoff template you can fill in for any project in under an hour.',
        verify: 'Hand it to the client and ask them to deploy a text change. If they cannot, the pack is incomplete.',
      };
    } else if (p === 'reporting') {
      first = {
        what: 'Define one monthly client report shape — what it measures, where each number comes from, and what it deliberately does not claim.',
        why: 'Reporting that is improvised each month is both expensive to produce and impossible to compare over time.',
        deliverable: 'A report template with a named data source beside every figure.',
        verify: 'Produce two consecutive months for one client and check the numbers are comparable.',
      };
    } else {
      first = {
        what: 'Set up one client file set for your current project: the facts in a config file, the rules in CLAUDE.md, the scope as the contract, and four logs — decisions, assumptions, changes, risks.',
        why: 'When every engagement starts from scratch, each one teaches the same lesson again. One set of files per client is what makes the second project cheaper than the first.',
        deliverable: 'A client folder with those six artefacts, populated for a real project.',
        verify: 'Ask a question about the project and answer it from the files alone. If you cannot, the files are not yet the memory.',
      };
    }
    return [
      first,
      {
        what: 'Keep a decisions log and an assumptions log from the first client call, and put the assumptions in the proposal.',
        why: 'The disputes that damage a relationship are almost always about an assumption one side made and never stated.',
        deliverable: 'Two running logs, each entry dated, with who decided it.',
        verify: 'At the next change request, find the entry that governs it. If there is none, add one now.',
      },
      {
        what: 'Put a person between every generated draft and the client — no proposal, estimate or report goes out unread.',
        why: 'A confident document containing an invented requirement, a budget the client never stated, or a promise about rankings will cost more than it saved.',
        deliverable: 'A named review step in your own process, written down.',
        verify: 'Take the last generated document you sent and check every factual claim in it against the client file.',
      },
    ];
  }

  function actionsUnclear(a) {
    return [
      {
        what: 'Write one sentence describing the outcome you want in ninety days, with a number in it.',
        why: 'Your answers did not point clearly at one problem, and the planner will not invent a diagnosis to fill the gap. A single sentence with a number in it usually resolves it.',
        deliverable: 'One sentence, for example "the contact form produces at least four enquiries a month" or "the site is live and indexed".',
        verify: 'If you cannot put a number in it, the goal is still a wish rather than an objective.',
      },
      {
        what: 'Take a read-only baseline of what exists today: the URLs, their status codes, and whatever measurement is already installed.',
        why: 'Whatever the goal turns out to be, the baseline is the same work, and it is the thing that makes the next decision cheap.',
        deliverable: 'A dated snapshot of the current state.',
        verify: 'Check two facts in the snapshot by hand.',
      },
      {
        what: 'Come back and answer the planner again with the sharper goal.',
        why: 'The routing here is deterministic: a clearer goal, stage and platform produce a specific plan rather than this general one.',
        deliverable: 'A plan matched to one stated problem.',
        verify: 'The recommendation should name one product and explain which answers produced it.',
      },
    ];
  }

  /* ------------------------------------------------------------------ *
   * Starter prompt. Original text, scoped to the answers, useful to
   * someone who never buys anything. No paid module content is reproduced.
   * ------------------------------------------------------------------ */
  function promptFor(a, sel, q) {
    var noun = pn(a), plat = platformLabel(a.platform) || 'not stated';
    var stage = stageLabel(a.stage) || 'not stated';
    var g = q.flags.not_ready ? 'getting_started' : (sel.primaryGoal || 'unclear');

    var HEAD = 'CONTEXT\n' +
      '- Platform: ' + plat + '\n' +
      '- Stage: ' + stage + '\n' +
      '- Goal: ' + (goalLabel(a.goal) || 'not stated') + '\n' +
      (a.goal_secondary ? '- Also working on: ' + goalLabel(a.goal_secondary) + '\n' : '');

    var TAIL = '\nBOUNDARIES\n' +
      '- Read and report only. Do not edit, create, delete or move any file in this first run.\n' +
      '- Do not run any command that writes to a live environment, a database or a third-party API.\n' +
      '- Do not commit, push, deploy or change configuration.\n' +
      '- If a check cannot be run, say so and say why. Do not substitute an assumption for a result.\n' +
      '\nEVIDENCE\n' +
      '- Every finding must carry what you observed: a file and line, a command and its output, a URL and its status code, or the exact text you read.\n' +
      '- Label each finding: confirmed (you observed it), likely (consistent with what you observed), or unknown (you could not check).\n' +
      '- Do not report a check as passed unless you ran it and saw it pass.\n' +
      '\nVALIDATION\n' +
      '- Before you report, name one finding that would have been wrong if the check had silently failed, and say how you ruled that out.\n' +
      '- List anything you could not verify, as its own section.\n' +
      '\nSTOP HERE\n' +
      '- Output the findings and stop. Do not begin fixing anything.\n' +
      '- End with: the three findings you would address first, and the single question you most need me to answer.\n';

    var body, title;
    switch (g) {
      case 'getting_started':
        title = 'A safe first Claude Code session';
        body = HEAD + '\nOBJECTIVE\nTell me what this project is, in plain language, without changing anything.\n' +
          '\nDISCOVERY\n' +
          '1. List the files and folders in this directory, to a depth of two.\n' +
          '2. Identify what kind of project this is and what it would take to run it locally.\n' +
          '3. Find the commands that build, test and start it, and tell me where you found each one.\n' +
          '4. Tell me which three files a new person should read first, and why.\n';
        break;
      case 'build':
        title = 'Pre-build review of the plan and the repository';
        body = HEAD + '\nOBJECTIVE\nTell me what is missing before this ' + noun + ' can be built to a production standard, and produce nothing else.\n' +
          '\nDISCOVERY (in this order)\n' +
          '1. Read any brief, requirements, README or CLAUDE.md in this repository and summarise what the project is meant to be.\n' +
          '2. List every page or route that the documentation implies, with its intended URL. Mark any that exist twice under two addresses.\n' +
          '3. Report whether a build, test and deploy command exists, and run each one you find, reporting what actually happened.\n' +
          '4. Identify what is undecided: content source, data source, authentication, hosting, and the definition of done.\n' +
          (a.build_blocker === 'quality' ? '5. Inspect the generated code for the three things most likely to be wrong in agent-generated work: error handling that swallows failures, tests that cannot fail, and configuration hard-coded for one environment.\n' : '') +
          (a.platform === 'undecided' ? '5. From the requirements only, list what each candidate platform would have to support. Do not recommend one yet.\n' : '');
        break;
      case 'seo':
        title = 'Read-only technical SEO review';
        body = HEAD + '\nOBJECTIVE\n' +
          (a.seo_symptom === 'not_indexed' ? 'Find the mechanical reasons specific pages on this ' + noun + ' are not being indexed.'
            : a.seo_symptom === 'indexed_no_rank' ? 'Find the gap between what these pages are about and what they are being shown for.'
            : a.seo_symptom === 'traffic_dropped' ? 'Find what changed on this site around the date search traffic dropped.'
            : 'Establish whether this ' + noun + ' can be crawled, indexed and understood, before anything is optimised.') + '\n' +
          '\nDISCOVERY (in this order — do not skip ahead)\n' +
          '1. Fetch robots.txt and the sitemap. Report the number of URLs in the sitemap and any disallow rule that affects them.\n' +
          '2. For each of up to twenty URLs, fetch the page with a plain HTTP request and report: final status code, number of redirect hops, robots meta and X-Robots-Tag, canonical target, title, meta description, and h1.\n' +
          '3. Flag every URL where the canonical points somewhere other than itself, or where the sitemap and the canonical disagree.\n' +
          '4. Report whether the main content is present in the HTML response or only after JavaScript runs.\n' +
          '5. List pages with a duplicate title or duplicate description, grouped.\n' +
          (a.seo_symptom === 'traffic_dropped' ? '6. List the changes visible in version control in the four weeks before the date I give you, filtered to templates, redirects, robots and head tags.\n' : '');
        break;
      case 'convert':
        title = 'Read-only conversion measurement and funnel review';
        body = HEAD + '\nOBJECTIVE\nTell me whether the conversion on this ' + noun + ' is measured correctly, and where the funnel loses people. Diagnose nothing that the data does not support.\n' +
          '\nDISCOVERY (in this order)\n' +
          '1. Identify every analytics or tag script loaded on the site, and report each one once with the page it loads on.\n' +
          '2. Identify the primary conversion action and the event that is supposed to represent it. Report where in the code that event is fired from.\n' +
          '3. Report every place that event could fire more than once: page load, route change, back navigation, a re-render, or two scripts firing the same event.\n' +
          '4. Locate the form or checkout that completes the conversion, and report where the submission is sent and what happens if that request fails.\n' +
          '5. List the steps between arriving and converting, in order, as they exist in the code.\n' +
          '\nEXPLICITLY DO NOT\n' +
          '- Do not tell me a change will increase conversions by a percentage. Nobody can know that in advance.\n' +
          '- Do not propose countdown timers, stock warnings or any other invented urgency.\n';
        break;
      case 'maintain':
        title = 'Outside-in operations baseline';
        body = HEAD + '\nOBJECTIVE\nProduce a dated baseline of this ' + noun + '’s operational state, from the outside, changing nothing.\n' +
          '\nDISCOVERY\n' +
          '1. For each key URL: final status code, redirect chain, response time, and the security headers actually served.\n' +
          '2. TLS: issuer, expiry date, and how many days remain.\n' +
          '3. DNS: every record as it is right now, recorded verbatim, including MX.\n' +
          '4. Dependencies, plugins or themes in use, with current version and latest version, and any with a published advisory.\n' +
          '5. Report whether a backup exists, when it last ran, and whether a restore has ever been tested. If you cannot tell, say you cannot tell.\n' +
          '6. Report what runs before and after a deploy, reading the CI configuration.\n';
        break;
      case 'shopify_admin':
        title = 'Read-only Shopify catalogue audit';
        body = HEAD + '\nOBJECTIVE\nAudit the parts of this Shopify catalogue I am about to change, and tell me exactly how many records are affected, before any write happens.\n' +
          '\nDISCOVERY\n' +
          '1. Confirm which store you are connected to and which Admin API scopes are available. Report them. Never print the access token.\n' +
          '2. Export, to a local file, the current values for the objects in scope. Report the row count.\n' +
          '3. Reconcile that row count against the catalogue total, and tell me if the export is short.\n' +
          '4. Audit the export against these rules and list the failures with their current values.\n' +
          '5. Report how many records a change would touch, and what the exact before value is for the first five.\n' +
          '\nBOUNDARIES SPECIFIC TO THIS RUN\n' +
          '- Read-only API calls only. No mutation, no bulk operation, no metafield write.\n' +
          '- Never print, log or write an API access token anywhere.\n';
        break;
      case 'migrate':
        title = 'Pre-migration inventory and baseline';
        body = HEAD + '\nOBJECTIVE\nInventory the existing site completely while it is still up, so that nothing is discovered missing after cut-over.\n' +
          '\nDISCOVERY\n' +
          '1. Crawl the existing site and produce one row per URL: address, status code, title, canonical, indexability, and internal link count.\n' +
          '2. Reconcile the crawl against the sitemap and list what is in one and not the other.\n' +
          '3. Record every form on the site, where it posts to, and what confirms a successful submission.\n' +
          '4. Record every third-party script and embed, and what would break without it.\n' +
          '5. Record the current DNS verbatim, including MX and TXT records.\n' +
          '6. Produce the redirect map as a draft: old URL, proposed new URL, and mark every row you are guessing at.\n' +
          '\nEXPLICITLY DO NOT\n' +
          '- Do not redirect anything to the homepage as a default.\n' +
          '- Do not touch DNS, and do not deploy the destination.\n';
        break;
      case 'agency':
        title = 'Client engagement file review';
        body = HEAD + '\nOBJECTIVE\nRead everything that exists for this client engagement and tell me what a person joining the project could not answer from it.\n' +
          '\nDISCOVERY\n' +
          '1. List every document that describes this engagement and what each one claims to define.\n' +
          '2. Extract the agreed scope, and separately every sentence that could be read as open-ended.\n' +
          '3. List the assumptions the work depends on that are not written down anywhere the client has seen.\n' +
          '4. List decisions that have been made in conversation and never recorded.\n' +
          '5. Report whether revision rounds, the change process and the handoff are defined, quoting the text where they are.\n' +
          '\nEXPLICITLY DO NOT\n' +
          '- Do not draft anything for the client in this run.\n' +
          '- Do not invent a requirement, a budget, a deadline or a promise about results.\n';
        break;
      default:
        title = 'Read-only project baseline';
        body = HEAD + '\nOBJECTIVE\nTell me what this project is and what state it is in, so I can decide what to work on. Change nothing.\n' +
          '\nDISCOVERY\n' +
          '1. Summarise what the project is, from its own files.\n' +
          '2. List the URLs or routes it serves and their status.\n' +
          '3. Report what measurement is installed, if any.\n' +
          '4. List the three things most likely to be wrong, with the evidence for each.\n';
    }
    return { title: title, text: body + TAIL };
  }

  /* ------------------------------------------------------------------ *
   * Free next step
   * ------------------------------------------------------------------ */
  var FREE_BY_GOAL = {
    build: { shopify: 'free-shopify-hub', wordpress: 'free-wordpress-hub', astro: 'free-astro-hub', _: 'free-build-guide' },
    seo: { _: 'free-technical-seo' },
    convert: { _: 'free-cro-guide' },
    maintain: { _: 'free-maintenance-guide' },
    shopify_admin: { _: 'free-shopify-admin-guide' },
    migrate: { _: 'free-migration-guide' },
    agency: { _: 'free-labs-hub' },
  };
  function freeStepFor(C, a, sel, q) {
    if (q.flags.not_ready) {
      var r = freeById(C, 'free-terminal-setup');
      return r ? { resource: r, why: 'It is the shortest route from "I have not used a terminal" to a working Claude Code session, and it costs nothing.' } : null;
    }
    var g = sel.primaryGoal;
    var map = FREE_BY_GOAL[g];
    var id = map ? (map[a.platform] || map._) : 'free-resources-hub';
    if (q.flags.shopify_admin_no_task) id = 'free-shopify-hub';
    if (!g) id = 'free-resources-hub';
    var res = freeById(C, id) || freeById(C, 'free-resources-hub');
    if (!res) return null;
    var WHY = {
      build: 'It covers the same first moves as the plan above, in more depth, and it is free to read before you spend anything.',
      seo: 'It walks through the read-only audit sequence the first action describes, with the commands.',
      convert: 'It explains the measurement checks the plan starts with, which is the part most conversion advice skips.',
      maintain: 'It covers the recurring checks in the plan above and what each one is actually looking for.',
      shopify_admin: 'It shows what Admin API work looks like in practice, so you can judge whether the paid toolkit is worth it before buying.',
      migrate: 'It is the checklist version of the inventory and redirect work in the plan above.',
      agency: 'The labs are short, hands-on exercises you can run against a real project today.',
    };
    return { resource: res, why: WHY[g] || 'A free starting point while you decide what to work on.' };
  }

  /* ------------------------------------------------------------------ *
   * decide() — the whole result
   * ------------------------------------------------------------------ */
  function decide(rawAnswers, catalogue, options) {
    options = options || {};
    var C = indexCatalogue(catalogue);
    var a = normalize(rawAnswers || {});
    var q = qualify(a);
    var sel = selectProducts(a, q);
    var ps = priceState(C, options.today);
    var owned = expandOwned(C, ownedIds(a));
    var ownsUnknown = a.owns.indexOf('notsure') !== -1;

    /* --- ownership ------------------------------------------------- */
    var ownershipNotes = [];
    var primaryId = sel.primary, complementaryId = sel.secondary;
    var ownedPrimary = null;

    if (primaryId && owned.indexOf(primaryId) !== -1) {
      ownedPrimary = primaryId;
      ownershipNotes.push('You already own the ' + C.byId[primaryId].shortName + ', which is the product your answers point to. Nothing to buy — the plan below is how to use it.');
      primaryId = (complementaryId && owned.indexOf(complementaryId) === -1) ? complementaryId : null;
      complementaryId = null;
    }
    if (complementaryId && owned.indexOf(complementaryId) !== -1) {
      ownershipNotes.push('You already own the ' + C.byId[complementaryId].shortName + ', so it is not offered again.');
      complementaryId = null;
    }
    if (ownsUnknown) {
      ownershipNotes.push('You were not sure what you already own. Check your order confirmation emails before buying anything below — every purchase is a one-time download and there is no reason to buy one twice.');
    }

    /* --- bundle ------------------------------------------------------ */
    var answerDerived = uniq([sel.primary, sel.secondary].filter(Boolean))
      .filter(function (id) { return C.bundleMembers.indexOf(id) !== -1; });
    var bundle = bundleComparison(C, answerDerived, owned, ps);
    /* The bundle is only offered when the arithmetic says it costs less
       for the products the visitor actually needs. */
    var offerBundle = bundle.verdict === 'bundle_cheaper';
    if (offerBundle) complementaryId = null;

    /* --- mode -------------------------------------------------------- */
    var mode = 'recommend';
    if (q.flags.not_ready) mode = 'free_first';
    else if (ownedPrimary && !primaryId) mode = 'use_what_you_own';
    else if (!primaryId && !offerBundle) mode = 'qualified';

    /* --- reasoning --------------------------------------------------- */
    var because = [];
    if (a.goal) because.push('your goal: ' + goalLabel(a.goal).toLowerCase());
    if (a.goal_secondary) because.push('and ' + goalLabel(a.goal_secondary).toLowerCase());
    if (a.platform) because.push('platform: ' + platformLabel(a.platform));
    if (a.stage) because.push('stage: ' + stageLabel(a.stage).toLowerCase());
    relevantContextKeys(a).forEach(function (k) {
      var v = a[k];
      if (v === undefined) return;
      if (CONTEXT[k].multi) {
        if (arr(v).length) because.push(CONTEXT[k].question.replace(/\?$/, '') + ': ' + arr(v).map(function (x) { return contextLabel(k, x); }).join(', '));
      } else {
        because.push(CONTEXT[k].question.replace(/\?$/, '') + ': ' + contextLabel(k, v));
      }
    });

    /* --- headline ---------------------------------------------------- */
    var headline, summary;
    if (mode === 'free_first') {
      headline = 'Start free, and buy nothing yet.';
      summary = 'Based on your answers, the thing standing between you and any of these workflows is Claude Code itself, not the workflows. Get a session running and write one memory file; that is a genuinely useful afternoon and it costs nothing. The ' + (sel.primary ? C.byId[sel.primary].shortName : 'matching toolkit') + ' is the right product for your goal, but it is worth buying after you have run a first session, not before.';
    } else if (mode === 'use_what_you_own') {
      headline = 'You already own what you need. Use it.';
      summary = 'Based on your answers, the product that matches your goal is one you have already bought. The three actions below are the sequence to run from it, and the free resource at the end covers the same ground if you want a refresher first.';
    } else if (mode === 'qualified') {
      headline = 'Your answers do not point at one product yet.';
      summary = 'Based on your answers, there is no single toolkit that clearly fits, and this planner will not invent one. The actions below are worth doing regardless, and the free resource is a better next step than any purchase right now.';
    } else {
      var p = C.byId[primaryId];
      headline = goalHeadline(sel.primaryGoal, a, q);
      summary = 'Based on your answers, the work in front of you is ' + goalSummary(sel.primaryGoal, a, q) +
        ' The three actions below are in the order they should be done, and the ' + p.shortName + ' is the SiteBuilderStack product written for exactly this.';
    }

    /* --- assemble ---------------------------------------------------- */
    var primaryProduct = primaryId ? C.byId[primaryId] : null;
    var complementaryProduct = complementaryId ? C.byId[complementaryId] : null;

    return {
      version: '1.0.0',
      answers: a,
      mode: mode,
      headline: headline,
      summary: summary,
      qualificationNotes: q.notes,
      flags: q.flags,
      because: because,
      actions: actionsFor(a, sel, q),
      prompt: promptFor(a, sel, q),
      primary: primaryProduct ? {
        id: primaryProduct.id,
        product: primaryProduct,
        priceText: priceText(C, primaryProduct, ps),
        fit: fitText(sel.primaryGoal, a, q, primaryProduct),
        limitation: limitationText(primaryProduct, a, q),
        freeVsPaid: freeVsPaid(sel.primaryGoal, primaryProduct),
        cta: 'View the complete ' + primaryProduct.shortName,
        deEmphasised: mode === 'free_first',
      } : null,
      complementary: complementaryProduct ? {
        id: complementaryProduct.id,
        product: complementaryProduct,
        priceText: priceText(C, complementaryProduct, ps),
        why: 'You also named ' + goalLabel(sel.statedSecondary || sel.secondaryGoal).toLowerCase() + '. That is a different problem with a different product, and it is optional — the primary recommendation stands on its own.',
      } : null,
      bundle: bundle,
      offerBundle: offerBundle,
      ownership: { owned: owned, unknown: ownsUnknown, notes: ownershipNotes, ownedPrimary: ownedPrimary },
      freeStep: freeStepFor(C, a, sel, q),
      priceState: ps,
      selection: sel,
    };
  }

  function goalHeadline(g, a, q) {
    var H = {
      build: 'Get this build to a launch you can defend.',
      seo: 'Find out why search cannot see this site.',
      convert: 'Trust the numbers before you change the page.',
      maintain: 'Turn maintenance into checks with a rhythm.',
      shopify_admin: 'Export first, audit second, write last.',
      migrate: 'Inventory everything while the old site is still up.',
      agency: 'Make the engagement repeatable, not the argument.',
    };
    if (q.flags.convert_not_live || q.flags.seo_before_launch || q.flags.maintain_not_live) return 'First, finish the build.';
    if (q.flags.convert_no_traffic) return 'You need arrivals before you optimise them.';
    return H[g] || 'Start with a baseline.';
  }
  function goalSummary(g, a, q) {
    if (q.flags.convert_not_live) return 'getting the site live and correct, not optimising a conversion rate on a site nobody can reach yet.';
    if (q.flags.convert_no_traffic) return 'discovery — the site is live, but conversion work on almost no traffic optimises a percentage of nearly nothing.';
    if (q.flags.seo_before_launch) return 'building the search architecture into the site now, rather than auditing a site that is not published.';
    if (q.flags.maintain_not_live) return 'reaching a launch, after which the operations work has something to operate.';
    var S = {
      build: 'a build problem: structure and constraints decided before code, then a gate in front of every deploy.',
      seo: 'a discovery problem, and it is almost certainly mechanical rather than a matter of writing more.',
      convert: 'a measurement problem before it is a design problem.',
      maintain: 'operational: the failures that matter are the quiet ones, and they are found by checks that run on a schedule.',
      shopify_admin: 'catalogue automation, which is safe only with an export to roll back to and a read-back after every write.',
      migrate: 'a mapping and validation exercise — a migration is not a copy.',
      agency: 'in the engagement rather than the build: scope, review, handoff and the record of what was decided.',
    };
    return S[g] || 'not yet clearly defined.';
  }

  function fitText(g, a, q, p) {
    var bits = [];
    if (q.flags.convert_not_live) bits.push('Your goal was conversion, but the site is not live yet, so the build product comes first.');
    if (q.flags.convert_no_traffic) bits.push('Your goal was conversion, but with little or no traffic the constraint is discovery, so this is the product for that.');
    if (q.flags.seo_before_launch) bits.push('An audit toolkit needs a published site; this one builds the search architecture in from the start.');
    if (q.flags.agency_defers) bits.push('Client delivery is the way you work; this product is for the project itself.');
    bits.push(p.useCase);
    return bits.join(' ');
  }
  function limitationText(p, a, q) {
    var ex = (p.exclusions || [])[0] || '';
    var base = 'Reasons this might not be for you yet: ' + ex;
    if (a.readiness === 'access_help') base += ' It also assumes you will run the prompts yourself inside Claude Code — there is a learning curve, and nothing here does the work unattended.';
    return base;
  }
  function freeVsPaid(g, p) {
    var F = {
      build: 'The plan above gets you a brief, a memory file and a gate. The product adds the staged build prompt, the platform systems, the security and accessibility audits, and the launch checklists.',
      seo: 'The plan above is the first three checks. The product adds the remaining seventeen prompts in dependency order, the report templates, and the rules that stop an audit quietly reporting a success it never checked.',
      convert: 'The plan above verifies measurement and tests one change. The product adds the full funnel and analytics-verification workflows, the finding format with honesty labels, and an experimentation system that refuses tests the traffic cannot support.',
      maintain: 'The plan above is the first baseline. The product adds the scripts that produce it every month, the health score, the deploy gates, the incident playbooks and the reporting.',
      shopify_admin: 'The plan above is export, audit, single write. The product adds the scripts and validated GraphQL for every catalogue area, with a preview, a backup and a read-back built into each one.',
      migrate: 'The plan above is the inventory and the redirect map. The product adds the crawler, the page-by-page metadata comparison, the platform guides and the GO / NO-GO scorecard.',
      agency: 'The plan above sets up one client file set. The product adds the commands for every stage from discovery to retention, the templates, the checklists and a complete worked engagement.',
    };
    return F[g] || 'The plan above is free and yours to keep. The product is the complete workflow set for the same problem.';
  }

  /* ------------------------------------------------------------------ *
   * Export as Markdown (used by the copy and download controls)
   * ------------------------------------------------------------------ */
  function toMarkdown(result, catalogue) {
    var C = indexCatalogue(catalogue), L = [];
    L.push('# Your SiteBuilderStack website action plan');
    L.push('');
    L.push('_Generated by the SiteBuilderStack Website Action Planner. This plan is based entirely on the answers you selected — nothing about your website was scanned, crawled or measured._');
    L.push('');
    L.push('## Your answers');
    result.because.forEach(function (b) { L.push('- ' + b); });
    L.push('');
    L.push('## Your next move');
    L.push('**' + result.headline + '**');
    L.push('');
    L.push(result.summary);
    if (result.qualificationNotes.length) {
      L.push('');
      result.qualificationNotes.forEach(function (n) { L.push('> ' + n); L.push('>'); });
    }
    L.push('');
    L.push('## Three prioritised actions');
    result.actions.forEach(function (ac, i) {
      L.push('');
      L.push('### ' + (i + 1) + '. ' + ac.what);
      L.push('');
      L.push('- **Why:** ' + ac.why);
      L.push('- **Deliverable:** ' + ac.deliverable);
      L.push('- **How to verify it is done:** ' + ac.verify);
    });
    L.push('');
    L.push('## Free starter Claude Code prompt');
    L.push('');
    L.push('**' + result.prompt.title + '**');
    L.push('');
    L.push('```');
    L.push(result.prompt.text);
    L.push('```');
    if (result.primary) {
      L.push('');
      L.push('## Recommended toolkit');
      L.push('');
      L.push('**' + result.primary.product.title + '** — ' + result.primary.priceText);
      L.push('');
      L.push(result.primary.fit);
      L.push('');
      (result.primary.product.benefits || []).slice(0, 3).forEach(function (b) { L.push('- ' + b); });
      L.push('');
      L.push('- **Prerequisites:** ' + result.primary.product.prerequisites);
      L.push('- **What the free plan does vs the product:** ' + result.primary.freeVsPaid);
      L.push('- **' + result.primary.limitation + '**');
      L.push('');
      L.push(result.primary.product.url);
    }
    if (result.offerBundle && result.bundle.statement) {
      L.push('');
      L.push('## Bundle comparison');
      L.push('');
      L.push(result.bundle.statement);
      L.push('');
      L.push(C.byId['complete-stack'].url);
    }
    if (result.ownership.notes.length) {
      L.push('');
      L.push('## What you already own');
      result.ownership.notes.forEach(function (n) { L.push('- ' + n); });
    }
    if (result.freeStep) {
      L.push('');
      L.push('## A free next step');
      L.push('');
      L.push('[' + result.freeStep.resource.title + '](' + result.freeStep.resource.url + ') — ' + result.freeStep.why);
    }
    L.push('');
    L.push('---');
    L.push('');
    L.push('Produced by SiteBuilderStack — https://sitebuilderstack.com');
    L.push('');
    L.push('This plan reflects self-reported answers. It is not an audit, a measurement, or a verified assessment of your website. Prices were last verified on ' + (result.priceState.verifiedOn || 'an unknown date') + '.');
    L.push('');
    return L.join('\n');
  }

  return {
    GOALS: GOALS, PLATFORMS: PLATFORMS, STAGES: STAGES, READINESS: READINESS,
    CONTEXT: CONTEXT, GOAL_PRODUCT: GOAL_PRODUCT,
    goalLabel: goalLabel, platformLabel: platformLabel, stageLabel: stageLabel,
    readinessLabel: readinessLabel, contextLabel: contextLabel,
    normalize: normalize, relevantContextKeys: relevantContextKeys, activeGoals: activeGoals,
    qualify: qualify, selectProducts: selectProducts,
    bundleComparison: bundleComparison, indexCatalogue: indexCatalogue,
    priceState: priceState, priceText: priceText, fmt: fmt, money: money,
    decide: decide, toMarkdown: toMarkdown,
  };
});
