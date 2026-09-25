# Third product implementation — September 2026

Claude Code Conversion & Revenue Optimization Toolkit, $59.

---

## 1. Executive summary

A third digital product was built, packaged, listed and launched. It is a real
downloadable toolkit — 99 files, 65,301 words — not a listing over a thin prompt
pack, and the storefront around it was updated from a two-product store to a
three-product one.

The product owns the **Convert → Optimize → Grow Revenue** stage of the
lifecycle. It does not duplicate either existing product: the Launch System's
only CRO material is one 1,035-word landing-page workflow, and the SEO toolkit
has none. Where the three do overlap, this one defers — full accessibility
auditing to the Launch System, search-performance analysis to the SEO toolkit —
and the workflows say so where they stop.

Its central discipline is that it never predicts a percentage lift and never
recommends a manipulative tactic. Both are enforced by a build-time check, not
just by intention: `validate-cro-toolkit.py` refuses to package the bundle if a
predicted lift or a recommended dark pattern appears in any file, and
`publish-cro-toolkit-product.py` refuses to publish the listing if one appears
in the marketing copy.

**Four defects were found on the existing site during the work.** Three of them
were live and none was introduced by this cycle. They are in §7.

---

## 2. What shipped

| | |
| --- | --- |
| Product | Claude Code Conversion & Revenue Optimization Toolkit |
| Price | $59 USD, one payment |
| URL | `/products/claude-code-conversion-revenue-optimization-toolkit` |
| SKU | `SBS-CCCRO-V1` |
| Status | ACTIVE, published to Online Store |
| Files | 99 |
| Modules | 13 |
| Workflows | 70 |
| Commands | 68 |
| Templates | 6 |
| Worked examples | 4 |
| Words | 65,301 |
| Archive | `claude-code-conversion-revenue-optimization-toolkit-v1.0.zip`, 218,172 bytes |
| SHA-256 | `9619ab31e24b04c785f2de5da0adbaa697f8bdb7cc600112d9fdda1240a19302` |
| Content digest | `1d1cd703953d931e42c51bbf06b8f14456deb5802e335a1698e8ef019c279392` |
| Delivery | **File not attached — see §11** |

Every number above was counted from the bundle by
`scripts/validate-cro-toolkit.py`, not typed. The publisher reads the same
counts and refuses to run if the product description disagrees with any of them.

---

## 3. The product

### Structure

```
01-core/                       8 workflows   master audit, modes, finding format,
                                             prioritisation, evidence, prohibitions
02-page-audits/                8 workflows   home, landing, pricing, product,
                                             category, checkout, signup, content
03-funnels/                    5 workflows   mapping, drop-off, micro-conversions,
                                             source fit, lead generation
04-elements/                   7 workflows   CTAs, forms, nav, pricing, trust,
                                             objections, conversion copy
05-ecommerce/                  6 workflows   Shopify audit, product detail, cart,
                                             checkout, merchandising, post-purchase
06-saas/                       5 workflows   funnel, onboarding, trial-to-paid,
                                             packaging, demo flow
07-analytics/                  7 workflows   audit, measurement plan, GA4,
                                             privacy-first, event QA, attribution
08-experimentation/            7 workflows   framework, hypotheses, sample size,
                                             design, results, when not to test, log
09-user-behaviour/             5 workflows   usability, recordings, surveys,
                                             voice of customer, method choice
10-performance-accessibility/  3 workflows   performance, a11y barriers, mobile
11-platforms/                  4 workflows   WooCommerce, no-code, JS frameworks,
                                             what is fixable where
12-reports/                    5 workflows   exec summary, full report, quick wins,
                                             experiment report, client delivery
13-templates/                  6 templates   roadmap, finding log, backlog,
                                             measurement plan, copy brief, hypothesis
commands/                     68 commands    nine categories
claude-md/                     2 files       the section, and a complete example
examples/                      4 examples    each including what the first pass got wrong
```

### The four modes

Every workflow declares one: **AUDIT** (analyse, change nothing), **PLAN**
(sequence findings), **IMPLEMENT** (one named change), **VALIDATE** (confirm it
worked). The validator fails any workflow that does not declare a mode. This is
the convention the product is built on: never let one session both find and fix.

### The finding format

Thirteen fields, of which the important one is the evidence class: **proven
problem / strong heuristic / experiment opportunity / insufficient data**.
Findings are scored Impact × Confidence ÷ Effort and banded into this week, this
month, next quarter, and *do not do* — with two overrides: critical severity
jumps the queue, and measurement gaps come first.

