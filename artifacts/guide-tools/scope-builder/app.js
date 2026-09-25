/* Website Scope Builder — the template from the guide, as a tool.
 *
 * The one idea it enforces: a blank field becomes a visible TBD with an owner,
 * never an invented fact. The "gaps" panel is not a score to get to zero; it
 * is the open-questions list the guide argues is the most useful section in
 * the document.
 *
 * No network. Nothing is stored. Client notes should be sanitised before they
 * are pasted anywhere, and the page says so.
 */
(function () {
  'use strict';

  var FIELDS = [
    { id: 'client', label: 'Client', rows: 1, tbd: 'the client’s legal name', owner: 'You' },
    { id: 'project', label: 'Project name', rows: 1, tbd: 'a short project name', owner: 'You' },
    { id: 'approver', label: 'Approver', rows: 1, owner: 'Client',
      tbd: 'ONE named person who can approve', hint: 'One person. If two people can approve, two people can disagree afterwards.' },
    { id: 'objectives', label: 'Objectives', rows: 3, owner: 'Client',
      tbd: 'what success means to the client', hint: 'One per line. Avoid anything the website cannot influence, like a ranking position.' },
    { id: 'pages', label: 'Pages', rows: 5, owner: 'Client',
      tbd: 'the page list', hint: 'One per line. The count is the number everything else keys off.' },
    { id: 'requirements', label: 'Functional requirements', rows: 4, owner: 'Client',
      tbd: 'what the site must do', hint: 'One per line, each written so it can be demonstrated. If you cannot say how it would be shown working, it is a question, not a requirement.' },
    { id: 'exclusions', label: 'Exclusions', rows: 4, owner: 'You',
      tbd: 'what is NOT included', hint: 'One per line. Everything the client said “maybe” or “eventually” about belongs here by name.' },
    { id: 'clientinputs', label: 'Client responsibilities', rows: 4, owner: 'Client',
      tbd: 'what the client must supply', hint: 'One per line. Add a date if you have one — these are what a schedule actually rests on.' },
    { id: 'rounds', label: 'Review rounds', rows: 2, owner: 'You',
      tbd: 'how many rounds, and what a round is', hint: '“A few” is two to you and five to them. Define what a round is, not just how many.' },
    { id: 'acceptance', label: 'Acceptance criteria', rows: 4, owner: 'You',
      tbd: 'how both sides know it is done', hint: 'One per line, observable by someone who was not in the meetings.' },
    { id: 'assumptions', label: 'Assumptions', rows: 3, owner: 'You',
      tbd: 'what you decided without being told', hint: 'One per line. These are the things that quietly become disputes.' },
    { id: 'questions', label: 'Open questions', rows: 3, owner: 'Client',
      tbd: 'what you still need to ask', hint: 'One per line. An empty list here usually means they were not looked for.' }
  ];

  var EXAMPLE = {
    client: 'Harbourline Physiotherapy Ltd (FICTIONAL EXAMPLE)',
    project: 'Website rebuild',
    approver: 'R. Okonkwo (Owner). Sole approver.',
    objectives: 'The practice can update the class timetable without contacting a developer.\nEnquiries arrive by a tracked route rather than only by phone.\nThe site is accurate about both clinics: addresses, hours, and who works where.',
    pages: 'Home\nAbout\nOur team\nServices (index)\nMusculoskeletal physiotherapy\nSports rehabilitation\nPost-operative rehabilitation\nClass timetable\nContact',
    requirements: 'The enquiry form sends to one named address — shown by a test submission the approver confirms receiving.\nThe form rejects an empty required field with a visible message — shown by submitting empty.\nThe practice can edit the timetable unaided — shown by the manager editing a class, observed.\nEvery old URL resolves in one hop — shown by testing the redirect map.',
    exclusions: 'Online booking or appointment scheduling\nOnline payments of any kind\nA patient portal, login, or any handling of patient data\nA blog, including its layout and any posts\nCopywriting — all page copy is supplied by the client\nPhotography\nA fourth or subsequent service page\nOngoing SEO work',
    clientinputs: 'Final copy for all 9 pages — by 11 April\nSix practitioner headshots, minimum 1000px — by 11 April\nGA4 property ID and access — by 18 April\nDNS registrar access, or a named person who has it — by 25 April\nBoth clinics’ addresses, hours and phone numbers in writing — by 4 April',
    rounds: '2 per deliverable. A round is one consolidated set of feedback from the approver. Typos and anything that does not match this scope are fixes and are not counted.',
    acceptance: 'All 9 pages exist and are reachable from the navigation.\nEach functional requirement demonstrated to the approver on staging.\nNo page scrolls horizontally at 390px, checked on a real device.\nEvery old URL resolves in one hop.\nThe manager edits a timetable entry unaided, observed once.',
    assumptions: 'No patient or health data is collected anywhere on the site — if wrong, the scope is re-drafted before any work.\nNo vector logo exists; the JPEG is used at its current quality.\nCopy is supplied as editable text, not PDFs or images.',
    questions: 'Which registrar holds the domain, and who can access it?\nIs the timetable one table for both clinics, or one each?\nIs the existing GA4 property still receiving data?'
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
  var spec = function (id) { return FIELDS.filter(function (f) { return f.id === id; })[0]; };

  /* A blank field never disappears. It becomes a TBD with an owner, which is
     the whole argument of the guide. */
  function textOrTbd(id) {
    var v = val(id);
    if (v) return v;
    var f = spec(id);
    return '**TBD** — ' + f.tbd + '. Owner: ' + f.owner + '.';
  }
  function listOrTbd(id) {
    var l = lines(id);
    if (l.length) return l.map(function (s) { return '- ' + s; }).join('\n');
    var f = spec(id);
    return '- **TBD** — ' + f.tbd + '. Owner: ' + f.owner + '.';
  }

  function markdown() {
    var pages = lines('pages');
    var L = [];
    L.push('# Website scope of work — ' + textOrTbd('client'), '');
    L.push('> Operational planning document, not a legal agreement. It records what will be',
           '> built and how both sides know it is finished. It does not replace a contract.', '');
    L.push('## 1. Project summary', '',
           '- **Project:** ' + textOrTbd('project'),
           '- **Approver:** ' + textOrTbd('approver'),
           '- **Version:** v1 — draft for approval', '');
    L.push('## 2. Objectives', '', listOrTbd('objectives'), '');
    L.push('## 3. Deliverables', '',
           '- Designed and built pages — **' + (pages.length || 'TBD') + '**' +
           (pages.length ? '' : ' (the page list is not settled)'),
           '- Responsive implementation across the same pages',
           '- Handoff pack: credentials route, deploy steps, decisions log', '');
    L.push('## 4. Page inventory', '', listOrTbd('pages'), '');
    L.push('## 5. Functional requirements', '', listOrTbd('requirements'), '');
    L.push('## 6. Exclusions', '',
           'Not included in this project:', '', listOrTbd('exclusions'), '');
    L.push('## 7. Client responsibilities', '', listOrTbd('clientinputs'), '',
           'A dependency arriving late moves the dates that depend on it. This is stated now,',
           'not negotiated later.', '');
    L.push('## 8. Review rounds', '', textOrTbd('rounds'), '');
    L.push('## 9. Acceptance criteria', '', listOrTbd('acceptance'), '');
    L.push('## 10. Change-request process', '',
           '1. The request is written down.',
           '2. It is classified against this document: **in scope**, **ambiguous**, or **out of scope**.',
           '3. Out-of-scope items get a written estimate: effort, cost, schedule impact.',
           '4. Nothing starts until the approver says yes in writing.', '',
           'Classification comes before pricing. A process that prices every question teaches',
           'a client to stop asking questions.', '');
    L.push('## 11. Assumptions', '', listOrTbd('assumptions'), '',
           'If one of these turns out to be wrong, annotate it with the date rather than',
           'deleting it.', '');
    L.push('## 12. Open questions', '', listOrTbd('questions'), '');
    L.push('---', '', '**Status:** draft for approval. Not approved. Not a contract.', '',
           'Built with the Website Scope Builder from SiteBuilderStack.',
           'https://sitebuilderstack.com/blogs/guides/website-scope-of-work-template-claude-code', '');
    return L.join('\n');
  }

  /* Not a score. These are the questions the document is currently silent on,
     plus the two risks that cost the most when they are missed. */
  function gaps() {
    var out = [];
    FIELDS.forEach(function (f) {
      if (!val(f.id)) out.push({ ok: false, text: f.label + ' — will print as TBD, owner ' + f.owner });
    });
    var pages = lines('pages').length;
    if (pages) out.push({ ok: true, text: pages + ' page' + (pages === 1 ? '' : 's') + ' in the inventory, which the deliverables count uses' });
    if (lines('exclusions').length) out.push({ ok: true, text: lines('exclusions').length + ' exclusions named' });
    else out.push({ ok: false, text: 'No exclusions — the section that prevents most disputes is empty' });
    if (!lines('assumptions').length) out.push({ ok: false, text: 'No assumptions recorded — you almost certainly made some' });
    var acc = lines('acceptance');
    var vague = acc.filter(function (a) { return /\b(works?|looks?|professional|modern|fast|nice|good)\b/i.test(a) && !/\b(shown|checked|demonstrated|measured|observed|tested)\b/i.test(a); });
    if (vague.length) out.push({ ok: false, text: vague.length + ' acceptance criterion' + (vague.length === 1 ? '' : 'a') + ' may not be observable — add how it is checked' });
    else if (acc.length) out.push({ ok: true, text: 'Acceptance criteria name how each is checked' });
    var all = Object.keys(data).map(function (k) { return data[k] || ''; }).join(' ');
    if (/\banything else\b|\bas (needed|required)\b|\betc\.?\b/i.test(all)) {
      out.push({ ok: false, text: 'Open-ended wording found (“anything else”, “as needed”) — the most expensive phrase in freelance work' });
    }
    if (/\b(penalt|indemnif|liabilit|warrant)/i.test(all)) {
      out.push({ ok: false, text: 'Legal-sounding language found — this is a planning document; leave those to the contract' });
    }
    return out;
  }

  function renderChecks() {
    var list = gaps(), host = clear($('checks'));
    list.forEach(function (g) {
      host.appendChild(el('li', { class: g.ok ? 'is-ok' : 'is-no' }, [
        el('span', { class: 'mark', 'aria-hidden': 'true', text: g.ok ? '✓' : '○' }),
        el('span', { text: g.text })
      ]));
    });
    var open = list.filter(function (g) { return !g.ok; }).length;
    var chip = $('score');
    chip.textContent = open === 0 ? 'nothing outstanding' : open + ' to settle';
    chip.className = 'chip' + (open === 0 ? ' chip--ok' : ' chip--warn');
  }

  function refresh() { $('preview').textContent = markdown(); renderChecks(); }

  function renderFields() {
    var host = clear($('fields'));
    FIELDS.forEach(function (f, i) {
      var ta = el('textarea', { id: 'f-' + f.id, rows: f.rows,
        oninput: function (e) { data[f.id] = e.target.value; refresh(); } });
      ta.value = data[f.id] || '';
      host.appendChild(el('div', { class: 'card' }, [
        el('div', { class: 'field' }, [
          el('label', { class: 'lbl', for: 'f-' + f.id, text: (i + 1) + '. ' + f.label }),
          f.hint ? el('p', { class: 'small dim', text: f.hint }) : null,
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
    data = JSON.parse(JSON.stringify(EXAMPLE)); renderFields(); refresh();
    setStatus('Loaded the fictional Harbourline Physiotherapy project from the guide.');
  });
  $('reset').addEventListener('click', function () {
    data = {}; renderFields(); refresh(); setStatus('');
    $('top').focus({ preventScroll: true }); window.scrollTo(0, 0);
  });

  $('copy').addEventListener('click', function () {
    var text = markdown(); clear($('fallback'));
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
    downloads.save({ filename: 'website-scope-of-work.md', data: markdown() }).then(
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

  data = JSON.parse(JSON.stringify(EXAMPLE));
  renderFields();
  refresh();
})();
