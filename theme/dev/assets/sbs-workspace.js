/* Site Builder Stack — My Projects workspace (/pages/my-projects).

   Loaded on demand by sbs.js after sbs-projects.js (the storage core). The
   section (sections/sbs-projects.liquid) renders the landmarks, forms and
   empty states; this file fills them from the browser-local store and wires
   the actions. Everything the reader stored is rendered through
   textContent — never innerHTML — because imported files are untrusted. */
(function () {
  'use strict';
  var P = window.SBSProjects;
  var track = (window.SBS && window.SBS.track) || function () {};
  var announce = (window.SBS && window.SBS.announce) || function () {};
  var root = document.querySelector('[data-sbs-projects]');
  if (!P || !root) return;

  /* ---- tiny DOM helper: attributes and text only, no markup strings ---- */
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
  function q(sel) { return root.querySelector(sel); }
  function clear(el) { while (el && el.firstChild) el.removeChild(el.firstChild); }
  function fmt(ts) { try { return new Date(ts).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }); } catch (e) { return ''; } }
  function fmtTime(ts) { try { return new Date(ts).toLocaleString(); } catch (e) { return ''; } }
  var STATE_LABEL = { 'not-started': 'Not started', 'in-progress': 'In progress', 'read': 'Read / reviewed', 'generated': 'Generated', 'self-reported': 'Self-reported', 'example-verified': 'Verified against example' };
  function pill(state) { return h('span', { 'class': 'sbs-pill sbs-pw__state sbs-pw__state--' + state, text: STATE_LABEL[state] || state }); }
  function say(msg, kind) {
    var s = q('[data-pw-status]'); if (!s) return;
    s.textContent = msg; s.hidden = !msg; s.className = 'sbs-pw__status' + (kind ? ' is-' + kind : '');
    if (msg) announce(msg);
  }

  /* ---- storage notices ------------------------------------------------- */
  function renderStorage() {
    var st = P.load();
    var box = q('[data-pw-storage]'); if (!box) return;
    var msg = '';
    if (!P.storageAvailable()) msg = 'This browser is not letting the site remember data (private window, blocked site data, or storage disabled). Your projects will exist only until you leave this page — export a JSON copy before you go.';
    else if (st.quota) msg = 'The browser refused to store the last change (storage is full). Export a JSON copy now, then delete some saved results.';
    else if (st.recovered) msg = 'The stored projects could not be read and were reset. If you have a JSON export, import it below.';
    box.textContent = msg; box.hidden = !msg;
  }

  /* ---- project switcher -------------------------------------------------- */
  function renderSwitcher() {
    var sel = q('[data-pw-select]'), list = P.list(), a = P.active();
    clear(sel);
    list.forEach(function (p) { sel.appendChild(h('option', { value: p.id, selected: a && a.id === p.id, text: p.name })); });
    var sw = q('[data-pw-switch]'); if (sw) sw.hidden = !list.length;
    q('[data-pw-empty]').hidden = !!list.length;
    q('[data-pw-current]').hidden = !list.length;
    q('[data-pw-count]').textContent = list.length ? (list.length + ' of 25 projects in this browser') : '';
  }

  /* ---- current project --------------------------------------------------- */
  function renderProject() {
    var p = P.active(); if (!p) return;
    q('[data-pw-name]').textContent = p.name;
    q('[data-pw-meta]').textContent = [p.platform !== 'other' ? p.platform : '', p.url, 'last activity ' + fmt(p.updated)].filter(Boolean).join(' · ');
    q('[data-pw-objective]').textContent = p.objective || 'No objective set yet.';
    var mig = q('[data-pw-migrated]'); if (mig) mig.hidden = !p.migratedFrom;
    var f = q('[data-pw-edit]');
    f.elements.name.value = p.name; f.elements.platform.value = p.platform; f.elements.objective.value = p.objective; f.elements.url.value = p.url;
    // continue
    var n = P.nextAction(p), box = q('[data-pw-next]');
    clear(box);
    if (n) box.appendChild(h('a', { href: n.url, 'class': 'sbs-btn sbs-btn--primary', text: n.label, on: { click: function () { track('project_resumed', { kind: n.kind }); } } }));
  }

  function renderTasks() {
    var p = P.active(), ul = q('[data-pw-tasks]'); if (!p) return;
    clear(ul);
    if (!p.tasks.length) { ul.appendChild(h('li', { 'class': 'sbs-pw__empty', text: 'No tasks yet. Add the next thing to check on this site.' })); return; }
    p.tasks.forEach(function (t) {
      var id = 'pw-task-' + t.id;
      ul.appendChild(h('li', { 'class': 'sbs-pw__task' + (t.done ? ' is-done' : '') }, [
        h('input', { type: 'checkbox', id: id, checked: t.done, on: { change: function () { P.toggleTask(p.id, t.id); refresh(); } } }),
        h('label', { 'for': id, text: t.text }),
        h('button', { type: 'button', 'class': 'sbs-pw__x', 'aria-label': 'Remove task: ' + t.text, text: '×', on: { click: function () { P.removeTask(p.id, t.id); refresh(); say('Task removed.'); } } })
      ]));
    });
  }

  function renderArtifacts() {
    var p = P.active(), ul = q('[data-pw-artifacts]'); if (!p) return;
    clear(ul);
    if (!p.artifacts.length) { ul.appendChild(h('li', { 'class': 'sbs-pw__empty', text: 'Nothing saved yet. Every guide with a "Try this on your project" module and every lab can save its result here.' })); return; }
    p.artifacts.forEach(function (a) {
      var pre = h('pre', { 'class': 'sbs-pw__text', hidden: true, text: a.text });
      var toggle = h('button', { type: 'button', 'class': 'sbs-btn sbs-btn--ghost', text: 'Show', 'aria-expanded': 'false', on: { click: function () { var open = pre.hidden; pre.hidden = !open; toggle.textContent = open ? 'Hide' : 'Show'; toggle.setAttribute('aria-expanded', open ? 'true' : 'false'); } } });
      var copy = h('button', { type: 'button', 'class': 'sbs-btn sbs-btn--ghost', text: 'Copy', on: { click: function () { copyText(a.text, copy); track('artifact_copied', { module: a.module, source: 'workspace' }); } } });
      var dl = h('button', { type: 'button', 'class': 'sbs-btn sbs-btn--ghost', text: 'Download', on: { click: function () { if (P.download(a.file, a.text)) track('artifact_exported', { module: a.module, source: 'workspace' }); else say('The browser blocked the download. Use Copy instead.', 'error'); } } });
      var del = h('button', { type: 'button', 'class': 'sbs-btn sbs-btn--ghost', text: 'Delete', on: { click: function () { if (window.confirm('Delete "' + a.title + '" from this project? This cannot be undone.')) { P.removeArtifact(p.id, a.id); refresh(); say('Deleted.'); } } } });
      var meta = [a.module || a.kind, a.guide ? 'from ' + a.guide : '', fmtTime(a.ts)].filter(Boolean).join(' · ');
      ul.appendChild(h('li', { 'class': 'sbs-pw__item' }, [
        h('div', { 'class': 'sbs-pw__item-head' }, [h('strong', { text: a.title }), pill(a.state)]),
        h('p', { 'class': 'sbs-pw__meta', text: meta }),
        h('div', { 'class': 'sbs-pw__actions' }, [toggle, copy, dl, del]),
        pre
      ]));
    });
  }

  function renderRecords(kind, sel, empty) {
    var p = P.active(), ul = q(sel); if (!p) return;
    clear(ul);
    var keys = Object.keys(p[kind]).sort(function (a, b) { return (p[kind][b].ts || 0) - (p[kind][a].ts || 0); });
    if (!keys.length) { ul.appendChild(h('li', { 'class': 'sbs-pw__empty', text: empty })); return; }
    keys.forEach(function (k) {
      var r = p[kind][k];
      ul.appendChild(h('li', { 'class': 'sbs-pw__row' }, [
        r.url ? h('a', { href: r.url, text: r.title || k }) : h('span', { text: r.title || k }),
        pill(r.state),
        h('span', { 'class': 'sbs-pw__meta', text: (typeof r.score === 'number' ? 'score ' + r.score + ' · ' : '') + fmt(r.ts) + (r.note ? ' · ' + r.note : '') })
      ]));
    });
  }

  function renderAssessments() {
    var p = P.active(), ul = q('[data-pw-assessments]'); if (!p) return;
    clear(ul);
    if (!p.assessments.length) { ul.appendChild(h('li', { 'class': 'sbs-pw__empty', text: 'No self-assessments recorded. The Launch Readiness tool and the labs add one when you save a result.' })); return; }
    p.assessments.forEach(function (a) {
      ul.appendChild(h('li', { 'class': 'sbs-pw__row' }, [h('span', { text: a.tool || 'assessment' }), h('span', { 'class': 'sbs-pw__meta', text: (a.score != null ? 'score ' + a.score + ' · ' : '') + fmtTime(a.ts) + (a.note ? ' · ' + a.note : '') })]));
    });
  }

  function refresh() {
    renderStorage(); renderSwitcher();
    if (P.active()) { renderProject(); renderTasks(); renderArtifacts(); renderRecords('guides', '[data-pw-guides]', 'No guides recorded yet. Marking a lesson complete or saving it for later records it here.'); renderRecords('labs', '[data-pw-labs]', 'No labs started. Each lab records its state and your score here.'); renderRecords('challenges', '[data-pw-challenges]', 'No Weekly Website Fix challenges yet.'); renderAssessments(); }
  }

  function copyText(text, btn) {
    function ok() { btn.textContent = 'Copied'; announce('Copied.'); window.setTimeout(function () { btn.textContent = 'Copy'; }, 1800); }
    function fb() { try { var ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.top = '-1000px'; document.body.appendChild(ta); ta.select(); var d = document.execCommand('copy'); ta.remove(); d ? ok() : say('Copying failed. Open the text and select it.', 'error'); } catch (e) { say('Copying failed. Open the text and select it.', 'error'); } }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok).catch(fb); else fb();
  }

  /* ---- wiring -------------------------------------------------------------- */
  q('[data-pw-select]').addEventListener('change', function (ev) { P.select(ev.target.value); refresh(); say('Switched to "' + P.active().name + '".'); });

  var createForm = q('[data-pw-create]');
  q('[data-pw-new]').addEventListener('click', function () { createForm.hidden = false; createForm.elements.name.focus(); });
  q('[data-pw-create-cancel]').addEventListener('click', function () { createForm.hidden = true; createForm.reset(); });
  createForm.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var f = createForm.elements;
    if (!String(f.name.value).trim()) { say('Give the project a name.', 'error'); f.name.focus(); return; }
    var r = P.create({ name: f.name.value, platform: f.platform.value, objective: f.objective.value, url: f.url.value });
    if (!r.ok) { say(r.message, 'error'); return; }
    createForm.reset(); createForm.hidden = true;
    track('project_created', { kind: r.project.platform });
    refresh(); say(r.persisted ? 'Project "' + r.project.name + '" created.' : 'Project created for this visit only — this browser is not storing site data.', r.persisted ? 'ok' : 'warn');
  });

  var editForm = q('[data-pw-edit]');
  editForm.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var p = P.active(); if (!p) return;
    var f = editForm.elements;
    if (!String(f.name.value).trim()) { say('The project needs a name.', 'error'); f.name.focus(); return; }
    var urlIn = String(f.url.value).trim();
    if (urlIn && !/^https?:\/\//i.test(urlIn)) { say('The URL must start with http:// or https:// — it was not saved. Everything else was.', 'error'); }
    P.update(p.id, { name: f.name.value, platform: f.platform.value, objective: f.objective.value, url: urlIn });
    refresh(); say('Project details saved.', 'ok');
  });

  q('[data-pw-delete]').addEventListener('click', function () {
    var p = P.active(); if (!p) return;
    if (!window.confirm('Delete the project "' + p.name + '" and everything saved in it? Export it first if you want a copy. This cannot be undone.')) return;
    P.remove(p.id); refresh(); say('Project deleted.');
  });

  var taskForm = q('[data-pw-task-form]');
  taskForm.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var r = P.addTask(taskForm.elements.task.value);
    if (!r.ok) { say(r.message || 'Type a task first.', 'error'); return; }
    taskForm.reset(); refresh(); say('Task added.');
  });

  q('[data-pw-export-json]').addEventListener('click', function () {
    var p = P.active(); if (!p) return;
    if (P.download('sitebuilderstack-project-' + (p.name || 'project').toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40) + '.json', P.exportJSON(p.id), 'application/json')) { track('artifact_exported', { kind: 'project-json' }); say('Exported this project as JSON.', 'ok'); }
    else say('The browser blocked the download.', 'error');
  });
  q('[data-pw-export-all]').addEventListener('click', function () {
    if (P.download('sitebuilderstack-projects-' + new Date().toISOString().slice(0, 10) + '.json', P.exportJSON(), 'application/json')) { track('artifact_exported', { kind: 'projects-json' }); say('Exported all projects as JSON.', 'ok'); }
    else say('The browser blocked the download.', 'error');
  });
  q('[data-pw-export-md]').addEventListener('click', function () {
    var p = P.active(); if (!p) return;
    if (P.download('sitebuilderstack-project-' + (p.name || 'project').toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40) + '.md', P.exportMarkdown(p.id))) { track('artifact_exported', { kind: 'project-markdown' }); say('Exported this project as Markdown.', 'ok'); }
    else say('The browser blocked the download.', 'error');
  });

  var importForm = q('[data-pw-import]');
  importForm.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var file = importForm.elements.file.files && importForm.elements.file.files[0];
    var mode = importForm.elements.mode.value === 'replace' ? 'replace' : 'merge';
    if (!file) { say('Choose a JSON export first.', 'error'); return; }
    if (file.size > 4 * 1024 * 1024) { say('That file is larger than 4 MB, which a projects export never is. Nothing was imported.', 'error'); return; }
    var reader = new FileReader();
    reader.onload = function () {
      var parsed = P.parseImport(String(reader.result));
      if (!parsed.ok) { say('Import rejected: ' + parsed.message + ' Your existing projects are untouched.', 'error'); return; }
      var msg = mode === 'replace'
        ? 'Replace ALL ' + P.list().length + ' project(s) in this browser with the ' + parsed.count + ' in the file? Existing projects will be deleted first.'
        : 'Merge ' + parsed.count + ' project(s) from the file into this browser? Projects with the same id keep whichever copy is newer.';
      if (!window.confirm(msg)) { say('Import cancelled. Nothing changed.'); return; }
      var r = P.importJSON(String(reader.result), mode);
      if (!r.ok) { say('Import rejected: ' + r.message, 'error'); return; }
      importForm.reset(); refresh();
      say('Imported: ' + r.added + ' added, ' + r.updated + ' updated' + (r.persisted ? '.' : ' — but this browser could not store them; export before leaving.'), r.persisted ? 'ok' : 'warn');
    };
    reader.onerror = function () { say('The file could not be read.', 'error'); };
    reader.readAsText(file);
  });

  q('[data-pw-clear]').addEventListener('click', function () {
    var n = P.list().length; if (!n) return;
    if (!window.confirm('Delete all ' + n + ' project(s) from this browser? Export first if you want a copy. This cannot be undone.')) return;
    P.list().forEach(function (p) { P.remove(p.id); });
    refresh(); say('All projects deleted from this browser.');
  });

  document.addEventListener('sbs:projects-changed', refresh);
  root.classList.add('is-ready');
  var nojs = q('[data-pw-nojs]'); if (nojs) nojs.hidden = true;
  refresh();
  if (window.location.hash === '#artifacts' || window.location.hash === '#tasks') { var t = document.getElementById(window.location.hash.slice(1)); if (t) t.scrollIntoView(); }
})();