### What it refuses

`01-core/ETHICAL-BOUNDARIES.md` enumerates the prohibitions by name — fabricated
evidence, manufactured urgency and scarcity, pricing deception, interface
manipulation, trapping, privacy violations, unsupported claims — and every
workflow restates the relevant part in its own constraints. That repetition is
deliberate: a prohibition stated once at the start of a long session does not
survive to the end of it.

Two of the four worked examples show this failing in practice. In example 1 the
first audit pass recommended a stock scarcity indicator on a store that does not
track inventory reliably, despite the prohibition being in the prompt. The
example includes the correction that removed it.

---

## 4. Storefront

### New

- `theme/dev/templates/product.cro-toolkit.json` — product page: 16 contents
  tiles, a 9-step walkthrough, 9 FAQs, a closing CTA to the SEO toolkit
- `content/products/cro-toolkit.html` — the description, including the
  three-product comparison table
- `theme/dev/sections/sbs-ecosystem.liquid` — the three-product row, resolving
  each card through `all_products[handle]` so a drafted or renamed product drops
  out rather than rendering a dead link at a stale price
- `theme/dev/snippets/sbs-product-tiles.liquid` — the contents grid, extracted
  so its two call sites cannot drift

### Changed

- **Homepage** — the ecosystem row inserted after the FAQ, not before it. The
  page still sells the flagship for its whole length; the row exists for the
  reader who has decided the Launch System is not their problem.
- **Both existing product pages** — an ecosystem row above their closing CTA,
  each framed for that page's reader.
- **Header** — the Products submenu now lists three; it already supported four.
- **Footer** — the Product column became Products and lists all three plus a
  compare link. The support column's "Get it — $99" became "Get the Launch
  System", since $99 is no longer the store's only price.
- **`/collections/all`** — "One product." replaced. Card blurbs now come from
  each product's SEO description rather than from stripping the description's
  HTML, which produced cards opening with "Who this is for Developers,
  founders and agencies who…".
- **`agents.md`** — three products described with counts, "exactly one product"
  removed, and the hard-coded "$99, a single payment" in the accuracy notes
  replaced. `audit-agents-claims.py` now verifies all three products' counts;
  it verified only the flagship's before.
- **Case study** — the launch snapshot is left as written and annotated with
  what has changed since. Rewriting the record would make it less useful.

### Product visuals

`scripts/generate-product-image.py` generates a 1600×1200 product image for a
toolkit from its bundle: the module grid with real per-module counts, in the
same tokens, mark and grammar as `generate-brand-assets.py`. Images were
generated and attached for both toolkits, with descriptive alt text. Each is
also the page's `og:image`, replacing the generic site-wide card.

Every number on the image is counted, because an image is the one place a stale
count is invisible to a text-based check.

---

## 5. Analytics

No new tooling. One new event, `product_ecosystem_clicked`, on the ecosystem
cards — a distinct name from `product_nav_clicked` (header menu) and
`product_cta_clicked` (closing CTA), because merging three placements into one
number makes all three unreadable.

`test-analytics-events.js` gained both directions: the event fires on an
ecosystem card, and the ecosystem card does **not** also fire
`product_nav_clicked`.

---

## 6. Verification

### New checks

**`scripts/validate-cro-toolkit.py`** — 16 self-tested checks. Two are specific
to this product and matter more than the structural ones:

- a **predicted percentage lift** anywhere in the bundle
- a **recommended manipulative tactic** — a countdown timer, a scarcity
  indicator, confirmshaming

Both fire on the phrasing a model actually produces, and both are guarded
against the toolkit's own prohibitions: the clearest way to prohibit "add a
countdown timer" is to write the phrase down, so a match is only a defect when
nothing in the run-up to it negates the sentence. The self-test proves the
negation guard is not a blanket excuse: a prohibition earlier in a file does not
license a recommendation later in it.

It also checks that every workflow declares a mode, that the stated command
count is true, that command ids are unique, and that every internal file and
directory reference resolves.

**Both directions, every check.** `--self-test` breaks each one on a crafted
input and confirms it stays silent on the real bundle. 16 detections, 0
failures.

### Extended checks

- `audit-storefront-claims.py` is now three-product aware, checks per-module
  tile counts against the directory each tile names, and resolves a claim to the
  product the surrounding sentence names — necessary now that every product page
  compares itself to the other two.
- `audit-agents-claims.py` verifies the SEO and conversion toolkits' counts, not
  only the flagship's.
