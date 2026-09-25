# Engagement cycle — completion report, 17 September 2026

Status words used: **implemented** · **tested locally** · **tested in preview** · **published** · **scheduled** · **draft** · **blocked**.

Branch `feature/engagement` (from master `0c91637`, tag `engagement-baseline`). Both Site Builder Stack themes carry the release. Since 20 September 2026 the **published** one is `191811453220` (named "Site Builder Stack — Development"; republished after a third-party theme was briefly live) and `191797854500` ("Site Builder Stack — Live") is the unpublished copy used for previews. `scripts/theme_push.py` refuses the published theme without `SBS_ALLOW_LIVE=1` whichever id that is. Nothing was merged to master or pushed to the mirror — that is the owner's call, as before.

## 1. What was implemented

| Feature | Status | Where |
| --- | --- | --- |
| "Try this on your project" module: seven deterministic generators, editable result, Copy (with fallback), Download (useful filename), Save to My Project, one next step, no-JS fallback, inputs preserved on validation error | implemented · tested locally · tested in preview · **published** | `snippets/sbs-try.liquid`, `assets/sbs-engage.js`, `sections/sbs-article.liquid` |
| Placed in six existing guides (CLAUDE.md → project section; technical SEO → scoped read-only audit prompt; Shopify → next safe workflow; landing page → functional validation checklist; WordPress → maintenance checklist + report; GitHub/Cloudflare → regression plan) and all three new articles | **published** | `content/articles/03,04,17,24,27,32,34,35,36` (`<div data-sbs-try-slot>`), metafield `sbs.try` |
| Labs hub + four labs (A Launch Readiness, B Technical SEO, C Conversion Functionality, D Website Operations): scenario, declared sample data with public fixture download, starting state, four guided decisions each, evidence view, explanations for every wrong option, corrected version, reset, save-to-project, product link after value, static no-JS version with every answer, four-frame accessible screenshot walkthrough per lab | implemented · tested locally · tested in preview · **published** | `content/labs/*.json` → generated `snippets/sbs-lab-fixtures.liquid`, `sections/sbs-lab.liquid`, `assets/sbs-labs.js`; `/pages/labs`, `/pages/lab-*` |
| My Projects workspace: create/rename/select/delete (confirm), platform/objective/optional URL, artifacts, guide/lab/challenge records with six states, tasks, "Continue your project", self-assessment history, JSON export (project / all), Markdown export, JSON import with validation and merge-vs-replace confirm, versioned storage with tested non-destructive migration from `sbs-learning`, corrupt/quota/blocked handling with in-memory fallback and warnings, honest limitations copy | implemented · tested locally · tested in preview · **published** | `assets/sbs-projects.js`, `assets/sbs-workspace.js`, `sections/sbs-projects.liquid`, `/pages/my-projects`; `/pages/my-learning` unchanged and still working |
| Weekly Website Fix: hub, archive (blog `weekly-fix` + Atom feed), challenge template, four challenges (problem, prerequisites, scope, observe-first workflow, copyable prompt, example evidence, completion criteria, common mistakes, guide + lab links, Save to My Project as self-reported, redacted summary export), editorial runbook | **published** (#1) · **scheduled** (#2 24 Sep, #3 1 Oct, #4 8 Oct, 09:00 America/Los_Angeles) | `content/challenges/*.html`, `scripts/publish-challenges.py`, `sections/sbs-challenge.liquid`, `sbs-weekly-fix.liquid`, `sbs-weekly-archive.liquid`, `docs/engagement/WEEKLY-FIX-RUNBOOK.md` |
| Reminders | implemented (form) · **not automated** by design | the existing Shopify customer form (`sbs-optin`) on the hub with its own tag `weekly-fix`, segmentation off, no download, frequency stated as "at most one a week, none if skipped", unsubscribe via Shopify Email. Markup and POST target verified in preview; **no live submission was made** (it would create a customer record). Sending is a manual Shopify Email to the tagged segment — see runbook. The feed exists regardless. |
| Analytics: twelve allowlisted events, ids only, dedupe of one-shot events, success-only `artifact_saved`, activation defined, no invented rates; pixel and collector updated to subscribe and count the identifier | implemented · tested locally (payload reduction) · tested in preview and on live (each event once; no request carried typed data) | `assets/sbs.js` `track()`, `docs/analytics/EVENTS.md`, `analytics/custom-pixel.js`, `analytics/collector-worker.js` (the pixel remains **not installed** — a manual admin step, unchanged from before) |
| Navigation: header "Labs" link; footer Practical labs / Weekly Website Fix / My projects; cross-links from the resources hub, tools hub and My Learning; agents.md updated | **published** | `sbs-header-group.json`, `sbs-footer-group.json`, `resources/_hub.html`, `content/tools/_hub.md`, `content/pages/my-learning.md`, `templates/agents.md.liquid` |

## 2. Three articles

| Article | Words (excl. code) | Status | Connections |
| --- | --- | --- | --- |
| Claude Code Website Maintenance: A Safe Weekly Checklist — `/blogs/guides/claude-code-website-maintenance` | 2,718 | **published**; in the Production track (last step) and pillar | maintenance module (checklist + report), Operations Lab, Weekly Fix #1/#3, project tasks; Operations & Maintenance System CTA |
| Website Migration SEO Checklist: Validate Your Move With Claude Code — `/blogs/guides/website-migration-seo-checklist-claude-code` | 2,545 | **published**; in the SEO track and pillar | migration module (checklist + url-map starter CSV), Technical SEO Lab; Migration System + SEO Toolkit CTAs |
| Playwright Testing With Claude Code: Forms, Links, and Regression Checks — `/blogs/guides/claude-code-playwright-website-testing` | 2,314 | **published**; in the Production track (after the deploy guide) and pillar | regression module, Conversion Lab, contact-form challenge; Launch System CTA |

Each: direct answer first, prerequisites, workflow, worked examples, failure cases, validation, download, next action; TOC; author/dates from the CMS; 4–6 internal links; ≥2 inbound links added from existing guides (27, 24, 16-cluster, 17, 21, 19, 32, 15); BlogPosting + BreadcrumbList schema (existing snippet, no duplicates); self-referencing canonicals; indexable; OG/Twitter meta; listed in Shopify's generated sitemap (`sitemap_blogs_1.xml`). Sources with dates: `research/engagement-articles-sources.md`. No invented metrics.

Tested examples behind the articles (all reproducible from the repo):
- `downloads/claude-code-maintenance-kit/weekly_check.py` against a local fixture with a planted 404 link and a missing form → 2 FAIL rows with evidence; repaired → 7/7 PASS (`scripts/test-weekly-check.py`). TLS path exercised read-only against the live site (68 days to expiry).
- `downloads/website-migration-seo-kit/check_redirects.py` against two local fixture servers: correct 301 passes; homepage dump, chain, loop, 302, wrong identity, 404 and timeout all fail with the reason; malformed rows stop the run with exit 2; `--limit` and `--host-rewrite` behave (`scripts/test-redirect-checker.py`, 18 checks).
- `downloads/playwright-website-tests/` run on Node 22 with `@playwright/test` 1.63.0: 15 passed, 1 skipped; email check disabled → the email test failed with `Received: "Thanks! We will email you to confirm."`; restored → 15 passed. Along the way the suite caught a loose assertion (`/email/i` matched the success message) and a hidden-landmark locator issue; both are in the article.

Downloads (public CDN, free, verified 200): `claude-code-maintenance-kit.zip`, `website-migration-seo-kit.zip`, `playwright-website-tests.zip`, and four `lab-*-fixture.zip`. Built deterministically by `scripts/build-downloads.py`.

## 3. Tests

- Existing suite before changes: 43/43 on master. After: **52/52** offline (`tests/run-all.sh`), new checks: graph engagement self-test (28 mutations detected), generated-snippet freshness (labs, schedule), storage core (42), generators/allowlist/scoring (60+ incl. a deliberately wrong answer failing on every lab), redirect checker (18), weekly checker (10), bundle syntax/registration, pixel/doc agreement (61 events), agents.md claims.
- Browser (`tests/run-all.sh --with-render`): `scripts/test-engagement-browser.js` — module → generate → copy → save (no duplicate on repeat) → My Projects (list, continue action, rename, task, export, merge import, malformed import rejected, delete confirm cancelled, keyboard) → lab (wrong answer fails with explanation and no Next; correct passes; completion; score 3/4; product link only at the end; save as example-verified; reset) → challenge (in-progress, then self-reported; never verified) → privacy (no request carried the typed marker; console clean) → storage disabled (warning; in-memory works) → no-JS (fallback text; static lab with answers; workspace explanation). **0 failures on the preview and on live.**
- Pre-existing storefront tests (nav menu, mobile menu, tools, analytics events, route engine, library filter, checklist, copy buttons, picker): 0 failures on the preview.
- Rendered accessibility audit at 390 and 1280: clean on every new page (two findings found and fixed first: unstyled secondary buttons with 1.03:1 contrast; a disabled select).
- Performance at 412 px (live preview): LCP 752–868 ms, CLS 0 (0.043 on My Projects), 147–177 requests. Baseline before: LCP 712 ms on the technical-SEO guide, 176 requests.
- Full render suite on live (`tests/run-all.sh --with-render`): 152 checks. Two runs: three checks flagged a transient Shopify console warning (`Invalid 'X-Frame-Options' header … ALLOW-FROM`, emitted by Shopify's own frames, not by the theme) and passed on individual re-runs; one genuine pre-existing finding — the collection page's card heading inherited the 49 px page-level h2 size and a long product title overflowed at 1024 px — was fixed in `sbs-collection.liquid` + `sbs.css` and re-audited clean.
- Live SEO crawl (`audit-seo-site.py`): no findings. Responses, canonicals, robots, meta, schema and sitemap coverage checked for all 12 new URLs (table in this session's log; all self-canonical, indexable, valid JSON-LD).
- Screenshots: `docs/engagement/screenshots/` (six pages × 390/820/1280, plus 16 walkthrough frames) and `docs/engagement/baseline/` (before).

## 4. What was not done, and why

- **Search Console / analytics aggregates**: unavailable to this session (no authorised access). No traffic, ranking or conversion figures appear anywhere; activation is defined but not measured.
- **Reminder email sending**: not automated, on purpose. The spec allows reminders only through the existing authorised integration with separate consent; that integration is a Shopify customer form plus manual Shopify Email. A live test submission was not made to avoid creating a customer record. The flow is documented in the runbook; the feed is the automated alternative.
- **Lab walkthrough recording**: a screenshot walkthrough with alt text and captions was chosen over a recording (spec allows either; no fake player).
- **Custom pixel installation**: still a manual admin step (unchanged state from `analytics/README.md`); the pixel source now subscribes to the new events.
- **Merge and mirror push**: not done; awaiting the word.

## 5. Rollback

Documented in `docs/engagement/README.md`. Theme files revert to `master`'s copies (`git show master:theme/dev/<path>`); new templates can be deleted so pages fall back to defaults; content can be unpublished. Readers' saved projects (`sbs-projects`) and learning progress (`sbs-learning`) are browser-local and untouched by any of it.

## 6. Where things are

- Task checklist: `docs/engagement/TASKS.md`
- Runbook: `docs/engagement/WEEKLY-FIX-RUNBOOK.md`
- Analytics: `docs/analytics/EVENTS.md`
- Sources: `research/engagement-articles-sources.md`
- Downloads source: `downloads/`; built archives: `dist/free/` (ignored by git; rebuild with `scripts/build-downloads.py`)
