/* src/app.js — the interface. All routing decisions come from
 * recommendation-rules.js; this file only asks the questions and draws
 * the answer. Nothing here fetches, and nothing is persisted except the
 * local debug journal, which holds no answers.
 *
 * Every node is built with createElement and textContent. No markup is
 * ever assembled from data, so there is no path from an answer to HTML.
 */
(function () {
  'use strict';

  var R = window.SBS_RULES;
  var CAT = window.SBS_PRODUCTS;
  var AN = window.SBSPlannerAnalytics;
  var CFG = window.SBS_PLANNER_CONFIG || { SHARE_URL: '', COMPANION_PAGE: '' };
  var C = R.indexCatalogue(CAT);

  /* ---------------- tiny DOM helpers ---------------- */
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === 'class') n.className = v;
      else if (k === 'text') n.textContent = v;
      else if (k === 'html') n.innerHTML = v;            /* only ever called with literal icon markup below */
      else if (k.slice(0, 2) === 'on') n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? '' : String(v));
    });
    (kids || []).forEach(function (k) { if (k) n.appendChild(typeof k === 'string' ? document.createTextNode(k) : k); });
    return n;
  }
  function frag(kids) { var f = document.createDocumentFragment(); kids.forEach(function (k) { if (k) f.appendChild(k); }); return f; }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); return n; }
  var TICK = '<svg viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8.5 6.2 12 13 4.5"/></svg>';

  /* ---------------- state ---------------- */
  var state = { step: -1, answers: { owns: [] }, result: null, isExample: false };
  var downloads = null;

  var STEPS = ['goal', 'platform', 'stage', 'context', 'readiness', 'owns'];
  var STEP_TITLE = {
    goal: 'What are you trying to do?',
    platform: 'What is the site built on?',
    stage: 'Where is it right now?',
    context: 'A little more about the problem',
    readiness: 'How are you placed for Claude Code?',
    owns: 'Do you already own any of these?',
  };

  /* ---------------- shell ---------------- */
  var root = document.getElementById('app');

  function mount() {
    AN.track('artifact_opened', {});
    if (window.claude && typeof window.claude.use === 'function') {
      try {
        window.claude.use('downloads').then(function (d) { downloads = d; if (state.step === 99) render(); })
          .catch(function () { downloads = null; });
      } catch (e) { downloads = null; }
    }
    render();
  }

  function render() {
    clear(root);
    if (state.step === -1) root.appendChild(viewIntro());
    else if (state.step === 99) root.appendChild(viewResult());
    else root.appendChild(viewStep());
    var h = root.querySelector('[data-focus]');
    if (h && state.step !== -1) { h.focus({ preventScroll: true }); window.scrollTo(0, 0); }
  }

  /* ---------------- intro ---------------- */
  function viewIntro() {
    var facts = [
      'The plan is free, and the whole result is on one page.',
      'No email address is required to see it — SiteBuilderStack does not ask for one here.',
      'Recommendations come from your answers and nothing else.',
      'This tool does not scan, crawl or audit a live website.',
    ];
    return el('div', { class: 'wrap' }, [
      el('section', { class: 'hero' }, [
        el('p', { class: 'eyebrow', text: 'SiteBuilderStack · Website Action Planner' }),
        el('h1', { class: 'h-hero', text: 'Find your next website move.' }),
        el('p', { class: 'lede', text: 'Answer a few questions to get a practical action plan, a starter Claude Code prompt, and a toolkit recommendation matched to your goal.' }),
        el('div', { class: 'hero__acts' }, [
          el('button', { class: 'btn', type: 'button', id: 'start', onclick: start }, ['Build my free plan']),
          el('button', { class: 'btn btn--ghost', type: 'button', id: 'example', onclick: showExample }, ['See an example']),
        ]),
        el('ul', { class: 'facts' }, facts.map(function (f) {
          return el('li', {}, [el('span', { html: TICK }), el('span', { text: f })]);
        })),
      ]),
      el('section', { class: 'section', style: 'margin-top:1rem' }, [
        el('p', { class: 'small dim prose', text: 'This planner is made by SiteBuilderStack and recommends SiteBuilderStack products. It is not an independent review site. The paid products are downloadable workflows, prompts, templates and checklists you run yourself inside Claude Code — not services that do the work for you.' }),
      ]),
    ]);
  }

  function start() {
    state.isExample = false;
    state.answers = { owns: [] };
    state.step = 0;
    AN.track('planner_started', {});
    render();
  }

  var EXAMPLE = {
    goal: 'seo', goal_secondary: '', platform: 'wordpress', stage: 'live_no_traffic',
    seo_symptom: 'not_indexed', readiness: 'using', owns: ['none'],
  };
  function showExample() {
    state.isExample = true;
    state.answers = JSON.parse(JSON.stringify(EXAMPLE));
    state.result = R.decide(state.answers, CAT);
    state.step = 99;
    render();
  }

  /* ---------------- questions ---------------- */
  function activeContextKeys() { return R.relevantContextKeys(state.answers); }

  function viewStep() {
    var id = STEPS[state.step];
    var body;
    if (id === 'goal') body = qGoal();
    else if (id === 'platform') body = qSingle('platform', 'Which of these is closest?', R.PLATFORMS);
    else if (id === 'stage') body = qSingle('stage', 'Where is the project today?', R.STAGES);
    else if (id === 'context') body = qContext();
    else if (id === 'readiness') body = qSingle('readiness', 'Pick the one that fits.', R.READINESS);
    else body = qOwns();

    return el('div', { class: 'wrap' }, [
      progress(),
      el('div', { class: 'q' }, [
        el('h1', { class: 'h-1', tabindex: '-1', 'data-focus': '1', text: STEP_TITLE[id] }),
        body,
        navRow(),
      ]),
    ]);
  }

  function progress() {
    var segs = STEPS.map(function (_, i) {
      return el('div', { class: 'progress__seg' + (i < state.step ? ' is-done' : i === state.step ? ' is-now' : '') });
    });
    return el('div', { class: 'progress' }, [
      el('div', { class: 'progress__bar', role: 'presentation' }, segs),
      el('div', { class: 'progress__txt' }, [
        el('span', { text: 'Step ' + (state.step + 1) + ' of ' + STEPS.length, 'aria-live': 'polite' }),
        el('span', { text: 'No email required' }),
      ]),
    ]);
  }

  function optionRow(type, name, value, text, note, checked, onchange) {
    var input = el('input', { type: type, name: name, value: value, checked: checked || null, onchange: onchange });
    return el('label', { class: 'opt' }, [
      input,
      el('span', { class: 'opt__dot' + (type === 'checkbox' ? ' opt__dot--box' : ''), 'aria-hidden': 'true' }),
      el('span', { class: 'opt__txt' }, [el('span', { text: text }), note ? el('span', { class: 'opt__note', text: note }) : null]),
    ]);
  }

  function group(legend, rows, hint) {
    return el('fieldset', { class: 'q__group' }, [
      el('legend', { class: 'q__legend h-3' }, [legend]),
      hint ? el('p', { class: 'small dim', text: hint }) : null,
      el('div', { class: 'q__opts' }, rows),
    ]);
  }

  function qSingle(key, legend, pairs, hint) {
    var rows = pairs.map(function (p) {
      return optionRow('radio', key, p[0], p[1], null, state.answers[key] === p[0], function () {
        state.answers[key] = p[0];
        updateNav();
      });
    });
    return group(legend, rows, hint);
  }

  function qGoal() {
    var primary = R.GOALS.map(function (g) {
      return optionRow('radio', 'goal', g[0], g[1], null, state.answers.goal === g[0], function () {
        state.answers.goal = g[0];
        if (state.answers.goal_secondary === g[0]) state.answers.goal_secondary = '';
        /* a changed goal invalidates the contextual answers it owned */
        Object.keys(R.CONTEXT).forEach(function (k) {
          if (activeContextKeys().indexOf(k) === -1) delete state.answers[k];
        });
        render();
      });
    });
    var secondaryOpts = [optionRow('radio', 'goal_secondary', '', 'Nothing else for now', null, !state.answers.goal_secondary, function () {
      state.answers.goal_secondary = '';
      Object.keys(R.CONTEXT).forEach(function (k) { if (activeContextKeys().indexOf(k) === -1) delete state.answers[k]; });
    })].concat(R.GOALS.filter(function (g) { return g[0] !== state.answers.goal; }).map(function (g) {
      return optionRow('radio', 'goal_secondary', g[0], g[1], null, state.answers.goal_secondary === g[0], function () {
        state.answers.goal_secondary = g[0];
        Object.keys(R.CONTEXT).forEach(function (k) { if (activeContextKeys().indexOf(k) === -1) delete state.answers[k]; });
      });
    }));

    return frag([
      group('Your main goal', primary),
      state.answers.goal ? el('details', { class: 'more' }, [
        el('summary', { text: 'Add a second goal (optional)' }),
        el('div', { class: 'more__body' }, [
          el('p', { class: 'small dim', text: 'Only if a second problem is genuinely in front of you. It changes the plan, and it is used to compare the bundle price honestly — never to add products you did not ask for.' }),
          el('div', { class: 'q__opts' }, secondaryOpts),
        ]),
      ]) : null,
    ]);
  }

  function qContext() {
    var keys = activeContextKeys();
    if (!keys.length) {
      return el('p', { class: 'muted', text: 'Nothing else is needed for this goal — go on to the next step.' });
    }
    return frag(keys.map(function (k) {
      var q = R.CONTEXT[k];
      if (q.multi) {
        var current = Array.isArray(state.answers[k]) ? state.answers[k] : [];
        var rows = q.options.map(function (o) {
          return optionRow('checkbox', k + '[]', o[0], o[1], null, current.indexOf(o[0]) !== -1, function (ev) {
            var arr = Array.isArray(state.answers[k]) ? state.answers[k].slice() : [];
            var excl = q.exclusive || [];
            if (ev.target.checked) {
              if (excl.indexOf(o[0]) !== -1) arr = [o[0]];
              else arr = arr.filter(function (x) { return excl.indexOf(x) === -1; }).concat([o[0]]);
            } else {
              arr = arr.filter(function (x) { return x !== o[0]; });
            }
            state.answers[k] = arr;
            render();
          });
        });
        return group(q.question, rows, 'Select any that apply.');
      }
      var rows2 = q.options.map(function (o) {
        return optionRow('radio', k, o[0], o[1], null, state.answers[k] === o[0], function () {
          state.answers[k] = o[0];
          updateNav();
        });
      });
      return group(q.question, rows2);
    }));
  }

  function qOwns() {
    var owns = Array.isArray(state.answers.owns) ? state.answers.owns : [];
    var rows = [optionRow('checkbox', 'owns[]', 'none', 'I own none of them', null, owns.indexOf('none') !== -1, onOwn('none'))];
    C.raw.products.forEach(function (p) {
      rows.push(optionRow('checkbox', 'owns[]', p.id, p.title, p.isBundle ? 'Counts as owning its three products' : null, owns.indexOf(p.id) !== -1, onOwn(p.id)));
    });
    rows.push(optionRow('checkbox', 'owns[]', 'notsure', 'Not sure', null, owns.indexOf('notsure') !== -1, onOwn('notsure')));
    return group('This is optional, and nothing is looked up.', rows, 'No login, no purchase history, nothing sent anywhere. It is here so the planner does not recommend something you have already bought.');
  }
  function onOwn(id) {
    return function (ev) {
      var owns = Array.isArray(state.answers.owns) ? state.answers.owns.slice() : [];
      if (ev.target.checked) {
        if (id === 'none' || id === 'notsure') owns = [id];
        else owns = owns.filter(function (x) { return x !== 'none' && x !== 'notsure'; }).concat([id]);
      } else {
        owns = owns.filter(function (x) { return x !== id; });
      }
      state.answers.owns = owns;
      render();
    };
  }

  /* ---------------- navigation ---------------- */
  function canAdvance() {
    var id = STEPS[state.step];
    if (id === 'goal') return !!state.answers.goal;
    if (id === 'platform') return !!state.answers.platform;
    if (id === 'stage') return !!state.answers.stage;
    if (id === 'readiness') return !!state.answers.readiness;
    if (id === 'context') {
      return activeContextKeys().every(function (k) {
        var q = R.CONTEXT[k];
        return q.multi ? (Array.isArray(state.answers[k]) && state.answers[k].length > 0) : !!state.answers[k];
      });
    }
    return Array.isArray(state.answers.owns) && state.answers.owns.length > 0;
  }
  function updateNav() {
    var n = document.getElementById('next');
    if (n) n.disabled = !canAdvance();
  }
  function navRow() {
    var last = state.step === STEPS.length - 1;
    return el('div', { class: 'nav' }, [
      state.step > 0 ? el('button', { class: 'btn btn--ghost', type: 'button', onclick: back }, ['Back']) : null,
      el('button', { class: 'btn', type: 'button', id: 'next', disabled: !canAdvance() || null, onclick: next }, [last ? 'Show my plan' : 'Next']),
      el('span', { class: 'nav__spacer' }),
      el('button', { class: 'btn btn--quiet btn--sm', type: 'button', onclick: reset }, ['Start again']),
    ]);
  }
  function back() { if (state.step > 0) { state.step--; render(); } }
  function next() {
    if (!canAdvance()) return;
    if (state.step === STEPS.length - 1) {
      state.result = R.decide(state.answers, CAT);
      state.step = 99;
      AN.track('planner_completed', {});
      AN.track('recommendation_viewed', { product_id: state.result.primary ? state.result.primary.id : 'none' });
      render();
      return;
    }
    state.step++;
    render();
  }
  function reset() {
    state.step = -1; state.answers = { owns: [] }; state.result = null; state.isExample = false;
    render();
  }

  /* ---------------- result ---------------- */
  function viewResult() {
    var r = state.result;
    var chip = r.mode === 'free_first' ? ['chip chip--free', 'Free path first']
      : r.mode === 'use_what_you_own' ? ['chip chip--owned', 'You already own it']
      : r.mode === 'qualified' ? ['chip chip--qualified', 'Qualified result']
      : ['chip', 'Matched to your answers'];

    var left = el('div', { class: 'result__main' }, [
      sectionNextMove(r, chip),
      sectionActions(r),
      sectionPrompt(r),
      sectionFreeStep(r),
      sectionControls(r),
    ]);
    var rail = el('aside', { class: 'result__rail' }, [sectionToolkit(r)]);

    return el('div', { class: 'wrap wrap--wide result' }, [
      state.isExample ? exampleBanner() : null,
      el('div', { class: 'result__cols' }, [left, rail]),
      footerNote(r),
    ]);
  }

  function exampleBanner() {
    return el('div', { class: 'note', style: 'border-left-color: var(--accent)' }, [
      el('strong', { text: 'Example project. ' }),
      el('span', { text: 'A WordPress site that is live, gets almost no traffic, and has pages missing from the index. It is an illustration of the output — not a real customer, not a case study, and not a measurement of any website.' }),
      el('div', { style: 'margin-top:.6rem' }, [
        el('button', { class: 'btn btn--sm', type: 'button', onclick: start }, ['Build my own plan']),
      ]),
    ]);
  }

  function sectionNextMove(r, chip) {
    return el('section', { class: 'section' }, [
      el('span', { class: chip[0], text: chip[1] }),
      el('h1', { class: 'h-1', tabindex: '-1', 'data-focus': '1', text: r.headline }),
      el('p', { class: 'lede', text: r.summary }),
      r.qualificationNotes.length ? el('div', {}, r.qualificationNotes.map(function (n) { return el('p', { class: 'note', text: n }); })) : null,
      el('div', {}, [
        el('p', { class: 'eyebrow', text: 'Recommended because you selected', style: 'margin-bottom:.5rem' }),
        el('ul', { class: 'because' }, r.because.map(function (b) { return el('li', { text: b }); })),
      ]),
      r.ownership.notes.length ? el('div', {}, r.ownership.notes.map(function (n) { return el('p', { class: 'note', style: 'border-left-color: var(--ok)', text: n }); })) : null,
    ]);
  }

  function sectionActions(r) {
    return el('section', { class: 'section' }, [
      el('h2', { class: 'h-2', text: 'Three prioritised actions' }),
      el('p', { class: 'small dim', text: 'In this order. Each one names what you will have when it is finished, and how to tell.' }),
      el('ol', { class: 'actions' }, r.actions.map(function (a) {
        return el('li', { class: 'action' }, [
          el('span', { class: 'action__n', 'aria-hidden': 'true' }),
          el('div', { class: 'action__body' }, [
            el('p', { class: 'action__what', text: a.what }),
            el('dl', { class: 'meta' }, [
              el('div', {}, [el('dt', { text: 'Why' }), el('dd', { text: a.why })]),
              el('div', {}, [el('dt', { text: 'You get' }), el('dd', { text: a.deliverable })]),
              el('div', {}, [el('dt', { text: 'Verify' }), el('dd', { class: 'verify', text: a.verify })]),
            ]),
          ]),
        ]);
      })),
    ]);
  }

  function sectionPrompt(r) {
    var box = el('div', { class: 'promptbox' }, [
      el('div', { class: 'promptbox__head' }, [
        el('span', { class: 'promptbox__title', text: r.prompt.title }),
        el('button', { class: 'btn btn--sm btn--ghost', type: 'button', id: 'copy-prompt', onclick: function () { doCopy(r.prompt.text, 'prompt-status', 'starter_prompt_copied'); } }, ['Copy prompt']),
      ]),
      el('pre', { class: 'promptbox__body' }, [el('code', { text: r.prompt.text })]),
    ]);
    return el('section', { class: 'section' }, [
      el('h2', { class: 'h-2', text: 'Your free starter Claude Code prompt' }),
      el('p', { class: 'small dim prose', text: 'Paste this into Claude Code in your project folder. It reads and reports; it changes nothing. It is yours to keep and edit whether or not you buy anything.' }),
      box,
      el('p', { class: 'status', id: 'prompt-status', role: 'status', 'aria-live': 'polite' }),
      el('div', { id: 'prompt-fallback' }),
    ]);
  }

  function sectionToolkit(r) {
    var kids = [];
    if (r.primary) {
      var p = r.primary.product;
      kids.push(el('div', { class: 'card' }, [
        el('div', { class: 'card__head' }, [
          el('p', { class: 'eyebrow', text: r.primary.deEmphasised ? 'When you are ready' : 'Your recommended toolkit' }),
          el('h2', { class: 'h-3', text: p.title }),
          el('p', { class: 'card__price', text: r.primary.priceText }),
        ]),
        el('p', { class: 'small muted', text: r.primary.fit }),
        el('ul', { class: 'card__list' }, p.benefits.slice(0, 3).map(function (b) { return el('li', {}, [el('span', { text: b })]); })),
        el('p', { class: 'small muted' }, [el('strong', { text: 'Free plan vs the product. ' }), el('span', { text: r.primary.freeVsPaid })]),
        el('p', { class: 'small muted' }, [el('strong', { text: 'You need first. ' }), el('span', { text: p.prerequisites })]),
        ctaLink(p, r.primary.cta, 'primary_recommendation', r.primary.deEmphasised),
        el('p', { class: 'limit', text: r.primary.limitation }),
      ]));
    } else if (r.mode === 'use_what_you_own') {
      kids.push(el('div', { class: 'card' }, [
        el('p', { class: 'eyebrow', text: 'Nothing to buy' }),
        el('h2', { class: 'h-3', text: 'You already have the right product' }),
        el('p', { class: 'small muted', text: 'The plan on this page is how to use it. If you want a refresher on the workflow it belongs to, the free resource below covers the same ground.' }),
      ]));
    } else {
      kids.push(el('div', { class: 'card' }, [
        el('p', { class: 'eyebrow', text: 'No product recommended' }),
        el('h2', { class: 'h-3', text: 'Your answers do not justify a purchase yet' }),
        el('p', { class: 'small muted', text: 'Buying something now would be a guess. Work the three actions, then come back — the routing is deterministic, so a sharper answer produces a specific recommendation.' }),
      ]));
    }

    if (r.complementary) {
      var c = r.complementary.product;
      kids.push(el('div', { class: 'card card--flat' }, [
        el('p', { class: 'eyebrow', text: 'Optional, and only if the second problem is real' }),
        el('h3', { class: 'h-3', text: c.title }),
        el('p', { class: 'card__price', text: r.complementary.priceText }),
        el('p', { class: 'small muted', text: r.complementary.why }),
        ctaLink(c, 'View the ' + c.shortName, 'complementary_recommendation', true),
      ]));
    }

    if (r.offerBundle) {
      kids.push(bundleCard(r));
    }

    kids.push(comparisonPanel(r));
    kids.push(el('p', { class: 'disclosure', text: 'SiteBuilderStack makes this planner and sells these products. Prices were last verified on ' + (r.priceState.verifiedOn || 'an unknown date') + '; the product page is always the authority.' }));
    return el('section', { class: 'section', style: 'gap:1.25rem' }, kids);
  }

  function bundleCard(r) {
    var b = C.byId['complete-stack'];
    return el('div', { class: 'card' }, [
      el('p', { class: 'eyebrow', text: 'Cheaper for what you named' }),
      el('h3', { class: 'h-3', text: b.title }),
      el('p', { class: 'card__price', text: R.priceText(C, b, r.priceState) }),
      el('p', { class: 'small muted', text: r.bundle.statement }),
      ctaLink(b, 'View the ' + b.shortName, 'bundle_comparison', false),
    ]);
  }

  /* The comparison is available on demand, never eight buttons by default.
     Ticking products recalculates the bundle arithmetic honestly. */
  function comparisonPanel(r) {
    var chosen = (r.bundle.selected || []).slice();
    var out = el('div', { class: 'more__body' });
    var details = el('details', { class: 'more' }, [
      el('summary', { text: 'Compare the bundle, and see every product' }),
      out,
    ]);

    function redraw() {
      clear(out);
      var cmp = R.bundleComparison(C, chosen, r.ownership.owned, r.priceState);
      out.appendChild(el('p', { class: 'small dim', text: 'Tick what you genuinely expect to use in the next few months. The comparison is arithmetic, not a recommendation.' }));
      var rows = C.bundleMembers.map(function (id) {
        var p = C.byId[id];
        var ownedAlready = r.ownership.owned.indexOf(id) !== -1;
        return optionRow('checkbox', 'cmp[]', id, p.shortName + ' — ' + R.priceText(C, p, r.priceState), ownedAlready ? 'You said you own this' : null, chosen.indexOf(id) !== -1, function (ev) {
          chosen = ev.target.checked ? chosen.concat([id]) : chosen.filter(function (x) { return x !== id; });
          redraw();
        });
      });
      out.appendChild(el('div', { class: 'q__opts' }, rows));
      var maths = el('div', { class: 'maths' }, []);
      if (cmp.individualTotal !== null) {
        maths.appendChild(el('div', { class: 'maths__row' }, [el('span', { text: 'Those you do not own, individually' }), el('span', { text: R.fmt(cmp.individualTotal, 'USD') })]));
        maths.appendChild(el('div', { class: 'maths__row' }, [el('span', { text: 'Complete Site Builder Stack' }), el('span', { text: R.fmt(cmp.bundlePrice, 'USD') })]));
      }
      maths.appendChild(el('p', { class: 'maths__verdict small', text: cmp.statement || 'Tick at least one product to compare.' }));
      out.appendChild(maths);
      out.appendChild(el('p', { class: 'small dim', text: C.bundleNote }));

      out.appendChild(el('h4', { class: 'eyebrow', style: 'margin-top:.75rem', text: 'Every product, for reference' }));
      var wrap = el('div', { class: 'tablewrap' });
      var table = el('table', { class: 'table' }, [
        el('thead', {}, [el('tr', {}, [el('th', { text: 'Product' }), el('th', { text: 'For' }), el('th', { text: 'Price' })])]),
        el('tbody', {}, C.raw.products.map(function (p) {
          return el('tr', {}, [
            el('td', {}, [el('a', { href: AN.tag(p.url, 'product_comparison'), target: '_blank', rel: 'noopener', text: p.shortName, onclick: function () { AN.track('product_cta_clicked', { product_id: p.id, cta_placement: 'product_comparison' }); } })]),
            el('td', { text: p.useCase }),
            el('td', { class: 'num', text: R.priceText(C, p, r.priceState) }),
          ]);
        })),
      ]);
      wrap.appendChild(table);
      out.appendChild(wrap);
    }
    redraw();
    return details;
  }

  function ctaLink(product, text, placement, quiet) {
    /* A click from the worked example is not a click from someone's own plan,
       so it gets its own placement and stays separable in the campaign report. */
    if (state.isExample) placement = 'example_result';
    return el('a', {
      class: 'btn' + (quiet ? ' btn--ghost' : '') + ' btn--block',
      href: AN.tag(product.url, placement),
      target: '_blank', rel: 'noopener',
      'data-cta': placement,
      onclick: function () { AN.track('product_cta_clicked', { product_id: product.id, cta_placement: placement }); },
    }, [text]);
  }

  function sectionFreeStep(r) {
    if (!r.freeStep) return null;
    var f = r.freeStep.resource;
    return el('section', { class: 'section' }, [
      el('h2', { class: 'h-2', text: 'A free next step' }),
      el('p', { class: 'prose muted', text: r.freeStep.why }),
      el('p', {}, [
        el('a', {
          class: 'btn btn--ghost', href: AN.tag(f.url, 'free_next_step'), target: '_blank', rel: 'noopener',
          'data-free': f.id,
          onclick: function () { AN.track('free_resource_clicked', { cta_placement: 'free_next_step' }); },
        }, [f.title + ' →']),
      ]),
    ]);
  }

  function sectionControls(r) {
    var acts = [
      el('button', { class: 'btn btn--ghost btn--sm', type: 'button', id: 'copy-plan', onclick: function () { doCopy(R.toMarkdown(r, CAT), 'plan-status', null); } }, ['Copy action plan']),
      el('button', { class: 'btn btn--ghost btn--sm', type: 'button', id: 'export-plan', hidden: !downloads, onclick: function () { doExport(r); } }, ['Export as Markdown']),
      CFG.SHARE_URL ? el('button', { class: 'btn btn--ghost btn--sm', type: 'button', id: 'share', onclick: sharePlanner }, ['Share the planner']) : null,
      el('button', { class: 'btn btn--quiet btn--sm', type: 'button', id: 'again', onclick: reset }, ['Start again']),
    ];
    var kids = [
      el('h2', { class: 'h-2', text: 'Take it with you' }),
      el('div', { class: 'toolbar' }, acts),
      el('p', { class: 'status', id: 'plan-status', role: 'status', 'aria-live': 'polite' }),
      el('div', { id: 'plan-fallback' }),
    ];
    if (!downloads) {
      kids.push(el('p', { class: 'small dim', text: 'File export is not available in this view, so it is not offered. Copy the action plan instead — it is the same Markdown.' }));
    }
    if (r.primary) {
      kids.push(el('div', { style: 'margin-top:1.25rem' }, [
        el('p', { class: 'small muted', text: 'If the plan above is the work you are about to do, the ' + r.primary.product.shortName + ' is the complete version of it.' }),
        el('p', { style: 'margin-top:.6rem' }, [
          el('a', {
            class: 'btn btn--ghost', href: AN.tag(r.primary.product.url, 'recommendation_repeat'), target: '_blank', rel: 'noopener',
            onclick: function () { AN.track('product_cta_clicked', { product_id: r.primary.id, cta_placement: 'recommendation_repeat' }); },
          }, [r.primary.cta]),
        ]),
      ]));
    }
    kids.push(measurementPanel());
    return el('section', { class: 'section' }, kids);
  }

  function measurementPanel() {
    return el('details', { class: 'more' }, [
      el('summary', { text: 'What this page measures' }),
      el('div', { class: 'more__body' }, [
        el('p', { class: 'small muted', text: 'Nothing is transmitted. ' + AN.remoteReason }),
        el('p', { class: 'small muted', text: 'Your answers, what you own and anything you copy stay in this browser tab and are not written anywhere. Reloading the page loses them, which is deliberate.' }),
        el('p', { class: 'small muted', text: 'A local debug journal records event names only — ' + AN.EVENTS.length + ' possible names, with at most a product id and a link placement. It counts what this one browser did. It is not analytics and it is not a visitor count.' }),
        el('p', { class: 'small dim', text: 'Links to sitebuilderstack.com carry campaign parameters (' + AN.CAMPAIGN.utm_campaign + ') and a fixed placement name, so the store can see that a visit came from this planner. No answer is ever put in a link.' }),
        el('button', { class: 'btn btn--quiet btn--sm', type: 'button', onclick: function (e) {
          var box = e.target.nextElementSibling;
          box.hidden = !box.hidden;
          if (!box.hidden) box.textContent = JSON.stringify(AN.journal(), null, 1);
        } }, ['Show the local journal']),
        el('pre', { class: 'promptbox__body small', hidden: true, style: 'border:1px solid var(--border);border-radius:10px' }),
      ]),
    ]);
  }

  function footerNote(r) {
    return el('footer', { class: 'foot' }, [
      el('div', { class: 'foot__in' }, [
        el('p', { class: 'small dim', text: 'This plan is based on the answers you selected. Nothing about your website was scanned, crawled or measured, and none of it is a verified assessment.' }),
        el('p', {}, [
          el('a', {
            href: AN.tag('https://sitebuilderstack.com/', 'footer_brand'), target: '_blank', rel: 'noopener', text: 'sitebuilderstack.com',
          }),
          el('span', { class: 'dim', text: '  ·  Independent product. Not affiliated with, sponsored by, or endorsed by Anthropic. “Claude” and “Claude Code” are trademarks of Anthropic, PBC.' }),
        ]),
      ]),
    ]);
  }

  /* ---------------- copy / export / share ---------------- */
  function setStatus(id, text, isErr) {
    var n = document.getElementById(id);
    if (!n) return;
    n.textContent = text;
    n.className = 'status' + (isErr ? ' status--err' : '');
  }
  function fallbackBox(id, text) {
    var host = document.getElementById(id);
    if (!host) return;
    clear(host);
    var ta = el('textarea', { readonly: true, 'aria-label': 'Text to copy' });
    ta.value = text;
    host.appendChild(el('div', { class: 'copyfallback' }, [
      el('p', { class: 'small dim', text: 'Clipboard access was refused here. The text is selected below — press Ctrl+C (or ⌘C) to copy it.' }),
      ta,
    ]));
    try { ta.focus(); ta.select(); } catch (e) { /* nothing more we can do */ }
  }
  function doCopy(text, statusId, eventName) {
    var fbId = statusId === 'prompt-status' ? 'prompt-fallback' : 'plan-fallback';
    var host = document.getElementById(fbId);
    if (host) clear(host);
    setStatus(statusId, '');
    var done = function () {
      setStatus(statusId, 'Copied.');
      if (eventName) AN.track(eventName, {});
    };
    var failed = function () {
      setStatus(statusId, 'Could not copy automatically.', true);
      fallbackBox(fbId, text);
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, failed);
      } else { failed(); }
    } catch (e) { failed(); }
  }
  function doExport(r) {
    if (!downloads) { setStatus('plan-status', 'File export is not available in this view.', true); return; }
    AN.track('plan_export_requested', {});
    setStatus('plan-status', 'Waiting for you to confirm the download…');
    downloads.save({ filename: 'sitebuilderstack-action-plan.md', data: R.toMarkdown(r, CAT) }).then(function (res) {
      if (res && res.status === 'saved') {
        setStatus('plan-status', 'Saved.');
        AN.track('plan_export_completed', {});
      } else {
        setStatus('plan-status', 'Sent to your device.');
      }
    }, function (err) {
      var code = err && err.code;
      setStatus('plan-status', code === 'declined' ? 'Download cancelled.' : 'The download could not be completed. Use “Copy action plan” instead.', true);
    });
  }
  function sharePlanner() {
    if (!CFG.SHARE_URL) return;
    AN.track('planner_share_clicked', {});
    doCopy(CFG.SHARE_URL, 'plan-status', null);
    setTimeout(function () {
      var n = document.getElementById('plan-status');
      if (n && n.textContent === 'Copied.') n.textContent = 'Planner link copied. It opens the planner itself — your answers are not in it.';
    }, 0);
  }

  /* expose for the browser test harness only */
  window.__planner = { state: state, render: render, decide: function () { return R.decide(state.answers, CAT); } };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
