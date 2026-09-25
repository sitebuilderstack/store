# Engagement layer — how it works, how to change it, how to roll it back

Shipped 17 September 2026 on branch `feature/engagement` (base: master `0c91637`,
tag `engagement-baseline`). Four connected features and three guides; the
completion report is `COMPLETION-REPORT-2026-09-17.md` in this directory.

## Map

| Piece | Source of truth | Renders through | Behaviour |
| --- | --- | --- | --- |
| Shared ids (modules, labs, challenges, article→module) | `content/content-graph.json` | `scripts/publish-graph.py` writes `sbs.try` on articles; `scripts/build-labs.py` / `build-weekly.py` generate Liquid | `scripts/validate-graph.py` (+ `--self-test`) |
| Try-this modules | `snippets/sbs-try.liquid` (fields, titles, next steps) | `sections/sbs-article.liquid` swaps `<div data-sbs-try-slot></div>` in the article body | `assets/sbs-engage.js` (seven generators) |
| Labs | `content/labs/*.json` | generated `snippets/sbs-lab-fixtures.liquid` + `sbs-labs-index.liquid`; `sections/sbs-lab.liquid`, `sbs-labs-hub.liquid`; templates `page.lab.json`, `page.labs.json` | `assets/sbs-labs.js` (`score()` is pure and tested) |
| My Projects | — (browser-local) | `sections/sbs-projects.liquid`, `templates/page.my-projects.json`, copy in `content/pages/my-projects.md` | `assets/sbs-projects.js` (store) + `assets/sbs-workspace.js` (UI) |
| Weekly Website Fix | graph `challenges` + `content/challenges/*.html` | blog `weekly-fix`; `sections/sbs-challenge.liquid` (`article.challenge.json`), `sbs-weekly-fix.liquid` (hub page), `sbs-weekly-archive.liquid` (`blog.weekly-fix.json`); generated `snippets/sbs-weekly-schedule.liquid` | `assets/sbs-labs.js` (challenge panel); `scripts/publish-challenges.py`; runbook `WEEKLY-FIX-RUNBOOK.md` |
| Analytics | allowlist in `assets/sbs.js` `track()` | — | `docs/analytics/EVENTS.md`; pixel + collector updated |
| Loading | `layout/landing.liquid` renders `<script id="sbs-assets" type="application/json">` with the four bundle URLs | `sbs.js` `initFeatureBundles()` loads them only when `[data-sbs-try]`, `[data-sbs-lab]`, `[data-sbs-challenge]` or `[data-sbs-projects]` is present | a page without any of them loads nothing extra |

## Storage (My Projects)

- Key `sbs-projects`, `{v:1, activeId, projects{id:{…}}}`. Limits: 25 projects,
  100 artifacts and 50 tasks per project, 64 KB per artifact, ~2 MB total
  (checked before the write; refused with a message, never truncated).
- First load migrates `sbs-learning` (My Learning) into a default project
  "My website" and leaves the original key untouched. Tested in
  `scripts/test-projects-store.js`.
- Corrupt record → reset to empty with `recovered` flag and a notice; quota
  failure → `quota` flag and a notice; storage throwing (private windows,
  blocked site data) → in-memory store for the visit with a warning. All three
  tested (node + browser).
- Import: must be `format: sitebuilderstack-projects`, `v ≤ 1`, < 4 MB,
  valid JSON with at least one usable project. Unknown fields dropped, text
  stored as text, URLs http(s) only, keys sanitised. Merge (newer `updated`
  wins) or replace, each behind a confirm. Markdown export cannot be
  imported and the message says so.
- States: `not-started` · `in-progress` · `read` · `generated` ·
  `self-reported` · `example-verified`. The UI never promotes anything to
  `example-verified` except a lab whose known answers were all matched, and
  the wording everywhere says that verifies the reader against the fixture,
  not their site.
- Not encrypted; the page says so and tells readers not to store secrets.

## Privacy rules enforced in code

- `track()` reduces engagement payloads to allowlisted id keys matching
  `^[a-z0-9-]{1,80}$`; one-shot events dedupe per page view.
- No project field, generated text, URL or note is ever put in a query
  string, share link, error report or event. The browser journey test types
  a marker (`Zq7…`) into every input and asserts no request carried it.
- Generators are deterministic and run in the page; no external calls.
- Lab fixtures are data (`textContent` everywhere); the JSON block escapes
  `</` so it can never close its own script element (tested).

## Tests

Offline (`tests/run-all.sh`, 52 checks): graph self-test, generated-snippet
freshness, storage core (42 assertions), generators + allowlist + lab
scoring (60+), redirect checker on local fixtures (18), weekly checker on a
broken-then-repaired fixture (10), bundle syntax + registration, pixel/doc
agreement, agents.md claims.

Browser (`tests/run-all.sh --with-render`): `scripts/test-engagement-browser.js`
— the full journey at 390 px, storage-disabled, no-JS, privacy and console
assertions; plus the pre-existing storefront tests, all passing on the
preview and on live.

Rendered accessibility (`audit-rendered-a11y.js` → `check-a11y-json.py`):
clean at 390 and 1280 on every new page. Performance at 412 px on live
preview: LCP 750–870 ms, CLS 0 (0.04 on My Projects while the switcher
appears), 147–177 requests.

## Changing things

- A module's copy or fields: `snippets/sbs-try.liquid`; its generator:
  `assets/sbs-engage.js` `GEN[id]`; keep `content/content-graph.json`
  `modules` in step (test-engagement checks the next-step URLs agree).
- A lab: edit `content/labs/<id>.json`, run `python3 scripts/build-labs.py`,
  push the two generated snippets. `build-labs.py` refuses dangling evidence
  ids, an answer that is not an option, or a wrong option without an
  explanation.
- A challenge: see `WEEKLY-FIX-RUNBOOK.md`.
- Screenshots and walkthrough frames: `node scripts/screenshot-engagement.js
  <dir> [--preview id]`; upload frames with `scripts/upload-files.py`; put
  the URLs in the lab JSON `walkthrough` and rebuild.

## Rollback

Theme (live `191797854500`): every changed file's previous version is
`git show master:theme/dev/<path>`. To reverse the release without touching
content: push those six pre-existing files back
(`assets/sbs.css assets/sbs.js layout/landing.liquid sections/sbs-article.liquid
sections/sbs-header-group.json sections/sbs-footer-group.json`) with
`SBS_ALLOW_LIVE=1 python3 scripts/theme_push.py 191797854500 <checkout of master> …`,
then delete the new templates (`page.lab.json`, `page.labs.json`,
`page.my-projects.json`, `page.weekly-fix.json`, `blog.weekly-fix.json`,
`article.challenge.json`) so those pages fall back to the default templates.
Readers' saved projects live in their browsers under `sbs-projects` and are
not touched by any theme change; `sbs-learning` was never modified.

Content: pages can be unpublished with `pageUpdate` (`isPublished:false`);
the three guides with `articleUpdate`; the challenges as in the runbook. The
`sbs.try` metafield on the six existing guides is harmless without the
snippet (an empty `<div>` renders).
