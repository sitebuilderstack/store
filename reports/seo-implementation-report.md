# SEO implementation report

September 2026. Everything below was measured or changed; nothing is projected.

## The constraint that shaped every decision

The site is **fourteen days into Search Console**. Over 90 days it has 1,093
impressions, 3 clicks, 134 queries and 21 pages with any impressions at all.

More importantly, from the URL Inspection API: **18 URLs indexed, 24 discovered
and not indexed**, out of 57 in the sitemap.

That last number decided the shape of this work. A page Google has chosen not to
fetch cannot rank, and adding more pages does not help the ones already waiting.
So this cycle deliberately published **two** new pages and improved existing ones,
rather than publishing a content batch.

## Action 1 — Search Console position 4–20 system

### What was built

`scripts/gsc-opportunities.py` already existed and reads the live API through a
service account. It was extended with:

- A `--report opportunities` mode writing `reports/gsc-opportunities.md` in the
  requested column format, with a **recommended action per row**.
- A `--csv` import path for environments without API access, which refuses a
  query-only or page-only export rather than guessing the join. Control-tested
  both directions: a valid Queries+Pages export parses; one missing the `Page`
  column is refused with the exact export instructions.
- A conservative action classifier. Most rows return "Watch — too few
  impressions to act on", which is the correct answer at this volume and is more
  useful than inventing a task per query.

### What the data actually said

The positions 4–20 band contains **eight query/page rows**, and the majority are
one person's certification quiz question pasted into Google verbatim, several
times, hitting the GitHub Actions guide. Optimising for it would be pointless.

Three rows were genuinely actionable:

**1. A guide ranking position 2.0 with zero clicks.**
`/blogs/guides/build-shopify-store-with-claude-code` ranked 2.0–2.6 for variants
of *shopify theme-check liquid linter install cli machine readable output*, across
12 impressions, with 0 clicks.

The page **did not mention theme-check at all.** Google was ranking it on
adjacency to the Shopify theme workflow.

This was the interesting decision of the cycle. Rewriting the title to mention
theme-check would have made the title more accurate about the *query* and less
accurate about the *page* — the exact "never make a title more clickable than the
page is accurate" failure. So the missing content was added instead: a new
`Theme Check, and getting output an agent can read` section covering CLI install,
`--output json`, `--fail-level`, and the two surprises in parsing the output.

Every flag and the JSON schema in it were **verified by running the tool**, not
recalled: `npx @shopify/cli@latest theme check --help` for the flags, and a real
run against this theme for the output shape. The description was then updated to
mention Theme Check, which is now true.

**2. `mcp__github_inline_comment__create_inline_comment` at position 6.3.** The
GitHub Actions guide does cover this in a working workflow, but its description
did not mention inline PR review comments. Description updated; content already
supported the claim.

**3. The highest-demand cluster is not in the 4–20 band at all.** *claude code
seo* and *claude code for seo* carry 83 impressions between them at position
~50. No metadata change reaches position 50. That is a coverage and authority
problem, and it is what the benchmark and internal linking work is for.

`scripts/validate-articles.py` rejected the first description rewrite for being
164 characters against a 158 limit. Both were shortened rather than the limit
being raised.

## Action 2 — Cannibalisation and indexation

### Cannibalisation

`scripts/audit-cannibalization.py` is new. It compares every pair of the 43
content pages on two axes — shared heading vocabulary (topic) and shared
title/h1 vocabulary (intent) — and cross-checks against Search Console for
queries that return more than one URL.

**Result: zero probable cannibalisation, zero duplicates.**

The first version reported four. All four were false: pairs like
`claude-code-website-security-audit` vs `claude-code-accessibility-audit`, which
share the word *audit* in their titles and almost nothing else. The classifier
now requires intent **and** topic overlap together, because on a site where every
title contains the same brand words, intent alone is not evidence. Nine
self-tests cover the classification boundaries in both directions.

Terms common to the whole site (`claude`, `code`, `website`) are excluded, or
every page resembles every other page.

### Indexation

