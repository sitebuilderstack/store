/* Answer Engine Optimization Checker.
 *
 * The honest framing, which the page states rather than hides: no answer
 * engine publishes its extraction rules, so nothing here is a mechanic. The
 * checks are the observable, uncontroversial things — is it crawlable, is the
 * answer in the HTML, does a claim survive being lifted out of its paragraph,
 * does the page name its own facts. None of it predicts a citation.
 *
 * No network. Nothing is stored. Everything runs in the tab.
 */
(function () {
  'use strict';

  var FLAGS = [
    ['html', 'The opening text is in the HTML source, not rendered by JavaScript', true],
    ['crawlers', 'robots.txt allows the AI crawlers you want to be cited by (GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended)', true],
    ['nogate', 'No cookie wall, paywall or interstitial covers the answer', true],
    ['llms', 'The site publishes llms.txt or agents.md listing this page', false],
    ['schema', 'The page carries Article or BlogPosting structured data', false],
    ['dated', 'A visible publication or updated date appears on the page', false],
    ['canonical', 'The page is self-canonical and is not a near-duplicate of another page', true]
  ];

  var EXAMPLE = {
    q: 'How do I bulk edit Shopify SEO titles and meta descriptions?',
    title: 'How to Bulk Edit Shopify SEO Titles and Meta Descriptions With Claude Code',
    entity: 'SiteBuilderStack',
    body: 'Editing SEO titles and meta descriptions across a catalogue is five steps, and only one of them involves a machine writing anything: export the current values, draft replacements from facts the product already states, review them one by one and record a decision, apply only the approved rows, then verify what is stored and what renders.\n\nBefore any of that: you may not need an API workflow at all. Shopify’s own bulk editor handles the SEO title and description columns directly, and for thirty products on a quiet afternoon it is the right tool. An API workflow earns its place when the batch is large, recurring, or needs a record of who approved what.\n\nIn the Shopify Admin API, the SEO title and meta description are the two members of the seo field on a product. They are separate from the product title, the body description and the handle, which is why a metadata job should send seo and nothing else.',
    headings: 'Pick the method before you pick the tool\nFour fields that are easy to confuse\nExport, and take a small batch\nDrafting from facts you already have\nThe review, with three real decisions\nApplying only what was approved\nVerifying, and what Google actually promises\nWhen it goes wrong',
    flags: { html: true, crawlers: true, nogate: true, llms: true, schema: true, dated: true, canonical: true }
  };

  var state = { q: '', title: '', entity: '', body: '', headings: '', flags: {} };
  var downloads = null;

  function el(t, a, k) {
    var n = document.createElement(t);
    if (a) Object.keys(a).forEach(function (key) {
      var v = a[key];
      if (v === null || v === undefined || v === false) return;
      if (key === 'class') n.className = v;
      else if (key === 'text') n.textContent = v;
      else if (key.slice(0, 2) === 'on') n.addEventListener(key.slice(2), v);
      else n.setAttribute(key, v === true ? '' : String(v));
    });
    (k || []).forEach(function (c) { if (c) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); return n; }
  var $ = function (i) { return document.getElementById(i); };
  var T = function (s) { return (s || '').trim(); };
  var words = function (s) { return T(s).split(/\s+/).filter(Boolean); };
  var sentences = function (s) {
    return T(s).replace(/\n+/g, ' ').split(/(?<=[.!?])\s+/).map(T).filter(function (x) { return x.length > 2; });
  };
  var headingList = function () {
    return T(state.headings).split('\n').map(T).filter(Boolean);
  };

  /* A claim that cannot be lifted out of its paragraph cannot be quoted. These
     are the openers that make a sentence depend on something not in the
     extract. */
  var DEPENDENT = /^(this|that|these|those|it|they|he|she|there)\b|^(as (mentioned|described|noted|above|we saw))|^(however|therefore|so|but|and|also|then|next|first|second|finally)\b|^(here|below|above)\b/i;

  function firstSelfContained() {
    var ss = sentences(state.body);
    for (var i = 0; i < ss.length; i++) {
      var s = ss[i];
      if (words(s).length < 8) continue;
      if (DEPENDENT.test(s)) continue;
      /* Two sentences read better as an extract than one, when the second does
         not itself depend on something earlier. */
      var next = ss[i + 1];
      if (next && !DEPENDENT.test(next) && words(s).length + words(next).length < 80) return s + ' ' + next;
      return s;
    }
    return '';
  }

  function questionish(h) {
    return /^(how|what|why|when|where|which|who|can|do|does|is|are|should|will)\b/i.test(h) || /\?\s*$/.test(h);
  }

  function checks() {
    var b = T(state.body), q = T(state.q), ttl = T(state.title), ent = T(state.entity);
    var ss = sentences(b), hs = headingList();
    var first120 = words(b).slice(0, 120).join(' ').toLowerCase();
    var qTerms = words(q).map(function (w) { return w.toLowerCase().replace(/[^a-z0-9]/g, ''); })
      .filter(function (w) { return w.length > 3; });
    var lift = firstSelfContained();
    var out = [];

    function add(id, ok, label, why) { out.push({ id: id, ok: ok, label: label, why: why }); }

    add('q', !!q, 'The page has a stated question',
      q ? '' : 'Write the question first. Everything else is judged against it.');

    add('answer-early', !!lift && b.indexOf(lift.slice(0, 40)) < 400,
      'A self-contained answer appears in the opening',
      lift ? '' : 'No sentence in the opening stands on its own. Every one either is too short or starts with a word that points at something the extract will not contain.');

    add('match', qTerms.length > 0 && qTerms.filter(function (w) { return first120.indexOf(w) !== -1; }).length >= Math.ceil(qTerms.length * 0.5),
      'The opening uses the question’s own words',
      'A model matching a query to a passage is matching language. Terms from the question should appear in the first hundred words, naturally.');

    var dependents = ss.slice(0, 6).filter(function (s) { return DEPENDENT.test(s); });
    add('selfcontained', ss.length > 0 && dependents.length <= Math.max(1, Math.floor(ss.length * 0.34)),
      'Most opening sentences survive being lifted',
      dependents.length ? dependents.length + ' of the first sentences start with a dependent word ("' + T(dependents[0]).split(' ')[0] + '…"). Those cannot be quoted without the sentence before them.' : '');

    add('entity', !!ent && (b.toLowerCase().indexOf(ent.toLowerCase()) !== -1 || ttl.toLowerCase().indexOf(ent.toLowerCase()) !== -1),
      'The publisher is named in the text, not just "we"',
      ent ? 'Name the publisher somewhere a model can attribute the claim to. "We" attributes to nobody.' : 'Say who publishes this.');

    /* Specificity is not only digits. "five steps" is exactly as checkable as
       "5 steps", and a named field or product is more specific than either.
       Counting digits alone marked genuinely precise prose as vague. */
    var WORDNUM = /\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|twenty|thirty|forty|fifty|hundred|thousand)\b/gi;
    var specifics =
      (b.match(/\b\d[\d,.]*\b/g) || []).length +
      (b.match(WORDNUM) || []).length +
      (b.match(/`[^`]+`|\b[a-z]+[A-Z][a-zA-Z]+\b/g) || []).length;
    add('specific', specifics >= 3, 'The opening contains specific, checkable detail',
      specifics >= 3 ? '' : 'Counts, versions, dates and named things are what make a passage worth quoting over a competitor\u2019s. Found ' + specifics + '. Vague prose is not extractable.');

    var hedges = (b.match(/\b(might|maybe|possibly|perhaps|arguably|some (?:people|say)|it depends|generally speaking)\b/gi) || []).length;
    add('direct', hedges <= 2, 'The answer is stated, not hedged into vapour',
      hedges > 2 ? hedges + ' hedging phrases in the opening. Qualify where it is honest to, but a passage that never commits to anything gives a model nothing to quote.' : '');

    add('title-q', !!ttl && (questionish(ttl) || (qTerms.length > 0 && qTerms.filter(function (w) { return ttl.toLowerCase().indexOf(w) !== -1; }).length >= 2)),
      'The title reflects the question',
      ttl ? 'The title is where a model first decides whether the page is about the query at all.' : 'Add the page title.');

    var qh = hs.filter(questionish).length;
    add('headings-q', hs.length > 0 && qh >= 1,
      'At least one heading is shaped like a question',
      hs.length ? 'None of your ' + hs.length + ' headings reads as a question. Question-shaped headings give a model a place to anchor a specific answer.' : 'Add your H2 headings.');

    add('headings-n', hs.length >= 3, 'The page has enough structure to navigate',
      hs.length >= 3 ? '' : 'Fewer than three headings. A long passage with no internal structure is hard to extract a specific answer from.');

    var lw = words(lift).length;
    add('lift-length', lw >= 20 && lw <= 90, 'The liftable block is a usable length',
      !lift ? '' : lw < 20 ? 'The strongest self-contained passage is only ' + lw + ' words. Too short to answer anything.' :
        'The strongest passage runs ' + lw + ' words. Long extracts get truncated mid-thought.');

    FLAGS.forEach(function (f) {
      var on = !!state.flags[f[0]];
      var why = '';
      if (!on) {
        if (f[0] === 'html') why = 'If the answer only exists after JavaScript runs, assume it will not be read.';
        else if (f[0] === 'crawlers') why = 'A blocked crawler cannot cite you. Check robots.txt for each agent you care about, and decide deliberately — blocking them is a legitimate choice, but then citation is not a goal.';
        else if (f[0] === 'nogate') why = 'Content behind a consent wall is content a crawler did not see.';
        else if (f[0] === 'llms') why = 'llms.txt and agents.md are an emerging convention, not a standard, and no engine guarantees it reads them. Cheap to publish; do not expect much on its own.';
        else if (f[0] === 'schema') why = 'Structured data does not cause a citation, but it removes ambiguity about author, date and headline.';
        else if (f[0] === 'dated') why = 'A visible date is how a model judges whether the answer is still current.';
        else if (f[0] === 'canonical') why = 'Two near-identical pages compete with each other, and neither wins clearly.';
      }
      add(f[0], on, f[1].replace(/ \(.*\)$/, ''), why);
    });

    return out;
  }

  function slug(s) {
    return T(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
  }

  function report() {
    var cs = checks(), lift = firstSelfContained();
    var pass = cs.filter(function (c) { return c.ok; }).length;
    var L = [];
    L.push('# Answer engine readiness — ' + (T(state.title) || 'untitled page'), '');
    L.push('Question: ' + (T(state.q) || '(not stated)'));
    L.push('Publisher: ' + (T(state.entity) || '(not stated)'));
    L.push('Checks passed: ' + pass + ' of ' + cs.length, '');
    L.push('These checks are informed practice, not published mechanics. No answer');
    L.push('engine discloses its extraction rules, and nothing here predicts a citation.', '');
    L.push('## The block most likely to be lifted', '');
    L.push(lift ? '> ' + lift : '> (none — no sentence in the opening stands on its own)', '');
    var failed = cs.filter(function (c) { return !c.ok; });
    if (failed.length) {
      L.push('## What is in the way', '');
      failed.forEach(function (c) { L.push('- **' + c.label + '**' + (c.why ? ' — ' + c.why : '')); });
      L.push('');
    }
    var passed = cs.filter(function (c) { return c.ok; });
    if (passed.length) {
      L.push('## Already true', '');
      passed.forEach(function (c) { L.push('- ' + c.label); });
      L.push('');
    }
    if (T(state.title)) {
      L.push('## Suggested llms.txt entry', '');
      L.push('- **' + T(state.title) + '** — https://your-domain.example/' + (slug(state.title) || 'page'), '');
      L.push('  ' + (lift ? lift.slice(0, 220) : '(one or two sentences describing what the page answers)'), '');
    }
    var hs = headingList().filter(function (h) { return !/^(how|what|why|when|where|which|who|can|do|does|is|are|should|will)\b/i.test(h) && !/\?$/.test(h); });
    if (hs.length) {
      L.push('## Headings that could be shaped as questions', '');
      hs.slice(0, 6).forEach(function (h) { L.push('- ' + h); });
      L.push('', 'Not all of them should be. A heading becomes a question when a reader would');
      L.push('actually ask it in those words.', '');
    }
    L.push('---', '', 'Checked with the Answer Engine Optimization Checker from SiteBuilderStack.');
    L.push('https://sitebuilderstack.com/blogs/guides/claude-code-technical-seo-audit', '');
    return L.join('\n');
  }

  function render() {
    var cs = checks();
    var host = clear($('checks'));
    cs.forEach(function (c) {
      host.appendChild(el('li', { class: c.ok ? 'is-ok' : 'is-no' }, [
        el('span', { class: 'mark', 'aria-hidden': 'true', text: c.ok ? '✓' : '!' }),
        el('span', {}, [
          el('span', { text: c.label }),
          !c.ok && c.why ? el('span', { class: 'why', text: c.why }) : null
        ])
      ]));
    });
    var pass = cs.filter(function (c) { return c.ok; }).length;
    var chip = $('score');
    chip.textContent = pass + ' / ' + cs.length;
    chip.className = 'chip' + (pass === cs.length ? ' chip--ok' : pass >= cs.length * 0.6 ? ' chip--warn' : ' chip--bad');
    $('lift').textContent = firstSelfContained();
    $('out').textContent = report();
    $('wc').textContent = words(state.body).length + ' words';
  }

  function bindText(id) {
    var n = $(id);
    n.addEventListener('input', function (e) { state[id] = e.target.value; render(); });
  }
  ['q', 'title', 'entity', 'body', 'headings'].forEach(bindText);

  function renderFlags() {
    var host = clear($('flags'));
    FLAGS.forEach(function (f) {
      var cb = el('input', { type: 'checkbox', id: 'flag-' + f[0], checked: !!state.flags[f[0]] || null,
        onchange: function (e) { state.flags[f[0]] = e.target.checked; render(); } });
      host.appendChild(el('label', { class: 'opt', for: 'flag-' + f[0] }, [cb, el('span', { text: f[1] })]));
    });
  }

  function fill(o) {
    state = { q: o.q || '', title: o.title || '', entity: o.entity || '',
      body: o.body || '', headings: o.headings || '', flags: Object.assign({}, o.flags || {}) };
    ['q', 'title', 'entity', 'body', 'headings'].forEach(function (k) { $(k).value = state[k]; });
    renderFlags(); render();
  }

  function setStatus(m, err) {
    var s = $('status'); s.textContent = m;
    s.className = 'status' + (err ? ' status--err' : '');
  }

  $('example').addEventListener('click', function () {
    fill(EXAMPLE);
    setStatus('Loaded a real published page. Its opening was written to be liftable.');
  });
  $('reset').addEventListener('click', function () {
    fill({ flags: {} }); setStatus('');
    $('top').focus({ preventScroll: true }); window.scrollTo(0, 0);
  });

  $('copy').addEventListener('click', function () {
    var text = report(); clear($('fallback'));
    var fail = function () {
      setStatus('Could not copy automatically.', true);
      var ta = el('textarea', { readonly: true, rows: 10, 'aria-label': 'Report to copy', style: 'width:100%' });
      ta.value = text;
      $('fallback').appendChild(el('div', { class: 'field', style: 'margin-top:var(--sp-3)' }, [
        el('p', { class: 'small dim', text: 'Clipboard access was refused here. The text is selected below — press Ctrl+C or ⌘C.' }), ta]));
      try { ta.focus(); ta.select(); } catch (e) {}
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { setStatus('Copied.'); }, fail);
      } else fail();
    } catch (e) { fail(); }
  });

  $('download').addEventListener('click', function () {
    if (!downloads) { setStatus('File download is not available in this view.', true); return; }
    setStatus('Waiting for you to confirm the download…');
    downloads.save({ filename: 'answer-engine-readiness.md', data: report() }).then(
      function (r) { setStatus(r && r.status === 'saved' ? 'Saved.' : 'Sent to your device.'); },
      function (e) { setStatus(e && e.code === 'declined' ? 'Download cancelled.' : 'The download could not be completed. Use “Copy the report” instead.', true); });
  });

  if (window.claude && typeof window.claude.use === 'function') {
    try {
      window.claude.use('downloads').then(function (d) {
        downloads = d; $('download').hidden = !d; $('dl-note').hidden = !!d;
      }).catch(function () { $('dl-note').hidden = false; });
    } catch (e) { $('dl-note').hidden = false; }
  } else { $('dl-note').hidden = false; }

  fill(EXAMPLE);
})();
