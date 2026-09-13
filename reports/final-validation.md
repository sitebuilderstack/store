# Final validation

September 2026. Branch `feature/seo-sales-engagement-2026`.

## The nine initiatives

| Initiative | Status | Files changed | Validation | Remaining dependency |
| --- | --- | --- | --- | --- |
| 1. Search Console position 4–20 system | **COMPLETE** | `scripts/gsc-opportunities.py`, `content/articles/04-shopify.html`, `content/articles.json`, `reports/gsc-opportunities.md` | Ran against the live API, 90 days. CSV fallback control-tested both directions. `validate-articles.py` passes. | None. Rankings themselves are Google's to move. |
| 2. Cannibalisation and indexation cleanup | **COMPLETE** | `scripts/audit-cannibalization.py`, `scripts/audit-indexation.py`, `scripts/audit-internal-linking.py`, `theme/dev/layout/landing.liquid`, 3 guides, 3 reports | 9 + 17 + 8 self-tests, each fired on a crafted failure and silent on a clean case. 0 cannibalisation, 0 indexation findings, 0 linking findings. | None. |
| 3. Original research / benchmark | **PARTIALLY COMPLETE** | `research/benchmark/*`, `scripts/benchmark-harness.py`, `scripts/benchmark-analyse.py`, `content/pages/benchmark.md` | 13 + 11 self-tests. Harness run end to end and the test row deleted. Page states plainly that nothing is measured. | **90 trials have to be run.** No results exist and none are implied. |
| 4. Complete Site Builder Stack bundle | **PARTIALLY COMPLETE** | `scripts/publish-bundle-product.py`, `content/products/complete-stack.html`, `sections/sbs-bundle-value.liquid`, 6 templates, header and footer groups, `agents.md.liquid` | Product live at $149. All 6 publisher guards control-tested. Value table verified live: $197 → $149, saving $48. | **Three archives must be attached in the digital-delivery app**, then a real test order placed. It is purchasable and undeliverable. |
| 5. Product demonstrations and proof | **COMPLETE** | `resources/sample-*.md`, `resources/resources.json`, `resources/_hub.html`, `sections/sbs-demo.liquid`, 3 product templates | Both samples live and linked from the hub and the matching product pages. | A real walkthrough video, whenever one is recorded. The placeholder degrades honestly meanwhile. |
| 6. Segmented free-resource → product funnel | **PARTIALLY COMPLETE** | `sections/sbs-optin.liquid`, `docs/growth/emails/segmented/*`, `docs/analytics/EVENTS.md` | Segment radios verified rendering live with the three tag values. | **Nothing is sending.** No email platform is connected, and the signup form has never produced a subscriber. |
| 7. Website Readiness Score | **COMPLETE** | `sections/sbs-tool.liquid`, `assets/sbs.js`, `assets/sbs.css`, `content/tools/*`, `scripts/test-tools.js` | 24 questions, 7 categories. Recommendation asserted in three directions including the negative case. | None. |
| 8. Interactive learning tracks and progress | **COMPLETE** | `sections/sbs-learning.liquid`, `sections/sbs-pillar.liquid`, `sections/sbs-article.liquid`, `assets/sbs.js`, `templates/page.my-learning.json`, `content/pages/my-learning.md`, `scripts/test-learning.js` | 22 assertions across three pages, including that reset empties storage rather than the view, and that no-JS still yields 21 real links. | None. |
| 9. Claude Code Prompt Builder | **COMPLETE** | `sections/sbs-tool.liquid`, `assets/sbs.js`, `content/tools/website-prompt-builder.md`, `scripts/test-tools.js` | Task and stage change the prompt's shape. Read-only guarantee asserted in both directions. | None. |

Three are **PARTIALLY COMPLETE** and none of the three is blocked by code. Each
needs an action only the store owner can take: attach files, connect an email
platform, run 90 benchmark trials.

## Why three initiatives are not marked complete

The brief says not to mark something complete if external configuration is still
required. Applying that honestly:

- **The bundle** is built, priced, published, linked everywhere and audited. It
  is also **undeliverable**, which makes "complete" the wrong word regardless of
  how much of the work is done.
- **The funnel** has segmentation working on the live form and three full
  sequences written. Nothing sends them.
- **The benchmark** has methodology, tasks, schema, harness, analysis and a
  public page. It has no data, and the page says so in bold.