`scripts/audit-indexation.py` is new. It reuses the existing live crawler rather
than writing a second one, and adds sitemap agreement, duplicate metadata,
parameter behaviour and — where available — what Google actually did.

The first run reported 14 findings. **Thirteen were the tool being wrong**, and
fixing the tool rather than the site was the correct response in each case:

- Eight noindexed tag archives, which are noindexed by a deliberate, documented
  decision in `landing.liquid`. Now encoded as expected, with the reason.
- Five `/policies/` pages flagged as "should not be indexable". Indexing them is
  legitimate, and one already takes impressions.
- One duplicate title: `/pages/privacy-policy` and `/policies/privacy-policy`.
  The first **301-redirects to the second**. The duplicate check was comparing
  post-redirect content; it now keys on the final URL. A redirect is not a
  duplicate.

**One genuine finding remained and was fixed:** `/collections/all` had no meta
description at all. Shopify generates the "All" collection with no description,
and the layout had no fallback. Now built from the live catalogue, so it cannot
go stale — it currently reads "4 downloadable products" and counted the new
bundle by itself.

Parameter handling was tested rather than assumed. Tracking parameters, sort
parameters and `?page=1` all canonicalise back to the clean URL.

### Internal linking

`scripts/audit-internal-linking.py` is new, and its first version reported that
**all 27 guides failed to link to their hub.** They all do — five times each,
from `sbs-article.liquid`. A check that fires on every single row is almost
always the check being wrong.

Rewritten to verify template guarantees once against the theme, and to measure
what templates cannot supply: contextual links in body copy. That left three real
findings — `claude-code-astro`, `claude-code-wordpress` and
`claude-code-vs-cursor-web-development` had no contextual inbound link from any
other page's body. All three were fixed with links placed where the subject
already came up: the platform table in the build guide, and the editor-comparison
paragraph in the vibe-coding guide.

**Findings now: zero.**

The audit also surfaced a commercial gap: the $59 conversion toolkit had **no
guide pointing at it**, because no guide is about conversion. That is a content
gap, not a linking bug, and is recorded in the content roadmap rather than fixed
by forcing a mismatched CTA onto an unrelated guide.

## Action 3 — Original research

`research/benchmark/` contains the methodology, six tasks with acceptance
criteria fixed before any trial, the field-by-field schema, a recording harness
and a headers-only dataset.

**No trials have been run and the page says so in bold.** The results section is
generated by `scripts/benchmark-analyse.py` from the raw rows, so the page is
structurally incapable of implying a result it does not have. Eleven self-tests
cover the empty state, the partial state (a task complete on one platform is
withheld), and the full state.

The suite also carries a check that fails if the published CSV ever contains more
rows than the raw store — control-tested by adding a fabricated row and watching
it go red.

Published at `/pages/claude-code-website-development-benchmark-2026`, with the
conflict of interest stated on the page.

## Structured data

Audited across the live site by the existing crawler. Organization, WebSite,
Person, Product, Article, BreadcrumbList and FAQPage are present and valid; the
suite asserts no `Review` or `AggregateRating` markup exists anywhere, since
there are no reviews.

## What is measurably different

| | Before | After |
| --- | --- | --- |
| Pages with no meta description | 1 | 0 |
| Guides with no contextual inbound link | 3 | 0 |
| Indexation findings | 1 genuine | 0 |
| Cannibalisation findings | 0 | 0 |
| Products unreachable from the content graph | 1 | 0 |
| Search Console reports | 3 | 4 |

## What was deliberately not done

- **No content batch.** With 24 URLs discovered-and-not-indexed, publishing more
  would compete for crawl budget the site has not earned.
- **No redirects or noindexing.** The cannibalisation audit found nothing that
  warranted either, and acting anyway would have been acting on the tool's first
  draft.
- **No duplicate readiness or prompt-builder pages.** The brief suggested
  `/pages/website-readiness-score` and `/pages/claude-code-prompt-builder`;
  `/pages/launch-readiness-score` and `/pages/website-prompt-builder` already
  exist and are indexed. Creating near-identical URLs would have manufactured the
  exact cannibalisation Action 2 exists to remove. Both existing tools were
  extended instead.
