/* Site Builder Stack — "Try this on your project" modules.

   Loaded on demand by sbs.js when a page contains [data-sbs-try]. Each module
   is a small server-rendered form (snippets/sbs-try.liquid) with two to four
   inputs, a Generate action, an editable result, Copy, Download and Save to
   My Project. Generation is deterministic and browser-local: nothing typed
   here is transmitted anywhere, and the analytics events carry only the
   module id and the guide handle (both public identifiers).

   Every generator follows the same honesty rules as the free tools: an input
   left blank produces a line that says so or no line at all — never a
   plausible default. Workflows separate observation from modification and end
   with validation and rollback. A generated prompt or checklist is a starting
   point, not evidence that anything was done. */
(function () {
  'use strict';

  var P = window.SBSProjects;
  var track = (window.SBS && window.SBS.track) || function () {};
  var announce = (window.SBS && window.SBS.announce) || function () {};

  function val(root, name) {
    var el = root.querySelector('[name="' + name + '"]');
    return el ? String(el.value || '').trim() : '';
  }
  function lines(root, name) {
    return val(root, name).split('\n').map(function (l) { return l.trim(); }).filter(Boolean);
  }
  function safeUrl(s) {
    return /^https?:\/\/[^\s]+$/i.test(s) ? s : '';
  }
  function today() { return new Date().toISOString().slice(0, 10); }
  function slug(s) { return (s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40) || 'project'; }

  /* ---- generators ------------------------------------------------------ */

  var GEN = {};

  GEN['claude-md-section'] = function (root) {
    var name = val(root, 'name') || 'This project';
    var cmds = lines(root, 'commands');
    var prohibit = lines(root, 'prohibitions');
    var done = lines(root, 'done');
    var L = ['## ' + name + ' — Claude Code section', '', '_Generated ' + today() + ' from what you typed. Every line below is a claim about your project; delete any you cannot stand behind. Anything you left blank is marked, not guessed._', ''];
    L.push('### Commands', '');
    if (cmds.length) cmds.forEach(function (c) { L.push('- `' + c.replace(/`/g, '') + '`'); });
    else L.push('- _No commands given. Add the real run, build, test and check commands — an agent without them spends a turn guessing from package.json._');
    L.push('', '### Do not', '');
    if (prohibit.length) prohibit.forEach(function (p) { L.push('- ' + p); });
    else L.push('- _No prohibitions given. The most valuable lines in a CLAUDE.md are the things that fail silently: "never edit the parent theme", "do not write to the database"._');
    L.push('', '### Definition of done', '');
    if (done.length) done.forEach(function (d) { L.push('- ' + d); });
    else L.push('- _Not stated. What must be true before a task is finished? Checks run and shown, the page fetched, the diff read as a reviewer._');
    L.push('', '### Before finishing', '', '- Run the check commands above and show the output.', '- Say what was not verified.', '', '_Keep the whole file under ~150 lines; move rules that must be enforced into hooks or settings, not prose._');
    return { text: L.join('\n'), file: 'CLAUDE-section-' + slug(name) + '.md' };
  };

  GEN['seo-audit-prompt'] = function (root) {
    var platform = val(root, 'platform') || 'not stated';
    var pages = lines(root, 'pages');
    var access = val(root, 'access') || 'not stated';
    var L = ['# Read-only technical SEO audit — scoped', '', 'Platform: ' + platform + '  ', 'Access available: ' + access + '  ', 'Date: ' + today(), '',
      '## Scope', ''];
    if (pages.length) { L.push('Audit only these pages (fetch each; do not crawl beyond them):', ''); pages.forEach(function (p) { L.push('- ' + p); }); }
    else L.push('_No pages listed. Name the pages that carry traffic or revenue; an audit of "the site" produces a list nobody acts on._');
    L.push('', '## Rules', '', '1. Read-only. Fetch pages and files; run no mutation, edit no file, change no setting. If a fix seems obvious, write it down as a recommendation.',
      '2. Evidence for every finding: the URL, the exact value observed (tag, header, status code), and the time. A finding without evidence is a guess and is not reported.',
      '3. Audit the rendered response, not the template. Titles, canonicals, robots directives and JSON-LD are read from what the server returned.',
      '4. Say what could not be checked (no Search Console access, no server logs) rather than filling the gap.',
      '5. Numbers that need external data (search volume, competitor rankings) are not invented. If it did not come from a request, it is not in the report.',
      '', '## Check, in this order', '',
      '- Status code and final URL after redirects (count the hops)', '- `<title>`, meta description, one H1', '- Canonical: present, self-referencing, on the production host',
      '- Robots meta / X-Robots-Tag: not `noindex` on a page that should rank', '- Every `application/ld+json` block parses; the values match what a visitor sees',
      '- Internal links on the page: none broken, none to staging or old hosts, none through redirect chains', '- Sitemap lists the page; robots.txt does not block it',
      '', '## Output', '', 'A table per page: check · observed · pass/fail · evidence. Then findings by priority (CRITICAL / HIGH / MEDIUM / LOW) with a recommendation and an effort each. Then "Not checked" with reasons.',
      '', '_The fix is a separate run: audit first, decide, then change — so the record of what was wrong survives._');
    return { text: L.join('\n'), file: 'seo-audit-prompt-' + today() + '.md' };
  };

  GEN['shopify-next-workflow'] = function (root) {
    var kind = val(root, 'kind') || 'theme';
    var goal = val(root, 'goal') || 'not stated';
    var risk = val(root, 'risk') || 'not stated';
    var L = ['# Next safe Shopify workflow — ' + kind, '', 'Goal: ' + goal + '  ', 'What must not break: ' + risk + '  ', 'Date: ' + today(), ''];
    L.push('## 1. Observe (no changes)', '');
    if (kind === 'theme') L.push('- Confirm which theme is MAIN and which is the development copy; write the development theme id into the push command and make the push refuse MAIN.', '- Pull the current theme; note the sections and templates the goal touches; run Theme Check.', '- Fetch the live page(s) affected and record title, canonical and the rendered markup you are about to change.');
    else if (kind === 'catalogue') L.push('- Export the products/collections you intend to change (JSON or CSV) — this export is the rollback.', '- Query the live values through the Admin API and diff them against the intended change; count how many resources it touches.', '- Confirm the mutation names and that `userErrors` is read on every call.');
    else L.push('- Export current SEO titles and descriptions for the pages in scope; record which pages carry organic traffic (Search Console).', '- Fetch each page and record the rendered title, description and canonical.', '- Confirm Shopify\'s generated sitemap lists the pages; do not plan to replace it.');
    L.push('', '## 2. Change, where it can be undone', '');
    if (kind === 'theme') L.push('- Edit files locally; push to the development theme only; preview by fetching the preview URL, not by trusting "push succeeded".', '- Section schema first, then section-group JSON, then templates — in that order.');
    else if (kind === 'catalogue') L.push('- Dry run first: print every planned change against the live value; apply only with an explicit confirm and a limit equal to the count you reviewed.', '- Batches of 25; stop on the first `userErrors` entry.');
    else L.push('- Apply metadata changes from a reviewed worksheet; skip any row whose live value changed since the export.', '- Never write competing canonical or sitemap tags in the theme.');
    L.push('', '## 3. Verify', '', '- Read each changed resource or page back and compare with the intention.', '- For a theme: crawl the preview for 200s, Liquid errors rendered as text (`{{`, `{%`), and the affected pages at 320px.', '- Say in writing what was not verified: ' + (risk !== 'not stated' ? 'specifically confirm "' + risk + '" still works.' : 'name the thing that must not break and check it.'));
    L.push('', '## 4. Publish and rollback', '', kind === 'theme' ? '- Publish the development theme only after the batch is verified; keep the previous theme unpublished as the rollback.' : '- The export from step 1 is the rollback; keep it until the change has been live for a week.', '- Record what changed, when, and how to reverse it.', '', '_Payments, tax, domains and app installs stay in the admin, by hand. A workflow that touches them is not this one._');
    return { text: L.join('\n'), file: 'shopify-' + kind + '-workflow-' + today() + '.md' };
  };

  GEN['landing-validation'] = function (root) {
    var url = safeUrl(val(root, 'url'));
    var cta = val(root, 'cta') || 'not stated';
    var dest = val(root, 'destination') || 'not stated';
    var devices = val(root, 'devices') || 'phone and desktop';
    var L = ['# Functional validation checklist — landing page', '', 'Page: ' + (url || '_not stated — validate on staging or the live URL you own_') + '  ', 'Primary call to action: "' + cta + '" → ' + dest + '  ', 'Devices: ' + devices + '  ', 'Date: ' + today(), '',
      '_Every line is a check with an observable result. Tick nothing you did not see._', '',
      '## Links and destinations', '', '- [ ] The primary CTA "' + cta + '" lands on ' + dest + ' (final URL after redirects, not the href)', '- [ ] Every other link on the page resolves 200; no `#` fragments that only exist on another page', '- [ ] Phone and email links open the right app with the right value',
      '', '## Form (if the page has one)', '', '- [ ] Required fields show a visible error when empty, and the error is announced (not colour alone)', '- [ ] An invalid email is rejected with a message; a valid one is accepted', '- [ ] Submitting shows a confirmation the visitor can see, and the submission arrives where it should (inbox / CRM) — a test with a recognisable marker', '- [ ] Spam protection does not block a normal submission on ' + devices,
      '', '## Tracking', '', '- [ ] The conversion event fires once on the CTA click or the form submit (real-time view), not on page load', '- [ ] No personal data in the event payload',
      '', '## Devices and states', '', '- [ ] ' + devices + ': CTA visible without scrolling; no horizontal overflow; tap targets usable', '- [ ] Keyboard: Tab reaches the CTA and the form; focus is visible; Enter submits', '- [ ] Slow network: the CTA is usable before every script has loaded',
      '', '## Evidence', '', 'Record for each check: what was observed, where (URL/device), when. A screenshot of the confirmation and the received submission is the proof.'];
    return { text: L.join('\n'), file: 'landing-validation-' + today() + '.md' };
  };

  GEN['maintenance-checklist'] = function (root) {
    var platform = val(root, 'platform') || 'other';
    var forms = lines(root, 'forms');
    var name = val(root, 'name') || 'the site';
    var hosted = platform === 'shopify';
    var L = ['# Recurring inspection checklist — ' + name, '', 'Platform: ' + platform + '  ', 'Date generated: ' + today(), '',
      '_A starting cadence, not a requirement: move items between columns as the site\'s risk changes. Checks marked (host) are handled by a hosted platform on ' + platform + ' and are listed so you know they are not yours to run._', '',
      '## Daily (2 minutes)', '', '- [ ] Homepage and the key page return 200 from outside (phone on mobile data)', '- [ ] Uptime monitor shows no incident overnight'];
    L.push('', '## Weekly (15–30 minutes)', '');
    if (forms.length) forms.forEach(function (f) { L.push('- [ ] Form "' + f + '": submit a test with a marker and confirm it arrived where it should'); });
    else L.push('- [ ] _No forms listed — if the site has one, a weekly test submission is the single most valuable check on this list_');
    L.push('- [ ] Navigation destinations: every menu and footer link resolves to the page its label names', '- [ ] Broken links scan on the key pages; 404 log reviewed', '- [ ] TLS certificate valid, more than 14 days from expiry' + (hosted ? ' (host)' : ''), '- [ ] Security headers unchanged from the baseline' + (hosted ? ' (host)' : ''));
    L.push('', '## Monthly (1–2 hours)', '', hosted ? '- [ ] Apps: list what is installed vs what injects scripts on the storefront; remove leftovers' : '- [ ] Dependencies: platform, plugins/packages reviewed; updates applied on staging first, then production, with a rollback point',
      '- [ ] Configuration drift: settings, redirects, DNS records compared with the recorded baseline', '- [ ] Backup: not "the job says success" — restore one backup somewhere and open it' + (hosted ? ' (host takes the backup; you verify an export)' : ''),
      '- [ ] Rollback readiness: the previous release/theme is still available and someone can name the steps', '- [ ] Performance on the key pages vs last month', '- [ ] Analytics still receiving events (real-time view)', '- [ ] Report written from evidence (template below)');
    L.push('', '---', '', '# Maintenance report — ' + name + ' — {month}', '', '| Check | Result | Evidence | Date |', '|---|---|---|---|', '| Forms deliver | | | |', '| Navigation and links | | | |', '| Certificate / headers | | | |', '| Dependencies / apps | | | |', '| Configuration vs baseline | | | |', '| Backup restore tested | | | |', '| Rollback available | | | |', '| Performance | | | |', '', '## Found and fixed', '', '## Open', '', '## Not checked (and why)', '');
    return { text: L.join('\n'), file: 'maintenance-checklist-' + slug(name) + '.md' };
  };

  GEN['migration-verification'] = function (root) {
    var kind = val(root, 'kind') || 'redesign';
    var src = safeUrl(val(root, 'source'));
    var dst = safeUrl(val(root, 'target'));
    var pages = lines(root, 'pages');
    var domainChange = kind === 'domain';
    var L = ['# Migration verification checklist — ' + kind, '', 'Source: ' + (src || '_not stated_') + '  ', 'Target: ' + (dst || '_not stated_') + '  ', 'Date: ' + today(), '',
      '## Before anything moves', '', '- [ ] Full URL inventory of the source (crawl + sitemap + Search Console pages + analytics), reconciled', '- [ ] SEO baseline saved off-host: titles, descriptions, canonicals, indexability per URL; Search Console exports', '- [ ] Existing redirects exported (they are merged, never dropped)',
      domainChange ? '- [ ] DNS zone recorded including MX, SPF, DKIM, DMARC and verification records; TTL lowered 48h ahead' : '- [ ] DNS: no change planned — recorded as such',
      '', '## Map', '', '- [ ] One row per source URL: KEEP / MOVE / MERGE / REMOVE; zero REVIEW rows before build', '- [ ] Nothing redirected to the homepage that was not the homepage', '', '## Staging', '', '- [ ] Staging noindexed; canonicals on staging point at the production host', '- [ ] Coverage: every mapped destination returns 200 on staging', '- [ ] Metadata compared page by page; critical pages verbatim',
      '', '## After cutover (T+15 min, T+24 h, T+7 d)', '', '- [ ] Production NOT noindexed; canonicals to production', '- [ ] Every redirect tested on the real origin: expected destination, one hop, 301', '- [ ] Forms, tracking, critical pages verified from outside', domainChange ? '- [ ] Old domain still redirecting; certificate on the old domain valid' : '- [ ] Old hosting retained for 30 days as the rollback',
      '', '---', '', '# url-map starter (CSV)', '', '```csv', 'source_url,target_url,disposition,expected_status,verified,notes'];
    if (pages.length) pages.forEach(function (p) { var s = /^https?:/.test(p) ? p : (src ? src.replace(/\/$/, '') + (p.charAt(0) === '/' ? p : '/' + p) : p); L.push(s + ',,KEEP,200,,'); });
    else L.push('https://old.example/page,https://new.example/page,MOVE,301,,example row — replace with your inventory');
    L.push('```', '', '_disposition: KEEP · MOVE · MERGE · REMOVE (301 to the closest page or 410). expected_status is what the SOURCE URL should return after cutover. verified is filled by the redirect check, never by hand._');
    return { text: L.join('\n'), file: 'migration-verification-' + kind + '-' + today() + '.md' };
  };

  GEN['regression-plan'] = function (root) {
    var flows = lines(root, 'flows');
    var target = val(root, 'target') || 'not stated';
    var tool = val(root, 'tool') || 'Playwright';
    var L = ['# Regression test plan', '', 'Target environment: ' + target + ' (never production for anything that submits, orders or changes state)  ', 'Tool: ' + tool + '  ', 'Date: ' + today(), '',
      '## Flows that must keep working', ''];
    if (flows.length) flows.forEach(function (f, i) { L.push((i + 1) + '. **' + f + '**', '   - Asserts: _the observable result — the destination URL, the visible confirmation, the error message text — not "no exception was thrown"_', '   - Setup: _isolated; no dependence on another test\'s state_', '   - Out of scope for this test: _real email delivery, payment capture, third-party uptime_', ''); });
    else L.push('_No flows listed. Name the three to five things that would embarrass you if they broke: the contact form, the primary CTA, mobile navigation, checkout entry, login._', '');
    L.push('## Rules', '', '- One behaviour per test; a test that checks five things fails for five reasons.', '- Robust locators: roles and labels, not CSS chains; explicit expectations with auto-waiting, no fixed sleeps.', '- Mock what leaves the site (form endpoints, payment) and say so in the test name; a mocked submission proves the page posts, not that anyone received it.', '- Every test is shown failing once on purpose before it is trusted.', '', '## What a browser test cannot establish', '', '- Security (a green suite says nothing about an exposed endpoint)', '- Accessibility beyond what an automated check covers', '- Conversion rate, ranking, or production reliability', '', '## Next', '', '- Implement in ' + tool + '; run locally; add the smallest subset to CI; link the run to the launch checklist.');
    return { text: L.join('\n'), file: 'regression-test-plan-' + today() + '.md' };
  };

  /* ---- module wiring ---------------------------------------------------- */

  function copyText(text, btn) {
    if (!text) return;
    function ok() { btn.textContent = 'Copied'; announce('Copied to the clipboard.'); window.setTimeout(function () { btn.textContent = 'Copy'; }, 1800); }
    function fail() { btn.textContent = 'Press Ctrl+C'; announce('Copying failed. Select the text and press Control C.'); window.setTimeout(function () { btn.textContent = 'Copy'; }, 2600); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(ok).catch(function () { fallback(); });
    } else fallback();
    function fallback() {
      try {
        var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.top = '-1000px';
        document.body.appendChild(ta); ta.select(); var done = document.execCommand('copy'); ta.remove(); done ? ok() : fail();
      } catch (e) { fail(); }
    }
  }

  function initModule(root) {
    var id = root.getAttribute('data-sbs-try');
    var guide = root.getAttribute('data-sbs-guide') || '';
    var gen = GEN[id];
    var form = root.querySelector('form');
    var result = root.querySelector('[data-try-result]');
    var output = root.querySelector('[data-try-output]');
    var status = root.querySelector('[data-try-status]');
    var copyBtn = root.querySelector('[data-try-copy]');
    var dlBtn = root.querySelector('[data-try-download]');
    var saveBtn = root.querySelector('[data-try-save]');
    var next = root.querySelector('[data-try-next]');
    var fallback = root.querySelector('[data-try-fallback]');
    if (!gen || !form || !result || !output) return;
    root.classList.add('is-ready');
    if (fallback) fallback.hidden = true;
    form.hidden = false;

    var current = null;   // { text, file }
    var started = false, saved = false;
    var payload = { module: id, guide: guide };   // public identifiers only

    function say(msg, kind) {
      if (!status) return;
      status.textContent = msg; status.hidden = !msg; status.className = 'sbs-try__status' + (kind ? ' is-' + kind : '');
    }

    form.addEventListener('input', function () {
      if (started) return; started = true;
      track('engagement_module_started', payload);
    });

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var fields = form.querySelectorAll('input, textarea');
      var filled = Array.prototype.some.call(fields, function (f) { return String(f.value).trim() !== ''; });
      if (!filled) {
        say('Fill in at least one field first — the result is only as specific as what you type. Your selections are kept.', 'error');
        if (fields[0]) fields[0].focus();
        return;
      }
      current = gen(root);
      output.value = current.text;
      result.hidden = false; saved = false;
      if (saveBtn) saveBtn.textContent = 'Save to My Project';
      say('', '');
      announce('Result ready. It is editable.');
      track('artifact_generated', payload);
      result.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    output.addEventListener('input', function () { if (current) { current.text = output.value; saved = false; if (saveBtn) saveBtn.textContent = 'Save to My Project'; } });

    if (copyBtn) copyBtn.addEventListener('click', function () {
      if (!current) return; copyText(current.text, copyBtn); track('artifact_copied', payload);
    });
    if (dlBtn) dlBtn.addEventListener('click', function () {
      if (!current) return;
      if (P && P.download(current.file, current.text)) { announce('Downloading ' + current.file); track('artifact_exported', payload); }
      else say('Your browser blocked the download. Copy the text instead.', 'error');
    });
    if (saveBtn) saveBtn.addEventListener('click', function () {
      if (!current || !P) return;
      if (saved) { say('Already saved. Edit the result to save a new version.', 'ok'); return; }
      var r = P.addArtifact({ kind: id, module: id, title: root.getAttribute('data-sbs-try-title') || id, text: current.text, file: current.file, guide: guide });
      if (!r.ok) { say(r.message || 'Could not save.', 'error'); return; }
      saved = true;
      saveBtn.textContent = 'Saved';
      var where = r.persisted ? 'Saved to "' + r.project.name + '" in this browser.' : 'Saved for this visit only — this browser is not remembering site data, so export it before you leave.';
      say(where + ' Open My Projects to continue.', r.persisted ? 'ok' : 'warn');
      announce(where);
      if (next) next.hidden = false;
      track('artifact_saved', payload);
    });
  }

  var roots = document.querySelectorAll('[data-sbs-try]');
  Array.prototype.forEach.call(roots, initModule);
  window.SBSEngage = { GEN: GEN };
})();
