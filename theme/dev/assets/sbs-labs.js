/* Site Builder Stack — practical labs and Weekly Website Fix challenges.

   Loaded on demand by sbs.js (after sbs-projects.js) when a page contains
   [data-sbs-lab] or [data-sbs-challenge].

   Labs: the fixture is a JSON block rendered by the theme from
   content/labs/*.json. The engine renders one step at a time — evidence,
   a decision, feedback — keeps a score of first-attempt matches, and at the
   end shows the corrected version, offers Save to My Project (a lab record
   plus a short report artifact) and reveals the product link. Wrong answers
   are explained, never hidden; the reader can retry a step. Everything the
   engine puts on the page goes through textContent.

   "Example verified" means the reader's decisions matched the lab's known
   answers. It is recorded as such and never as a claim about their site.

   Challenges: a much smaller surface — a checklist of completion criteria
   the reader self-reports, a copyable prompt, and Save to My Project that
   records the state as self-reported (or example-verified only when the
   challenge links to a lab the reader completed in this browser). */
(function () {
  'use strict';
  var P = window.SBSProjects;
  var track = (window.SBS && window.SBS.track) || function () {};
  var announce = (window.SBS && window.SBS.announce) || function () {};

  function h(tag, attrs, children) {
    var el = document.createElement(tag), k, i, c;
    if (attrs) for (k in attrs) {
      if (k === 'text') el.textContent = attrs[k];
      else if (k === 'on') { for (var ev in attrs.on) el.addEventListener(ev, attrs.on[ev]); }
      else if (attrs[k] === true) el.setAttribute(k, '');
      else if (attrs[k] !== false && attrs[k] != null) el.setAttribute(k, attrs[k]);
    }
    if (children) for (i = 0; i < children.length; i++) { c = children[i]; if (c == null) continue; el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); }
    return el;
  }
  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); }

  /* ---- scoring (pure; tested in scripts/test-engagement.js) -------------- */
  function score(lab, answers) {
    // answers: { stepId: [firstAttempt, secondAttempt, ...] }
    var first = 0, solved = 0, total = lab.steps.length;
    lab.steps.forEach(function (s) {
      var tries = answers[s.id] || [];
      if (tries.length && tries[0] === s.decision.correct) first++;
      if (tries.indexOf(s.decision.correct) !== -1) solved++;
    });
    return { first: first, solved: solved, total: total, verified: solved === total && total > 0 };
  }

  function evidenceNode(e) {
    var body;
    if (e.kind === 'table') {
      var thead = h('thead', null, [h('tr', null, e.columns.map(function (c) { return h('th', { text: c }); }))]);
      var tbody = h('tbody', null, e.rows.map(function (r) { return h('tr', null, r.map(function (c) { return h('td', { text: c }); })); }));
      body = h('div', { 'class': 'sbs-lab__table' }, [h('table', null, [thead, tbody])]);
    } else {
      body = h('pre', { 'class': 'sbs-lab__pre', tabindex: '0' }, [e.content]);
    }
    return h('figure', { 'class': 'sbs-lab__ev' }, [h('figcaption', { text: e.title }), body]);
  }

  function initLab(root) {
    var id = root.getAttribute('data-sbs-lab');
    var cfg = root.querySelector('[data-lab-fixture]');
    var app = root.querySelector('[data-lab-app]');
    var stat = root.querySelector('[data-lab-static]');
    if (!cfg || !app) return;
    var lab;
    try { lab = JSON.parse(cfg.textContent); } catch (e) { return; }
    if (!lab || lab.id !== id || !lab.steps) return;
    var ev = {};
    lab.evidence.concat(lab.after).forEach(function (e) { ev[e.id] = e; });
    var eyebrow = root.parentNode.querySelector('[data-lab-eyebrow]');
    if (eyebrow && lab.eyebrow) eyebrow.textContent = lab.eyebrow;

    var state = { step: 0, answers: {}, started: false, done: false, saved: false };
    var payload = { lab: id };

    function reset() {
      state = { step: 0, answers: {}, started: false, done: false, saved: false };
      render(); announce('Lab reset to the start.');
    }

    function header() {
      return h('div', { 'class': 'sbs-lab__scenario' }, [
        h('h2', { text: 'Scenario' }),
        h('p', { text: lab.scenario }),
        h('div', { 'class': 'sbs-lab__sample' }, [
          h('h3', { text: lab.sample.label }),
          h('p', { text: lab.sample.note }),
          lab.sample.artifacts.some(function (a) { return a.url; }) ? h('ul', { 'class': 'sbs-lab__downloads' }, lab.sample.artifacts.filter(function (a) { return a.url; }).map(function (a) { return h('li', null, [h('a', { href: a.url, download: true, text: a.label })]); })) : null
        ]),
        h('h3', { text: 'Starting state' }),
        h('p', { text: lab.starting })
      ]);
    }

    function stepView(i) {
      var s = lab.steps[i], d = s.decision, tries = state.answers[s.id] || [];
      var solved = tries.indexOf(d.correct) !== -1;
      var box = h('section', { 'class': 'sbs-lab__step', 'aria-labelledby': 'lab-step-h' });
      box.appendChild(h('p', { 'class': 'sbs-lab__progress', text: 'Step ' + (i + 1) + ' of ' + lab.steps.length }));
      box.appendChild(h('h2', { id: 'lab-step-h', text: s.title }));
      box.appendChild(h('p', { text: s.instruction }));
      box.appendChild(h('div', { 'class': 'sbs-lab__evidence' }, s.evidence.map(function (eid) { return evidenceNode(ev[eid]); })));
      var fs = h('fieldset', { 'class': 'sbs-lab__decision' }, [h('legend', { text: d.question })]);
      d.options.forEach(function (o, n) {
        var rid = 'lab-' + s.id + '-' + o.id;
        var input = h('input', { type: 'radio', name: 'lab-' + s.id, id: rid, value: o.id, checked: !!(tries.length && tries[tries.length - 1] === o.id), disabled: solved });
        fs.appendChild(h('div', { 'class': 'sbs-lab__opt' }, [input, h('label', { 'for': rid, text: o.label })]));
      });
      var fb = h('div', { 'class': 'sbs-lab__feedback', role: 'status', hidden: true });
      var actions = h('div', { 'class': 'sbs-lab__actions' });
      var checkBtn = h('button', { type: 'button', 'class': 'sbs-btn sbs-btn--primary', text: 'Check my decision', disabled: solved, on: { click: function () {
        var chosen = fs.querySelector('input:checked');
        if (!chosen) { showFeedback(fb, 'Choose one option first.', 'warn'); return; }
        if (!state.started) { state.started = true; track('lab_started', payload); }
        var a = chosen.value;
        tries = state.answers[s.id] = (state.answers[s.id] || []).concat([a]);
        if (a === d.correct) {
          showFeedback(fb, 'Matches the example. ' + d.explain.correct, 'ok');
          Array.prototype.forEach.call(fs.querySelectorAll('input'), function (x) { x.disabled = true; });
          checkBtn.disabled = true; nextBtn.hidden = false; nextBtn.focus();
        } else {
          showFeedback(fb, 'Not what the evidence shows. ' + (d.explain.wrong[a] || 'Look at the evidence again.') + ' Try again — your first answer is what the score records.', 'error');
        }
      } } });
      var nextBtn = h('button', { type: 'button', 'class': 'sbs-btn sbs-btn--primary', text: i + 1 < lab.steps.length ? 'Next step' : 'See the corrected version', hidden: !solved, on: { click: function () { state.step = i + 1; if (state.step >= lab.steps.length) state.done = true; render(); } } });
      actions.appendChild(checkBtn); actions.appendChild(nextBtn);
      if (i > 0) actions.appendChild(h('button', { type: 'button', 'class': 'sbs-btn sbs-btn--ghost', text: 'Previous step', on: { click: function () { state.step = i - 1; render(); } } }));
      box.appendChild(fs); box.appendChild(fb); box.appendChild(actions);
      if (solved) showFeedback(fb, 'Matches the example. ' + d.explain.correct, 'ok');
      return box;
    }

    function showFeedback(fb, text, kind) { fb.textContent = text; fb.hidden = false; fb.className = 'sbs-lab__feedback is-' + kind; }

    function report(sc) {
      var L = ['# ' + lab.title + ' — lab report', '', 'Result: matched the example on ' + sc.first + ' of ' + sc.total + ' decisions at the first attempt; all ' + sc.total + ' resolved.', 'This verifies your decisions against a controlled fixture. It says nothing about your own site.', '', '## Decisions', ''];
      lab.steps.forEach(function (s, i) {
        var tries = state.answers[s.id] || [];
        var label = function (oid) { var o = s.decision.options.filter(function (x) { return x.id === oid; })[0]; return o ? o.label : oid; };
        L.push((i + 1) + '. ' + s.title, '   - First answer: ' + (tries.length ? label(tries[0]) : '—'), '   - Correct: ' + label(s.decision.correct), '   - Why: ' + s.decision.explain.correct, '');
      });
      L.push('## Take it to your own site', '', '- ' + lab.guide.title + ': ' + lab.guide.url, '- ' + lab.module.title + ': ' + lab.module.url, '', '_Generated in the browser on ' + new Date().toISOString().slice(0, 10) + '._');
      return L.join('\n');
    }

    function endView() {
      var sc = score(lab, state.answers);
      if (!state.tracked) { state.tracked = true; track('lab_completed', payload); }
      var box = h('section', { 'class': 'sbs-lab__end', 'aria-labelledby': 'lab-end-h' });
      box.appendChild(h('h2', { id: 'lab-end-h', text: 'The corrected version' }));
      box.appendChild(h('p', { 'class': 'sbs-lab__score', text: 'You matched the example on ' + sc.first + ' of ' + sc.total + ' decisions at the first attempt.' }));
      box.appendChild(h('p', { 'class': 'sbs-lab__caveat', text: 'That verifies your reading of this fixture — “example verified” — not anything about your own site.' }));
      box.appendChild(h('div', { 'class': 'sbs-lab__evidence' }, lab.after.map(function (e) { return evidenceNode(e); })));
      box.appendChild(h('p', { text: lab.closing }));
      var status = h('p', { 'class': 'sbs-lab__feedback', role: 'status', hidden: true });
      var saveBtn = h('button', { type: 'button', 'class': 'sbs-btn sbs-btn--primary', text: state.saved ? 'Saved' : 'Save to My Project', disabled: !P || state.saved, on: { click: function () {
        var r = P.setLab(id, { state: 'example-verified', title: lab.title, url: '/pages/' + lab.handle, score: sc.first, note: sc.first + '/' + sc.total + ' first attempt' });
        var a = P.addArtifact({ kind: 'lab-report', module: 'lab-' + id, title: lab.title + ' — report', text: report(sc), file: 'lab-' + id + '-report.md', url: '/pages/' + lab.handle });
        if (!r.ok || !a.ok) { showFeedback(status, (a.message || 'Could not save.'), 'error'); return; }
        state.saved = true; saveBtn.textContent = 'Saved'; saveBtn.disabled = true;
        showFeedback(status, (a.persisted ? 'Saved to "' + a.project.name + '" in this browser.' : 'Saved for this visit only — this browser is not storing site data.') + ' The lab is recorded as example-verified with your first-attempt score.', a.persisted ? 'ok' : 'warn');
        track('artifact_saved', { module: 'lab-' + id, lab: id });
      } } });
      var actions = h('div', { 'class': 'sbs-lab__actions' }, [
        saveBtn,
        h('a', { 'class': 'sbs-btn sbs-btn--ghost', href: '/pages/my-projects', text: 'Open My Projects' }),
        h('button', { type: 'button', 'class': 'sbs-btn sbs-btn--ghost', text: 'Reset the lab', on: { click: reset } })
      ]);
      box.appendChild(actions); box.appendChild(status);
      box.appendChild(h('div', { 'class': 'sbs-lab__next' }, [
        h('h3', { text: 'Take it to your own site' }),
        h('ul', { 'class': 'sbs-lab__linklist' }, [
          h('li', null, [h('a', { href: lab.module.url, text: lab.module.title })]),
          h('li', null, [h('a', { href: lab.guide.url, text: lab.guide.title }), ' — the guide this lab is drawn from']),
          h('li', null, [h('a', { href: '/products/' + lab.product.handle, text: lab.product.label, on: { click: function () { track('related_product_clicked', { product: lab.product.handle, source: 'lab' }); } } }), ' — ' + lab.product.note])
        ])
      ]));
      return box;
    }

    function render() {
      clear(app);
      if (state.step === 0 && !state.done) app.appendChild(header());
      app.appendChild(state.done ? endView() : stepView(state.step));
      app.hidden = false;
      if (stat) stat.hidden = true;
      var links = root.querySelector('.sbs-lab__links'); if (links) links.hidden = state.done ? false : true;
      if (state.step > 0 || state.done) { var hd = app.querySelector('h2'); if (hd) { hd.setAttribute('tabindex', '-1'); hd.focus(); } }
    }
    render();
  }

  /* ---- challenges ----------------------------------------------------------- */
  function initChallenge(root) {
    var id = root.getAttribute('data-sbs-challenge');
    var title = root.getAttribute('data-sbs-challenge-title') || id;
    var labId = root.getAttribute('data-sbs-challenge-lab') || '';
    var form = root.querySelector('[data-ch-form]');
    var status = root.querySelector('[data-ch-status]');
    var saveBtn = root.querySelector('[data-ch-save]');
    var startBtn = root.querySelector('[data-ch-start]');
    if (!form) return;
    root.classList.add('is-ready');
    var payload = { challenge: id };
    var started = false;
    function say(t, k) { if (!status) return; status.textContent = t; status.hidden = !t; status.className = 'sbs-lab__feedback' + (k ? ' is-' + k : ''); if (t) announce(t); }
    function criteria() { return Array.prototype.map.call(form.querySelectorAll('input[type="checkbox"]'), function (c) { return { text: c.parentNode.textContent.trim(), done: c.checked }; }); }
    function markStarted() { if (started) return; started = true; if (P) P.setChallenge(id, { state: 'in-progress', title: title, url: window.location.pathname }); track('challenge_started', payload); }
    if (startBtn) startBtn.addEventListener('click', function () { markStarted(); say('Recorded as in progress' + (P && P.storageAvailable() ? ' in My Projects.' : ' for this visit.'), 'ok'); startBtn.disabled = true; });
    form.addEventListener('change', markStarted);
    if (saveBtn) saveBtn.addEventListener('click', function () {
      if (!P) return;
      var cs = criteria(), done = cs.filter(function (c) { return c.done; }).length, all = done === cs.length && cs.length > 0;
      var note = form.querySelector('[name="note"]'); note = note ? String(note.value).trim().slice(0, 400) : '';
      var labState = labId && P.active() && P.active().labs[labId] ? P.active().labs[labId].state : '';
      var state = all ? 'self-reported' : 'in-progress';
      var r = P.setChallenge(id, { state: state, title: title, url: window.location.pathname, note: done + '/' + cs.length + ' criteria' + (note ? ' — ' + note : '') + (labState === 'example-verified' ? ' — linked lab example-verified' : '') });
      if (!r.ok) { say('Could not save.', 'error'); return; }
      var L = ['# ' + title + ' — completion record', '', 'State: ' + (all ? 'self-reported complete' : 'in progress') + ' (' + done + ' of ' + cs.length + ' criteria)', 'Recorded: ' + new Date().toISOString().slice(0, 10), '', '## Criteria', ''];
      cs.forEach(function (c) { L.push('- [' + (c.done ? 'x' : ' ') + '] ' + c.text); });
      if (note) L.push('', '## Notes', '', note);
      L.push('', '_Self-reported: what you told this page. Nothing here was checked by the site. Keep the evidence (screenshots, inbox capture, logs) with your own records; do not paste secrets into this note._');
      var a = P.addArtifact({ kind: 'challenge-record', module: 'challenge-' + id, title: title + ' — record', text: L.join('\n'), file: 'weekly-fix-' + id + '.md', url: window.location.pathname });
      if (!a.ok) { say(a.message || 'Could not save.', 'error'); return; }
      say((a.persisted ? 'Saved to "' + a.project.name + '".' : 'Saved for this visit only — this browser is not storing site data.') + (all ? ' Recorded as self-reported complete.' : ' Recorded as in progress (' + done + ' of ' + cs.length + ').'), a.persisted ? 'ok' : 'warn');
      if (all) track('challenge_completed', payload);
      track('artifact_saved', { module: 'challenge-' + id, challenge: id });
    });
    // Export a redacted completion summary: criteria and dates only, no notes.
    var exportBtn = root.querySelector('[data-ch-export]');
    if (exportBtn) exportBtn.addEventListener('click', function () {
      var cs = criteria();
      var L = ['# ' + title + ' — completion summary (redacted)', '', 'Date: ' + new Date().toISOString().slice(0, 10), 'Criteria met: ' + cs.filter(function (c) { return c.done; }).length + ' of ' + cs.length, ''];
      cs.forEach(function (c) { L.push('- [' + (c.done ? 'x' : ' ') + '] ' + c.text); });
      L.push('', '_Self-reported. Contains no site names, URLs, notes or evidence._');
      if (P && P.download('weekly-fix-' + id + '-summary.md', L.join('\n'))) track('artifact_exported', { module: 'challenge-' + id, challenge: id });
      else say('The browser blocked the download.', 'error');
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll('[data-sbs-lab]'), initLab);
  Array.prototype.forEach.call(document.querySelectorAll('[data-sbs-challenge]'), initChallenge);
  window.SBSLabs = { score: score };
})();