- `test-nav-menu.js` and `test-mobile-menu.js` read the catalogue instead of
  asserting a hard-coded count of two. A literal failed the day a third product
  was added, which is backwards: the drift worth catching is a product the menu
  omits.
- `upload-files.py` refuses every paid product's slug, not only the flagship's.

### Results

**`./tests/run-all.sh --with-render` — 61 passed, 0 failed**, against the live
site after publishing.

| Area | Result |
| --- | --- |
| Repository checks, incl. 2 new for the conversion bundle | 18 passed |
| Browser behaviour — 8 scripts | 0 failures |
| Accessibility & overflow — 7 URLs × 5 widths | 35 clean |
| Landing layer renders with no unresolved Liquid | pass |

The a11y sweep now includes the new product page and `/collections/all`, taking
it from 25 checks to 35.

Separately: `validate-cro-toolkit.py --self-test` — 16 detections, 0 failures.
`verify-archive.py` — 99 entries, CRCs valid, no empty entries, no credential
patterns, single top-level directory. `audit-live-links.py` — 0 broken.
`validate-sitemap.py` — 0 failures; the new product URL is present, 200,
self-canonical and indexable.

Performance on the new product page, measured in a lab run rather than
estimated: **LCP 724 ms, CLS 0, TTFB 47 ms**, 112 requests, 1.17 MB
transferred of which 1.02 MB is JavaScript — effectively all of it Shopify's
own; the theme ships two assets totalling 128 KB. One image, with dimensions
and alt text, not lazy-loaded because it is the page's largest element. INP is
not reported: it cannot be measured in a lab and needs field data.

No conversion or revenue effect is claimed from any of this. It is the
measurement and the mechanism; what moves is a question for a period of real
traffic.

---

## 7. Defects found

Four, all pre-existing, three of them live.

**1. Every contents tile on the SEO toolkit's page was empty.** The template set
`note` on each tile; `sbs-product.liquid` renders `meta`. Seventeen tiles
rendered with an empty `<span>`. Live since that product launched. Fixed, and
one tile's count was wrong once it became visible — "01 Technical SEO — 10
files" for a directory holding 4.

**2. `og:title` and `twitter:title` were double-escaped.** Shopify's
`page_title` arrives already escaped for a title containing an ampersand, and
the layout applied `escape` again, producing `&amp;amp;` — which link unfurlers
render as the literal text "&amp;". The `<title>` tag was correct because it
prints `page_title` unfiltered, which is why it survived unnoticed. Fixed with
`escape_once`.

**3. Comparison tables in a product description scrolled the whole page
sideways.** The table rules existed only under `.sbs-article__body`, so a table
in a product description had no wrapper overflow and no min-width. The SEO
toolkit's three-column table pushed the page to 454px at a 375px viewport.
Adding a fourth column made it worse, which is how it was found. Fixed by giving
`.sbs-rte` the same treatment.

**4. The header CTA advertised $99 on every page.** It was hard-wired to the
configured product, so the $39 and $59 product pages carried "Get it — $99"
pointing at the homepage, above that product's own buy button. Found by running
the toolkit's own CTA inventory command against this site. It now follows the
product being viewed.

The fourth is worth noting for what found it: `commands/04-ELEMENTS-COPY.md`
C-25, run against sitebuilderstack.com as a dry run of the product.

---

## 8. Toolkit dry runs

Six workflows were run against sitebuilderstack.com before shipping, as QA of
the product rather than of the site.

| Workflow | What it produced |
| --- | --- |
| `commands/01-DISCOVERY.md` C-05 — above-the-fold inventory at 390×844 | The CRO page's buy button sat at y=838, 17px below the fold. The summary was shortened twice and it now clears at y=749/802 |
| `commands/04-ELEMENTS-COPY.md` C-25 — CTA inventory | Found defect 4 in §7: the header CTA said "$99" on a $59 page |
| `commands/02-PAGE-AUDITS.md` C-13 — pricing visibility | Each page shows its own price with the currency stated. No mandatory charge is undisclosed; there is nothing to disclose |
| `commands/03-FUNNELS-ANALYTICS.md` C-20 — fire-once verification | Positive plus the negative cases; both directions are now in the suite |
| `05-ecommerce/SHOPIFY-CRO-AUDIT.md` Phase 1 — theme reconnaissance | Accurate inventory: 2 layouts, 18 templates, 2 assets (sbs.css 77KB, sbs.js 51KB), 5 snippets, one `content_for_header`, no third-party injection |
| `commands/07-EXPERIMENTS.md` C-48 — should this be tested | **Do not test** |

