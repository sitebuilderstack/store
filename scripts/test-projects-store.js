/* Unit tests for the My Projects storage core (theme/dev/assets/sbs-projects.js).
 *
 * Runs the shipped file inside a small sandbox with a fake localStorage, so
 * the persistence, migration, limits, import validation and the
 * "continue your project" choice are tested without a browser. The fake
 * storage can be told to throw (private windows, blocked site data) and to
 * refuse writes (quota), because those are the cases that must degrade
 * gracefully rather than the ones that usually work.
 */
const fs = require('fs');
const vm = require('vm');
const src = fs.readFileSync(__dirname + '/../theme/dev/assets/sbs-projects.js', 'utf8');

let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d && !ok ? '  -> ' + String(d).slice(0, 200) : ''}`); };

function makeStorage(opts) {
  opts = opts || {};
  const data = Object.assign({}, opts.seed || {});
  return {
    getItem(k) { if (opts.throws) throw new Error('blocked'); return Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null; },
    setItem(k, v) { if (opts.throws) throw new Error('blocked'); if (opts.quota && k === 'sbs-projects') throw new Error('QuotaExceededError'); data[k] = String(v); },
    removeItem(k) { if (opts.throws) throw new Error('blocked'); delete data[k]; },
    _data: data,
  };
}
function boot(opts) {
  const events = [];
  const localStorage = makeStorage(opts);
  const sandbox = {
    window: null, document: { dispatchEvent: (e) => events.push(e.type) }, console,
    CustomEvent: function (t) { this.type = t; }, URL: { createObjectURL: () => 'blob:x', revokeObjectURL() {} }, Blob: function () {},
    unescape, encodeURIComponent, Date, Math, JSON, Object, Array, String, RegExp, Error, setTimeout,
  };
  sandbox.window = { localStorage, setTimeout };
  vm.createContext(sandbox);
  vm.runInContext(src, sandbox);
  return { P: sandbox.window.SBSProjects, storage: localStorage, events };
}

// ---- fresh store ----------------------------------------------------------
{
  const { P, storage } = boot();
  check('fresh store: storage available, no projects, no active', P.storageAvailable() && P.list().length === 0 && P.active() === null);
  const r = P.create({ name: '  Northgate  ', platform: 'wordpress', objective: 'more quote requests', url: 'https://northgate.example' });
  check('create: trims the name, keeps platform/objective/url, persists', r.ok && r.persisted && r.project.name === 'Northgate' && r.project.platform === 'wordpress' && r.project.url === 'https://northgate.example', JSON.stringify(r));
  check('create: the new project is active and stored under the key', P.active().id === r.project.id && JSON.parse(storage._data['sbs-projects']).v === 1);
  check('url: a javascript: url is rejected', P.update(r.project.id, { url: 'javascript:alert(1)' }) && P.active().url === '');
  check('platform: an unknown platform becomes other', P.update(r.project.id, { platform: 'weird' }) && P.active().platform === 'other');
  const a = P.addArtifact({ kind: 'checklist', module: 'maintenance-checklist', title: 'Weekly checks', text: '# Weekly\n- forms', file: 'weekly.md', guide: 'claude-code-website-maintenance' });
  check('artifact: saved with state generated and the actual text', a.ok && a.artifact.state === 'generated' && P.active().artifacts[0].text === '# Weekly\n- forms');
  const big = P.addArtifact({ title: 'big', text: 'x'.repeat(70 * 1024) });
  check('artifact: over 64 KB is refused with a message', !big.ok && big.error === 'size' && /64 KB/.test(big.message));
  check('artifact: empty text is refused', !P.addArtifact({ title: 'e', text: '   ' }).ok);
  const g = P.setGuide('claude-code-wordpress', { state: 'read', title: 'WP', url: '/blogs/guides/claude-code-wordpress' });
  check('guide record: relative url accepted; state read', g.ok && P.active().guides['claude-code-wordpress'].state === 'read');
  const l = P.setLab('technical-seo', { state: 'example-verified', title: 'Technical SEO Lab', url: '/pages/lab-technical-seo', score: 3 });
  check('lab record: example-verified with a score', l.ok && P.active().labs['technical-seo'].state === 'example-verified' && P.active().labs['technical-seo'].score === 3);
  check('state: an unknown state becomes not-started', P.setChallenge('x', { state: 'certified' }).record.state === 'not-started');
  const t = P.addTask('Test the contact form on staging');
  check('task: added open', t.ok && P.active().tasks[0].done === false);
  check('nextAction: an open task wins', P.nextAction(P.active()).kind === 'task');
  P.toggleTask(P.active().id, t.task.id);
  P.setLab('launch-readiness', { state: 'in-progress', title: 'Launch Lab', url: '/pages/lab-launch-readiness' });
  check('nextAction: then a lab in progress', P.nextAction(P.active()).kind === 'lab');
  P.setLab('launch-readiness', { state: 'example-verified' });
  check('nextAction: then the newest generated artifact', P.nextAction(P.active()).kind === 'artifact');
  const md = P.exportMarkdown(P.active().id);
  check('markdown export: has the name, the task, the artifact text and the state caveat', /# Northgate/.test(md) && /\[x\] Test the contact form/.test(md) && /- forms/.test(md) && /self-reported unless marked example-verified/.test(md));
  const json = P.exportJSON();
  check('json export: format marker and version', JSON.parse(json).format === 'sitebuilderstack-projects' && JSON.parse(json).v === 1);
  // second project, selection, rename, delete
  const r2 = P.create({ name: 'Second' });
  check('second project becomes active; list sorted newest first', P.active().id === r2.project.id && P.list()[0].id === r2.project.id);
  check('select switches back', P.select(r.project.id) && P.active().id === r.project.id);
  check('rename', P.update(r.project.id, { name: 'Northgate Physio' }) && P.get(r.project.id).name === 'Northgate Physio');
  check('remove: deletes and picks another active', P.remove(r.project.id) && P.active().id === r2.project.id && P.list().length === 1);
  // round trip
  const { P: P2 } = boot();
  const imp = P2.importJSON(json, 'merge');
  check('import (merge) round-trips the export', imp.ok && imp.added === 1 && P2.get(JSON.parse(json).projects[Object.keys(JSON.parse(json).projects)[0]].id).artifacts[0].text === '# Weekly\n- forms', JSON.stringify(imp));
}

// ---- migration from sbs-learning -----------------------------------------
{
  const seed = { 'sbs-learning': JSON.stringify({ done: { 'claude-code-wordpress': 1700000000000 }, saved: { 'claude-code-astro': { t: 'Astro guide', u: '/blogs/guides/claude-code-astro', ts: 1700000001000 } } }) };
  const { P, storage } = boot({ seed });
  const p = P.active();
  check('migration: a default project is created from sbs-learning', p && p.name === 'My website' && p.migratedFrom === 'sbs-learning');
  check('migration: done → read, saved → in-progress, titles kept', p.guides['claude-code-wordpress'].state === 'read' && p.guides['claude-code-astro'].state === 'in-progress' && p.guides['claude-code-astro'].title === 'Astro guide');
  check('migration: sbs-learning is untouched', storage._data['sbs-learning'] === seed['sbs-learning']);
  check('migration: nextAction offers the saved guide', P.nextAction(p).kind === 'guide');
}

// ---- corrupt, blocked, quota ----------------------------------------------
{
  const { P } = boot({ seed: { 'sbs-projects': '{not json' } });
  check('corrupt record: recovered to an empty store (flagged), nothing thrown', P.load().recovered === true && P.list().length === 0);
}
{
  const { P } = boot({ seed: { 'sbs-projects': JSON.stringify({ v: 1, activeId: 'x', projects: { bad: 'string', ok: { name: 'Kept', artifacts: [{ text: 'a' }, 'junk', { text: 42 }], tasks: [{ text: 'do' }, null], guides: { 'g/../x': { state: 'read' } } } } }) } });
  const p = P.list()[0];
  check('corrupt fields: junk entries dropped, valid ones kept, unsafe keys sanitised', P.list().length === 1 && p.name === 'Kept' && p.artifacts.length === 1 && p.tasks.length === 1 && Object.keys(p.guides)[0] === 'g/x');
}
{
  const { P } = boot({ throws: true });
  check('blocked storage: storageAvailable is false', P.storageAvailable() === false);
  const r = P.create({ name: 'Temp' });
  check('blocked storage: create works in memory and reports persisted=false', r.ok && r.persisted === false && P.active().name === 'Temp');
  check('blocked storage: export still works', /Temp/.test(P.exportJSON()));
}
{
  const { P } = boot({ quota: true });
  const r = P.create({ name: 'Quota' });
  check('quota failure: reported as persisted=false and flagged on the store', r.ok && r.persisted === false && P.load().quota === true);
}
{
  const { P } = boot();
  P.create({ name: 'Big' });
  for (let i = 0; i < 40; i++) P.addArtifact({ title: 'a' + i, text: 'y'.repeat(60 * 1024) });
  let last; for (let i = 0; i < 5; i++) last = P.addArtifact({ title: 'z', text: 'y'.repeat(60 * 1024) });
  check('store limit: refuses to grow past 2 MB before mutating, with a message', !last.ok && last.error === 'store-limit' && P.active().artifacts.length < 45 && P.load().overLimit !== true);
}

// ---- import validation ----------------------------------------------------
{
  const { P } = boot();
  P.create({ name: 'Existing' });
  const cases = [
    ['not json', '{', 'json'],
    ['wrong format', JSON.stringify({ format: 'other', v: 1, projects: {} }), 'format'],
    ['newer version', JSON.stringify({ format: 'sitebuilderstack-projects', v: 99, projects: {} }), 'version'],
    ['no projects', JSON.stringify({ format: 'sitebuilderstack-projects', v: 1, projects: { a: 'nope' } }), 'empty'],
    ['oversize', '{"format":"sitebuilderstack-projects","v":1,"projects":{},"pad":"' + 'z'.repeat(4 * 1024 * 1024 + 10) + '"}', 'size'],
  ];
  cases.forEach(([n, text, err]) => {
    const r = P.importJSON(text, 'merge');
    check('invalid import (' + n + ') is rejected with ' + err + ' and existing work survives', !r.ok && r.error === err && P.list().length === 1 && P.active().name === 'Existing', JSON.stringify(r));
  });
  const good = JSON.stringify({ format: 'sitebuilderstack-projects', v: 1, projects: { pimport1: { name: 'Imported', updated: 5, artifacts: [{ text: '<script>alert(1)</script>', title: 'x' }], tasks: [{ text: 'a task' }] } } });
  const m = P.importJSON(good, 'merge');
  check('merge: adds the imported project beside the existing one', m.ok && m.added === 1 && P.list().length === 2);
  check('import: artifact text is stored as text (rendering is the UI\'s job)', P.get('pimport1').artifacts[0].text === '<script>alert(1)</script>');
  const rep = P.importJSON(good, 'replace');
  check('replace: discards existing projects first', rep.ok && P.list().length === 1 && P.list()[0].name === 'Imported');
  const older = JSON.stringify({ format: 'sitebuilderstack-projects', v: 1, projects: { pimport1: { name: 'Older copy', updated: 1 } } });
  P.importJSON(older, 'merge');
  check('merge: an older copy of the same project does not overwrite the newer one', P.get('pimport1').name === 'Imported');
}

console.log(`\n${failures} failure(s)`);
process.exit(failures ? 1 : 0);
