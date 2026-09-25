/* questions.js — assessment data. Each question: id, category, text, weight
 * (1 normal, 2 significant production risk), optional `only` (project types
 * it applies to) or `not` (types it is skipped for), and the three texts the
 * report uses when it is a gap: why it matters, what to do, what to validate.
 * Answers: yes = 1, partial = 0.5, notsure = 0.25, no = 0. */
window.LRA_QUESTIONS = (function () {
  'use strict';
  var PROJECT_TYPES = [
    ['new', 'New website'], ['shopify', 'Shopify store'], ['wordpress', 'WordPress site'], ['astro', 'Astro site'],
    ['saas', 'SaaS application'], ['landing', 'Landing page'], ['redesign', 'Existing website redesign'], ['improve', 'Existing website improvement'], ['other', 'Other'],
  ];
  var USAGE = [
    ['starting', 'Just getting started'], ['occasional', 'Using Claude Code occasionally'],
    ['most', 'Using Claude Code for most development'], ['structured', 'Using Claude Code as part of a structured development workflow'],
  ];
  var CATEGORIES = [
    ['planning', 'Planning & Architecture'], ['claude', 'Claude Code Configuration'], ['seo', 'SEO'], ['security', 'Security'],
    ['a11y', 'Accessibility'], ['testing', 'Testing'], ['deployment', 'Deployment'], ['launch', 'Launch & Operations'],
  ];
  var STEPS = [
    { id: 'project', title: 'Project', heading: 'Project profile' },
    { id: 'foundation', title: 'Foundation', heading: 'Does the project currently have…', cats: ['planning', 'claude'] },
    { id: 'seo', title: 'SEO', heading: 'SEO readiness', cats: ['seo'] },
    { id: 'security', title: 'Security', heading: 'Security readiness', cats: ['security'] },
    { id: 'a11y', title: 'Accessibility', heading: 'Accessibility', cats: ['a11y'] },
    { id: 'testing', title: 'Testing', heading: 'Testing', cats: ['testing'] },
    { id: 'deployment', title: 'Deployment', heading: 'Deployment', cats: ['deployment'] },
    { id: 'launch', title: 'Launch', heading: 'Launch and operations', cats: ['launch'] },
  ];
  function q(id, cat, text, weight, why, do_, validate, scope) {
    var o = { id: id, cat: cat, text: text, weight: weight || 1, why: why, do: do_, validate: validate };
    if (scope && scope.only) o.only = scope.only; if (scope && scope.not) o.not = scope.not; if (scope && scope.label) o.label = scope.label;
    return o;
  }
  var SAAS = { only: ['saas'] }, SHOP = { only: ['shopify'] }, EXISTING = { only: ['redesign', 'improve'] }, NOT_LANDING = { not: ['landing'] };
  var Q = [
    // ---- planning
    q('brief', 'planning', 'A written project brief', 1, 'Without a brief, Claude Code builds a different site each time you ask; every later decision has nothing to check against.', 'Write one page: who the site is for, what it must do, what "done" looks like, what is out of scope.', 'Every prompt you give Claude Code can point at a line in the brief.'),
    q('requirements', 'planning', 'Clearly defined requirements', 1, 'Vague requirements become generated assumptions that look finished and are wrong.', 'List the pages, features and content the launch needs, each with an acceptance condition.', 'Each requirement has a way to show it is met — a page to open, a test to run.'),
    q('architecture', 'planning', 'A technical architecture', 2, 'Structure decided by accident is rebuilt later, usually after content and SEO depend on it.', 'Decide the page hierarchy, URL structure, data sources and how content is managed, before the build.', 'The URL structure and page list are written down and Claude Code was told to follow them.'),
    q('stack', 'planning', 'A defined technology stack', 1, 'A stack chosen mid-build leaves half-migrated code and dependencies nobody asked for.', 'Name the platform, framework, hosting and the tools that build and test it.', 'CLAUDE.md names the stack and the commands; a new session reproduces the build.'),
    q('dod', 'planning', 'A definition of done', 1, '"Done" left undefined means Claude Code stops at "it renders".', 'Write what must be true before any task is finished: checks run, page fetched, diff reviewed.', 'The definition is in CLAUDE.md and the agent shows the checks in its final message.'),
    q('git', 'planning', 'A Git repository with a clear branch strategy', 2, 'Without version control there is no rollback, no review and no way to know what changed.', 'Put the project in Git; work on branches; keep main deployable.', 'The last deploy corresponds to a commit you can name.'),
    // ---- claude configuration
    q('claudemd', 'claude', 'A CLAUDE.md file describing the project', 2, 'CLAUDE.md is the only context Claude Code has at the start of every session. Without it, every session begins from zero and guesses the rules.', 'Write a short CLAUDE.md: stack, commands, constraints, definition of done, things that must never be done.', 'Start a fresh session and ask Claude Code what the project rules are; it answers from the file.'),
    q('standards', 'claude', 'Coding standards Claude Code is told to follow', 1, 'Generated code drifts toward whatever the last prompt implied; standards keep sessions consistent.', 'Record formatting, naming, component and testing conventions in CLAUDE.md or a linked file.', 'Two sessions produce code in the same style; the linter passes.'),
    q('verify', 'claude', 'Claude Code is told how to verify its own work (test, lint and build commands it must run)', 2, 'An agent that cannot verify reports "done" on faith.', 'Name the exact commands in CLAUDE.md and require their output before a task is finished.', 'The final message of a task shows the commands and their results.'),
    q('reuse', 'claude', 'Reusable prompts or slash commands for repeated tasks', 1, 'Typing the same audit prompt slightly differently each time produces different audits.', 'Save the prompts you repeat as slash commands or skills with a fixed output format.', 'The same command run twice produces reports in the same shape.'),
    // ---- seo
    q('keywords', 'seo', 'Keyword and search-intent research', 1, 'Pages built without knowing the query they answer rank for nothing in particular.', 'For each key page, name the query it should answer and the intent behind it.', 'Every key page has a target query written next to it.', NOT_LANDING),
    q('seoarch', 'seo', 'An SEO site architecture (which pages exist, how they cluster and link)', 2, 'Search visibility is decided by structure before content: what pages exist, at what URLs, linked how.', 'Map the page hierarchy and internal links before building templates.', 'The map exists and the built site matches it.', NOT_LANDING),
    q('titles', 'seo', 'A page-title strategy', 1, 'Titles decide which query a page competes for and whether anyone clicks.', 'Define a title pattern per template and write unique titles for key pages.', 'No two pages share a title; none is truncated in results.'),
    q('descriptions', 'seo', 'A meta-description strategy', 1, 'A site-wide fallback gives searchers nothing page-specific to click.', 'Write descriptions for the pages that matter; make the fallback obvious so it gets replaced.', 'No description repeats across pages.'),
    q('linking', 'seo', 'An internal-linking plan', 1, 'Pages nothing links to are crawled late and rank on nothing but their own merit.', 'Decide which pages link to which; give every important page inbound links from relevant ones.', 'A crawl shows no orphan pages among the ones that matter.', NOT_LANDING),
    q('canonical', 'seo', 'Canonical tags on every page', 2, 'A wrong or missing canonical hands your ranking to another URL — often a staging host.', 'Emit a self-referencing canonical on the production host on every page.', 'The rendered head of a live page shows a canonical to itself on the production domain.'),
    q('schema', 'seo', 'Structured data / schema where appropriate', 1, 'Valid structured data earns rich results; invalid or dishonest markup is a policy risk.', 'Add JSON-LD that describes what the page visibly shows — nothing more.', 'Every block parses and the values match the visible page.'),
    q('sitemap', 'seo', 'An XML sitemap', 1, 'The sitemap is how engines learn what you consider canonical.', 'Generate one from the page list; exclude noindexed, redirected and staging URLs.', 'It lists every important URL and nothing that returns non-200.'),
    q('robots', 'seo', 'A robots.txt that allows what should be crawled', 2, 'A staging robots rule shipped to production hides the whole site.', 'Serve a production robots.txt that blocks only what should be blocked.', 'Fetch it from the production host; no Disallow covers a page that should rank.'),
    q('cwv', 'seo', 'Core Web Vitals checks on the key templates', 1, 'Slow, shifting pages lose visitors and ranking signal.', 'Measure LCP, INP and CLS on the templates that earn; name the LCP element.', 'Field or lab data passes on the key templates, or the failing element is known.'),
    q('gsc', 'seo', 'Google Search Console prepared (property verified, sitemap ready to submit)', 1, 'Without it you cannot see what Google did with the site.', 'Verify the property before launch and submit the sitemap at launch.', 'The property shows the sitemap as read.'),
    q('bing', 'seo', 'Bing Webmaster Tools / IndexNow prepared', 1, 'The second engine, and the source for several AI answer engines, is often forgotten.', 'Verify in Bing Webmaster Tools; set up an IndexNow key.', 'Bing shows the sitemap; the IndexNow key file is served.'),
    // ---- security
    q('secrets', 'security', 'Secret scanning (no keys or tokens in the repository)', 2, 'A committed secret is public the moment the repository is, and stays in history after deletion.', 'Scan the repository and its history; move secrets to environment variables; rotate anything found.', 'A scan of the full history finds nothing; the deploy works from environment configuration alone.'),
    q('deps', 'security', 'Dependency auditing', 1, 'Known-vulnerable packages are the cheapest attack there is.', 'Run the audit tooling for your stack and resolve or accept each finding deliberately.', 'The audit reports no unreviewed high or critical findings.'),
    q('owasp', 'security', 'An OWASP-style security review', 1, 'Generated code reproduces common weaknesses — injection, broken access control, insecure defaults.', 'Review the application against the OWASP Top 10 for the parts that take input or store data.', 'Each category has a note: applies / does not apply / reviewed.'),
    q('auth', 'security', 'Authentication and authorization reviewed (who can do what, and where it is enforced)', 2, 'Authorization enforced only in the UI is not enforced.', 'Check every server endpoint enforces who may call it; test as a wrong user.', 'A request as the wrong user is refused by the server, not just hidden by the interface.', { only: ['saas', 'wordpress', 'shopify', 'other', 'new', 'redesign', 'improve'], label: 'where applicable' }),
    q('headers', 'security', 'HTTP security headers configured', 1, 'Headers are the cheapest defence against clickjacking, sniffing and script injection.', 'Set Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options, Referrer-Policy and frame protection.', 'A response from the production host carries them.'),
    q('https', 'security', 'HTTPS configured with a valid certificate and HTTP redirected', 2, 'A site without working HTTPS is flagged by browsers and loses every visitor at the warning.', 'Provision the certificate, force HTTPS, and know how renewal happens.', 'http:// redirects to https:// in one hop; the certificate has more than 30 days left.'),
    q('envvars', 'security', 'Environment-variable management (per environment, never committed)', 2, 'Configuration in code ships secrets and points production at staging services.', 'Keep configuration in environment variables per environment; document the names, not the values.', 'The production deploy reads its configuration without any secret in the repository.'),
    q('prodconfig', 'security', 'A production configuration review (debug off, error pages, logging)', 1, 'Debug mode in production leaks stack traces and internals.', 'Review every setting that differs between development and production.', 'An error on production shows a friendly page, not a stack trace.'),
    q('backup', 'security', 'A backup strategy, with a restore tested', 2, 'A backup that has never been restored is a hope, not a backup.', 'Automate backups of the data the site cannot regenerate; restore one somewhere and open it.', 'A restore has been performed and the restored copy opened.', { not: ['landing'] }),
    q('saasdata', 'security', 'Tenant data isolation and API input validation reviewed', 2, 'In a multi-tenant application, one missing filter exposes every customer to every other.', 'Test cross-tenant access explicitly; validate every API input server-side.', 'A request for another tenant\'s record returns nothing.', SAAS),
    q('billing', 'security', 'Billing webhooks verified and idempotent', 2, 'An unverified webhook lets anyone grant themselves a subscription; a non-idempotent one double-charges or double-credits.', 'Verify webhook signatures; make handlers idempotent by event id.', 'A replayed webhook changes nothing the second time.', SAAS),
    q('shopcheckout', 'security', 'Checkout, payments and tax settings tested with a real test order', 2, 'A store that cannot take money is not launched.', 'Place a test order end to end, including the confirmation email and any digital delivery.', 'The test order appears in the admin with the right totals and the customer received what they bought.', SHOP),
    // ---- accessibility
    q('wcag', 'a11y', 'WCAG 2.2 AA considered in the design', 1, 'Accessibility retrofitted after launch costs more than designing for it.', 'Review the AA criteria that apply to your components and note how each is met.', 'A written note per applicable criterion.'),
    q('keyboard', 'a11y', 'Keyboard navigation works for every interactive element', 2, 'A control that cannot be reached by keyboard excludes users and fails audits.', 'Tab through every page; operate every control without a mouse.', 'Every control is reachable and operable by keyboard alone.'),
    q('focus', 'a11y', 'Visible focus states', 1, 'Without a visible focus indicator, keyboard users cannot tell where they are.', 'Keep or restore focus styles on every interactive element.', 'Tabbing shows a visible outline everywhere.'),
    q('semantic', 'a11y', 'Semantic HTML (landmarks, headings, lists, buttons)', 1, 'Assistive technology and crawlers both read structure from semantics, not from class names.', 'Use headings in order, landmarks for regions, real buttons and links.', 'The document outline reads sensibly with styles disabled.'),
    q('alt', 'a11y', 'Image alt text', 1, 'Images without alt are silent to screen readers and invisible to search.', 'Write alt text that says what the image conveys; empty alt for decoration.', 'No informative image has empty or missing alt.'),
    q('labels', 'a11y', 'Form labels associated with their fields', 2, 'An unlabelled field cannot be announced and is the most common reason a form is abandoned by assistive-technology users.', 'Use a visible label bound with for/id on every field; describe errors in text.', 'Every field announces its label; errors are announced.'),
    q('contrast', 'a11y', 'Colour contrast checked', 1, 'Low-contrast text fails for many sighted users too.', 'Check text and control contrast against AA ratios, in both themes if you have two.', 'No text below 4.5:1 (3:1 for large text).'),
    q('sr', 'a11y', 'Screen-reader considerations (names, roles, live regions)', 1, 'Custom components without names and roles are unusable with a screen reader.', 'Give custom widgets accessible names and roles; announce dynamic changes.', 'A screen reader announces each control by name and role.'),
    q('a11ytest', 'a11y', 'Accessibility testing performed (automated and by hand)', 1, 'Automated checks catch about a third of issues; the rest need a person.', 'Run an automated audit, then a keyboard-only and a screen-reader pass on the key pages.', 'Findings are recorded and the key pages pass both passes.'),
    // ---- testing
    q('functional', 'testing', 'Functional testing of the flows that matter', 2, 'A generated feature that was never exercised is an assumption with a UI.', 'Test the flows that earn or convert, as a visitor would.', 'Each key flow has been run end to end and the result recorded.'),
    q('responsive', 'testing', 'Responsive testing at phone, tablet and desktop widths', 1, 'Most visitors are on phones; a layout that overflows at 390 px loses them.', 'Test at 390, 820 and 1280 px; check no horizontal overflow.', 'No page scrolls sideways at phone width.'),
    q('browsers', 'testing', 'Cross-browser testing', 1, 'Safari and Firefox differ from Chrome in ways generated CSS rarely accounts for.', 'Test the key pages in at least Safari, Firefox and Chrome.', 'Key pages render and operate in each.'),
    q('errors', 'testing', 'Error-state testing (empty, failed, invalid)', 1, 'The happy path is the only one generated code is sure to handle.', 'Try empty inputs, failed requests and invalid data on every form and fetch.', 'Every error shows a message a visitor can act on.'),
    q('forms', 'testing', 'Form testing, including that submissions actually arrive', 2, 'A form that shows "Thanks" and delivers nothing is the most common silent failure on small sites.', 'Submit each form with a marker and confirm it arrived where a human reads it; test the empty-field case.', 'The marked submission is in the inbox or system, with a timestamp.'),
    q('links', 'testing', 'Broken-link testing', 1, 'Broken links are the first thing a visitor notices and the last thing a developer checks.', 'Crawl the built site for non-200 links, internal and external.', 'The crawl reports zero broken internal links.'),
    q('perf', 'testing', 'Performance testing', 1, 'Performance regressions arrive with every added script and image.', 'Measure the key templates; set a budget; check it before launch.', 'Key templates are within the budget you set.'),
    q('prodbuild', 'testing', 'The production build tested (not just the dev server)', 2, 'The dev server hides what the production build breaks: paths, environment, minification.', 'Build for production, serve the output locally, click through it.', 'The production build runs and the key pages work from it.'),
    q('regression', 'testing', 'Regression tests for things fixed once', 1, 'A bug fixed by a prompt returns with the next prompt unless a test holds it.', 'Write a test for each bug that has been fixed; run it in CI.', 'The suite fails if the fixed behaviour regresses.'),
    // ---- deployment
    q('procedure', 'deployment', 'A written deployment procedure', 2, 'A deploy that lives in one person\'s head cannot be repeated or reversed.', 'Write the steps, the command, who runs it and how you know it worked.', 'A second person can deploy from the notes.'),
    q('cicd', 'deployment', 'CI/CD that runs checks before deploy', 1, 'Checks that are not automated are skipped under time pressure.', 'Run build, tests and audits in CI; deploy only from green.', 'A failing check blocks the deploy.', NOT_LANDING),
    q('actions', 'deployment', 'GitHub Actions or an equivalent pipeline', 1, 'A pipeline is the difference between a deploy and a hope.', 'Add a workflow that builds, tests and deploys on merge to main.', 'The last deploy has a run you can open.', NOT_LANDING),
    q('envsep', 'deployment', 'Environment separation (development, staging/preview, production)', 1, 'Testing on production is how a bad change reaches every visitor at once.', 'Use preview deploys or a staging environment for every change.', 'Every change is seen somewhere before production.'),
    q('dns', 'deployment', 'DNS configured and verified (apex, www, mail records)', 2, 'DNS mistakes take the site — and often the email — down at launch.', 'Configure and verify the records ahead of time; lower the TTL before a change.', 'The domain resolves correctly from outside; mail records are intact.'),
    q('caching', 'deployment', 'A caching strategy', 1, 'No caching is slow; wrong caching serves stale or private content.', 'Decide cache rules per asset type and page; test that updates appear.', 'A deployed change is visible without a hard refresh within the expected time.'),
    q('rollback', 'deployment', 'A rollback procedure, rehearsed', 2, 'Every deploy is a bet; rollback is how you limit the stake.', 'Write the exact steps to return to the previous version; rehearse them once.', 'The previous version exists and a rollback has been performed and reversed.'),
    q('monitoring', 'deployment', 'Production monitoring (uptime, errors)', 1, 'Without monitoring your visitors are the alerting system.', 'Add an uptime check and error reporting; route them to someone.', 'A deliberate error reaches the person responsible.'),
    q('observability', 'deployment', 'Observability for the application (logs, traces, key metrics)', 1, 'A SaaS application that cannot be observed cannot be debugged in production.', 'Ship structured logs and a few key metrics; know where to look when a customer reports a fault.', 'A request can be followed from log to outcome.', SAAS),
    // ---- launch
    q('prelaunch', 'launch', 'A pre-launch checklist', 2, 'Launch faults are boring and repeatable: a noindex left on, a canonical to staging, an unsubmitted sitemap.', 'Use a checklist that requires evidence per line, not ticks.', 'Every line has the observation next to it.'),
    q('launchday', 'launch', 'A launch-day checklist and a go/no-go decision', 1, 'Launch day without a sequence is improvisation under pressure.', 'Write the order: DNS, verification, submission, announcements, who watches what.', 'Someone can say "go" from evidence, or "hold".'),
    q('analytics', 'launch', 'Analytics validated (events fire once, real-time view checked)', 1, 'Analytics installed is not analytics working; double-firing is common.', 'Fire each key event once and watch it arrive in the real-time view.', 'One click, one event, in the report.'),
    q('indexing', 'launch', 'Search-engine indexing checks (noindex removed, sitemap submitted)', 2, 'The single most damaging launch fault is shipping the staging noindex.', 'Fetch the production homepage head; submit the sitemap; check the Pages report after a week.', 'The production head says index; the sitemap is reported as read.'),
    q('404', 'launch', '404 checks on the launched site', 1, 'Old links and typos land on 404s that nobody sees but visitors.', 'Watch the 404 log for the first week; redirect or fix.', 'No high-traffic 404 remains unaddressed after a week.'),
    q('redirects', 'launch', 'Redirect validation', 2, 'Redirects that chain, loop or land on the homepage lose the traffic they were meant to keep.', 'Test every redirect for one hop, right status, right destination.', 'A check reports zero failures on the live origin.', { only: ['redesign', 'improve', 'shopify', 'wordpress', 'astro', 'saas', 'new', 'other'] }),
    q('postmon', 'launch', 'Post-launch monitoring', 1, 'The first days after launch are when the faults you missed show up.', 'Watch errors, uptime, forms and the 404 log daily for the first week.', 'A daily note exists for each of the first seven days.'),
    q('rev24', 'launch', 'A 24-hour review', 1, 'The first day tells you whether the launch worked at all.', 'Check indexing, analytics, forms and errors at 24 hours.', 'The review is written down.'),
    q('rev7', 'launch', 'A 7-day review', 1, 'A week in, search engines have started to react.', 'Review Search Console coverage, 404s and performance.', 'The review is written down.'),
    q('rev30', 'launch', 'A 30-day review', 1, 'A month in, the numbers mean something.', 'Compare against the pre-launch baseline; decide what to fix next.', 'The review is written down with the decisions.'),
  ];
  function applies(question, projectType) {
    if (question.only && question.only.indexOf(projectType) === -1) return false;
    if (question.not && question.not.indexOf(projectType) !== -1) return false;
    return true;
  }
  return { PROJECT_TYPES: PROJECT_TYPES, USAGE: USAGE, CATEGORIES: CATEGORIES, STEPS: STEPS, QUESTIONS: Q, applies: applies };
})();