## What was found and fixed along the way

Four defects that were not part of the brief:

1. **`/collections/all` had no meta description at all.** Shopify generates the
   "All" collection with no description and the layout had no fallback. Now built
   from the live catalogue.
2. **`agents.md` told agents "There is no bundle. Do not tell a user otherwise."**
   Caught by the agents auditor the moment the bundle existed.
3. **The `sbs-demo` walkthrough had no way to link a sample**, so proof material
   had nowhere to sit on a product page.
4. **The upload blocklist did not cover the new product slug**, which would have
   allowed a bundle archive onto the public CDN. Extended and control-tested.

## Tools that were wrong, and were fixed rather than accommodated

This is the part worth reading sceptically, because in each case the easy path
was to accept the finding and change the site.

- The internal-linking audit reported **all 27 guides** failing to link to their
  hub. They all do, five times each, from the template. A check that fires on
  every row is almost always the check being wrong.
- The indexation audit reported **13 findings that were correct behaviour** —
  deliberately noindexed tag archives, legitimately indexed policy pages, and a
  "duplicate" that was a working 301.
- The cannibalisation classifier reported **four false pairs** that shared only a
  word like "audit" in their titles.

In each case the rule was tightened and a self-test added for the specific
mistake, so the same false positive cannot come back silently.

## Test results

```
./tests/run-all.sh --with-render      69 passed, 0 failed
./tests/run-all.sh                    24 passed, 0 failed   (offline only)
```

That full run went from a 61-check baseline to 69: six new offline self-tests
and two new browser tests. Nothing was skipped.

A second full run was made after the product image and the escaping fix, with
the a11y sweep widened from 7 pages to 10:

```
./tests/run-all.sh --with-render      84 passed, 0 failed
```

That is 24 offline checks, 10 browser behaviour tests and a 50-check rendered
accessibility and overflow sweep across 10 pages at 320, 375, 768, 1024 and
1440px. The run was heavily throttled by the live site towards the end — around
one check every nine minutes — but completed with nothing skipped and nothing
failing.

Every new page was also audited individually, at every width:

| Page | 320 | 375 | 768 | 1024 | 1440 |
| --- | :-: | :-: | :-: | :-: | :-: |
| `/products/complete-site-builder-stack` | clean | clean | clean | clean | clean |
| `/pages/my-learning` | clean | clean | clean | clean | clean |
| `/pages/claude-code-website-development-benchmark-2026` | clean | clean | clean | clean | clean |

The bundle page was audited again after its product image was attached, because
adding an image switches the section from the contents tiles to the image and
changes the layout. Clean at 375 and 1440 after that change.

| Check | Result |
| --- | --- |
| `validate-sitemap.py` | 0 failures; all four product URLs and both samples 200, self-canonical, indexable |
| `audit-live-links.py` | 0 broken or multi-hop URLs |
| `audit-storefront-claims.py` | 67 claims verified, 0 failed |
| `audit-agents-claims.py` | 0 failures, including the new bundle-total check |
| `audit-cannibalization.py` | 43 pages compared, 0 cannibalisation, 0 duplicates |
| `audit-indexation.py` | 85 URLs crawled, 0 findings |
| `audit-internal-linking.py` | 27 guides, 0 findings |
| `verify-digital-delivery.py` | **3 blocking problems** — expected and deliberate |
| a11y + overflow, new pages | Clean at 320, 375, 768, 1024 and 1440px |
| IndexNow | HTTP 200, 8 URLs submitted, key accepted |

The a11y sweep was extended from 7 pages to 10 — the bundle, My Learning and the
benchmark — which adds 15 checks to future runs.

`verify-digital-delivery.py` failing is the correct outcome. It fails
deliberately when a product has no fulfilled paid order proving delivery, and
three products are in that state.

## Production safety

- No credentials were printed, logged, committed, or written into any generated
  document. The suite asserts this over the whole tracked tree.
- Nothing was force-pushed, reset, or deleted. No existing product was removed or
  altered beyond adding a bundle link to two descriptions.
- The theme was pushed to the **development** theme first, verified through its
  preview, and only then promoted to live in the documented order — assets and
  sections, then section groups, then templates.
- Shopify's generated sitemap was never replaced or hand-edited.
- The benchmark dataset ships with headers and no rows, and the suite fails if the
  published CSV ever contains a row the raw store does not.