Two results are worth reporting in full.

**C-13 raised something worth deciding on rather than fixing.** Each product
page now displays three prices — its own in the buy panel, and the other two
inside the comparison table and the ecosystem row. Both of those are labelled
and neither is adjacent to a buy button, so the page's own price is unambiguous.
It is recorded here because "more than one price on a page" is the shape of a
real defect even when this instance is not one.

**C-48 gave the answer most CRO material will not.** Asked whether the
homepage's three-product row should be A/B tested, it worked the gate in order —
not broken, not a legal requirement, a losing arm harms nobody — and then
reached traffic: the store has **one paid order in its history**, a test order.
At that volume no minimum detectable effect is reachable at any duration, and
the correct output is that testing is not viable and the change should be made
on judgement and said to have been made on judgement. That is what the workflow
returned.

**A measured trade-off, recorded rather than chased:** at 360×800 the buy button
sits below the fold on both toolkit pages (850px and 831px). The flagship clears
it at 746px because its title is shorter. Closing this would mean cutting real
information from the summary; the toolkit's own guidance is that there is no
single fold and that the primary action should be reachable within one short
scroll, which it is.

## 9. Repository documentation

- `docs/BUNDLE-ARCHITECTURE.md` — what is ready for a future bundle and what is
  not built, with the rule that a bundle price must be a real price. **No bundle
  exists and none is advertised.**
- `docs/CONTENT-ROADMAP.md` — ten articles in three tiers, with what each must
  do, what is deliberately excluded, and the horizons at which to judge them.
- `docs/STORE-ARCHITECTURE.md`, `docs/ANALYTICS-SETUP.md`,
  `docs/SHOPIFY-AUTH.md`, `docs/QA-REPORT.md`, `README.md` — updated from
  one- and two-product language.

---

## 10. What was deliberately not done

**The two existing bundles were not repackaged.** Their READMEs still describe
two products. Rebuilding either changes its SHA-256, and the SEO toolkit's file
has already been attached in the Digital Products app — a rebuild would leave
the attached file stale against a published checksum, and only the store owner
can re-upload it. This is a real inconsistency inside a paid product and it is
listed as a manual action rather than closed silently.

**No bundle, and no discount.** The architecture is ready; nothing is
advertised. A struck-through price the store never charged would contradict the
product's own prohibitions on its own storefront.

**No case study, no testimonial, no results claim.** There are no customers with
results to report, and the toolkit prohibits predicting lifts.

---

## 11. Manual actions

1. **Attach `claude-code-conversion-revenue-optimization-toolkit-v1.0.zip` in
   the Digital Products app and place a real test order.** The product is
   purchasable and cannot be delivered until this is done. The Admin API cannot
   see whether a file is attached; only a fulfilled paid order proves it.
   `verify-digital-delivery.py` fails on exactly this, for both toolkits.
2. **The SEO toolkit's file is still unproven** by the same check.
3. **Request indexing** for the new product URL and `/collections/all`.
4. **Consider a v1.1 of both existing bundles** to correct their "two products"
   READMEs — bundled with the next content change, so the re-upload happens once.

---

## 12. Definition of done

| # | Criterion | Status |
| --- | --- | --- |
| 1 | A real, substantial downloadable product exists | 99 files, 65,301 words |
| 2 | It does not duplicate the other two | Measured: 1 CRO file in the Launch System, 0 in the SEO toolkit |
| 3 | Flagship master audit | `01-core/MASTER-CRO-AUDIT.md`, 8 phases |
| 4 | Standardised finding format and prioritisation | 13 fields, 4 evidence classes, I×C÷E |
| 5 | At least 50 commands | 68, in 9 categories |
| 6 | Four modes throughout | Enforced by the validator |
| 7 | Manipulative tactics prohibited and enforced | Build-time check, control-tested |
| 8 | No predicted lifts | Build-time check, control-tested; also on the listing |
| 9 | Packaged with a checksum | 218,172 bytes, SHA-256 published, round-trip verified |
| 10 | Shopify product live at $59 | ACTIVE, published, correct digital settings |
| 11 | Conversion-focused product page | 16 tiles, 9-step walkthrough, 9 FAQs, comparison table |
| 12 | Homepage updated without clutter, flagship preserved | One row, after the FAQ |
| 13 | Stale one-product language removed | 4 files; case study annotated rather than rewritten |
| 14 | Internal linking between all three | Header, footer, homepage, all three product pages, collection |
| 15 | Accessibility, performance, responsive verified | Clean at 320–1440px on every changed page |
