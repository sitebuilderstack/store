/* Digital Product Page Builder — the twelve-section template, as a tool.
 *
 * Fill the sections, watch the copy assemble, and see which checks still fail.
 * No network. Nothing is saved anywhere; that is stated on the page.
 *
 * The checks are deliberately the mechanical ones — is the section present,
 * does it name a prerequisite, is there a preview — because those are the ones
 * a tool can answer honestly. It does not grade prose.
 */
(function () {
  'use strict';

  var SECTIONS = [
    { id: 'name', label: 'Product name', hint: 'The name as it appears on the page.', rows: 2 },
    { id: 'headline', label: 'Outcome headline', rows: 2,
      hint: 'What the buyer will be able to do. Not the file count, not "ultimate".' },
    { id: 'summary', label: 'Short description', rows: 3,
      hint: 'Who it is for, the problem in their words, and the mechanism.' },
    { id: 'benefits', label: 'Three concrete benefits', rows: 4,
      hint: 'One per line. Test: could a competitor paste the identical line on their page? Then it says nothing.' },
    { id: 'preview', label: 'Genuine preview', rows: 3,
      hint: 'The real artefact a stranger could judge in thirty seconds. An output, not a folder tree.' },
    { id: 'deliverables', label: 'What you receive', rows: 3,
      hint: 'File types, counts, formats, size. Counts belong HERE, with context — not in the headline.' },
    { id: 'firstuse', label: 'First twenty minutes', rows: 4,
      hint: 'What to open, what to supply, what to run, what to expect. If you cannot write step 4 concretely, the product is not ready to sell.' },
    { id: 'requirements', label: 'What the buyer needs already', rows: 3,
      hint: 'Software, runtime with a version, access, skill. "No dependencies" is almost always false.' },
    { id: 'licence', label: 'Licence and delivery', rows: 3,
      hint: 'When the file arrives, who may use it, whether client work is included, and a LINK to the refund policy rather than a paraphrase.' },
    { id: 'limits', label: 'What this does not do', rows: 3,
      hint: 'A page that names a limitation is more believable than one that does not.' },
    { id: 'faqs', label: 'FAQs', rows: 4,
      hint: 'Three to six. Each answers something a buyer asks before paying, not something invented to hold a keyword.' },
    { id: 'close', label: 'Final purchase action', rows: 2,
      hint: 'What it is, the live price, the same button label, THIS product.' }
  ];

  var EXAMPLE = {
    name: 'Claude Code Conversion & Revenue Optimization Toolkit',
    headline: 'Find where visitors get stuck, decide what to fix first, and check whether the fix worked.',
    summary: 'For developers and founders who own a site that gets traffic and does not turn enough of it into revenue. The honest answer to "why" usually needs evidence nobody has collected. Thirteen modules that separate the audit from the plan, the plan from the change, and the change from the claim that it worked.',
    benefits: 'Findings carry evidence and an honesty label: proven bug, strong heuristic, experiment opportunity, or insufficient data.\nThe experimentation module checks whether your traffic could detect the effect before it designs a test, and stops if it cannot.\nAudits never fix in the same run, so a finding leaves a report rather than an unreviewed diff across thirty files.',
    preview: 'One complete finding from the master audit: the observed problem, the evidence line, the honesty label, the proposed change, and how the change would be validated. Rendered as readable text, not a screenshot.',
    deliverables: 'One ZIP. 99 files, 213 KB, all plain Markdown. Thirteen modules, 70 workflows, 68 commands, six report templates and four worked examples. A published SHA-256 checksum accompanies the download.',
    firstuse: '1. Open START-HERE.md.\n2. Supply the site URL and whatever analytics you already have.\n3. Run the master conversion audit in read-only mode.\n4. Expect a findings list with an evidence line and an honesty label on each.\n5. Review the labels before acting — "insufficient data" means exactly that.',
    requirements: 'Claude Code, and a live site that already receives traffic. Plain Markdown; nothing to install. If nobody is arriving yet, this is the wrong product — fix distribution first.',
    licence: 'Delivered as a download link immediately after checkout. Licensed to one person for unlimited projects including client work. Not to be redistributed or resold. Refunds: see the store policy, linked — not summarised here.',
    limits: 'No workflow predicts a percentage lift, because nobody can know that in advance.\nIt refuses manipulative tactics — countdowns, fake stock warnings, invented scarcity — by name.\nIt will not help a site nobody has found yet.',
    faqs: 'Do I need Claude Code? Yes. This is a set of workflows you run inside it.\nHow much traffic do I need? The experimentation module gives thresholds and says plainly when testing is not possible.\nCan I use it for client work? Yes, under a single-person licence.',
    close: 'Thirteen modules for finding where the traffic goes and deciding what to fix first. One payment, instant download.'
  };

  var data = {};
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
  var val = function (id) { return (data[id] || '').trim(); };
  var lines = function (id) { return val(id).split('\n').map(function (s) { return s.trim(); }).filter(Boolean); };

  /* Mechanical checks only. A tool can tell you the requirements section is
     empty; it cannot tell you the prose is any good, and pretending otherwise
     would be the same fabrication the guide argues against. */
  var CHECKS = [
    ['Has an outcome headline', function () { return val('headline').length > 10; }],
    ['Headline is not a file count', function () {
      var h = val('headline');
      return h.length > 10 && !/^\s*\d[\d,]*\s*(files?|words?|pages?|prompts?)/i.test(h) && !/\bultimate\b/i.test(h);
    }],
    ['Names who it is for', function () { return /\bfor\b/i.test(val('summary')) && val('summary').length > 40; }],
    ['Exactly three benefits', function () { return lines('benefits').length === 3; }],
    ['Has a genuine preview', function () { return val('preview').length > 30; }],
    ['Preview is output, not packaging', function () {
      var p = val('preview');
      return p.length > 30 && !/^(a )?(folder|file) (tree|list)/i.test(p);
    }],
    ['States what the buyer receives', function () { return val('deliverables').length > 20; }],
    ['Has a first-use walkthrough', function () { return lines('firstuse').length >= 3; }],
    ['States prerequisites', function () { return val('requirements').length > 20; }],
    ['Does not claim "no dependencies"', function () { return !/no dependencies/i.test(val('requirements')); }],
    ['States licence and delivery', function () { return val('licence').length > 20; }],
    ['Links the refund policy rather than paraphrasing', function () {
      var l = val('licence');
      return l.length > 20 && /polic/i.test(l);
    }],
    ['Names at least one limitation', function () { return val('limits').length > 20; }],
    ['Has at least three FAQs', function () { return lines('faqs').length >= 3; }],
    ['Has a closing purchase action', function () { return val('close').length > 15; }],
    ['No unsupported guarantee', function () {
      var all = Object.keys(data).map(function (k) { return data[k] || ''; }).join(' ');
      return !/\b(we|this product|this toolkit) guarantees?\b|guaranteed (results|rankings?|revenue|increase)|\bis guaranteed to\b/i.test(all);
    }],
    ['No predicted percentage lift', function () {
      var all = Object.keys(data).map(function (k) { return data[k] || ''; }).join(' ');
      return !/\b\d+\s*% (increase|lift|more|uplift|improvement)/i.test(all);
    }],
    ['No price typed into the copy', function () {
      var all = Object.keys(data).map(function (k) { return data[k] || ''; }).join(' ');
      return !/[$£€]\s?\d+(\.\d{2})?/.test(all);
    }]
  ];

  function markdown() {
    var L = [];
    if (val('name')) L.push('# ' + val('name'), '');
    if (val('headline')) L.push('> ' + val('headline'), '');
    if (val('summary')) L.push(val('summary'), '');
    if (lines('benefits').length) {
      L.push('## Why this one', '');
      lines('benefits').forEach(function (b) { L.push('- ' + b); });
      L.push('');
    }
    if (val('preview')) L.push('## What it produces', '', val('preview'), '');
    if (val('deliverables')) L.push('## What you receive', '', val('deliverables'), '');
    if (lines('firstuse').length) {
      L.push('## Your first twenty minutes', '');
      lines('firstuse').forEach(function (s) { L.push(s.replace(/^\d+[.)]\s*/, '- ')); });
      L.push('');
    }
    if (val('requirements')) L.push('## What you need already', '', val('requirements'), '');
    if (val('licence')) L.push('## Licence and delivery', '', val('licence'), '');
    if (lines('limits').length) {
      L.push('## What this does not do', '');
      lines('limits').forEach(function (s) { L.push('- ' + s); });
      L.push('');
    }
    if (lines('faqs').length) {
      L.push('## Questions', '');
      lines('faqs').forEach(function (s) {
        var i = s.indexOf('?');
        if (i > 0) L.push('**' + s.slice(0, i + 1) + '** ' + s.slice(i + 1).trim(), '');
        else L.push(s, '');
      });
    }
    if (val('close')) L.push('## Get it', '', val('close'), '');
    L.push('---', '', 'Price and purchase action render from the live product — never typed into this copy.',
      '', 'Drafted with the Digital Product Page Builder from SiteBuilderStack.',
      'https://sitebuilderstack.com/blogs/guides/shopify-digital-product-page-template', '');
    return L.join('\n');
  }

  function renderChecks() {
    var host = clear($('checks')), pass = 0;
    CHECKS.forEach(function (c) {
      var ok = false;
      try { ok = !!c[1](); } catch (e) { ok = false; }
      if (ok) pass++;
      host.appendChild(el('li', { class: ok ? 'is-ok' : 'is-no' }, [
        el('span', { class: 'mark', 'aria-hidden': 'true', text: ok ? '✓' : '○' }),
        el('span', { text: c[0] })
      ]));
    });
    var chip = $('score');
    chip.textContent = pass + ' / ' + CHECKS.length;
    chip.className = 'chip' + (pass === CHECKS.length ? ' chip--ok' : pass > CHECKS.length / 2 ? ' chip--warn' : '');
  }

  function refresh() {
    $('preview').textContent = markdown();
    renderChecks();
  }

  function renderFields() {
    var host = clear($('fields'));
    SECTIONS.forEach(function (s, i) {
      var ta = el('textarea', {
        id: 'f-' + s.id, rows: s.rows,
        oninput: function (e) { data[s.id] = e.target.value; refresh(); }
      });
      ta.value = data[s.id] || '';
      host.appendChild(el('div', { class: 'card' }, [
        el('div', { class: 'field' }, [
          el('label', { class: 'lbl', for: 'f-' + s.id, text: (i + 1) + '. ' + s.label }),
          el('p', { class: 'small dim', text: s.hint }),
          ta
        ])
      ]));
    });
  }

  function setStatus(m, err) {
    var s = $('status'); s.textContent = m;
    s.className = 'status' + (err ? ' status--err' : '');
  }

  $('example').addEventListener('click', function () {
    data = JSON.parse(JSON.stringify(EXAMPLE));
    renderFields(); refresh();
    setStatus('Loaded a real product as a worked example. Every claim in it is verifiable on its product page.');
  });
  $('reset').addEventListener('click', function () {
    data = {}; renderFields(); refresh(); setStatus('');
    $('top').focus({ preventScroll: true }); window.scrollTo(0, 0);
  });

  $('copy').addEventListener('click', function () {
    var text = markdown();
    clear($('fallback'));
    var fail = function () {
      setStatus('Could not copy automatically.', true);
      var ta = el('textarea', { readonly: true, rows: 10, 'aria-label': 'Markdown to copy', style: 'width:100%' });
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
    downloads.save({ filename: 'product-page-copy.md', data: markdown() }).then(
      function (r) { setStatus(r && r.status === 'saved' ? 'Saved.' : 'Sent to your device.'); },
      function (e) { setStatus(e && e.code === 'declined' ? 'Download cancelled.' : 'The download could not be completed. Use “Copy Markdown” instead.', true); });
  });

  if (window.claude && typeof window.claude.use === 'function') {
    try {
      window.claude.use('downloads').then(function (d) {
        downloads = d; $('download').hidden = !d; $('dl-note').hidden = !!d;
      }).catch(function () { $('dl-note').hidden = false; });
    } catch (e) { $('dl-note').hidden = false; }
  } else { $('dl-note').hidden = false; }

  /* Opens with the example filled in, so the first frame shows what the tool
     does rather than twelve empty boxes. */
  data = JSON.parse(JSON.stringify(EXAMPLE));
  renderFields();
  refresh();
})();
