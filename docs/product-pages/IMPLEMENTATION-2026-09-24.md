# Product pages — purchase-path release, 24 September 2026

**Status: RELEASED TO PRODUCTION, 24 September 2026.** Authorised in session by
the store owner. Validated on the unpublished preview first, then pushed to the
published theme and re-verified against production.

| | |
| --- | --- |
| Branch | `feature/product-pages-2026-09` (from `master` at `000fe8e`) |
| Preview theme | **191797854500** — *Site Builder Stack — Live* (UNPUBLISHED), validated here first |
| Published theme | **191811453220** — *Site Builder Stack — Development* (MAIN) — **released** |
| Released | 18 files, 24 September 2026, commits `d06aa1a` + `0ebdca0` |
| Production verification | **326/326 static**, **144/144 browser**, policy and all eight pages verified consistent |
| Description edits | applied to the live products 24 September 2026, read back and re-verified |
| Preview URL | `https://sitebuilderstack.com/products/<handle>?preview_theme_id=191797854500` |
| Products in scope | the eight listed below; no other product was read or written |
| Checks | 326 static + 144 browser, **all 470 passing** against production |

Production release is **not** authorised. `docs/THEME-WORKFLOW.md` says of the
`SBS_ALLOW_LIVE` flag that guards a push to the published theme: *"Do not set
it."* Nothing in this session overrides that, so the work stops at the preview.
§7 gives the exact command when the owner wants it live.

---

## 1. Baseline — what was actually wrong

Captured from the **rendered** published pages on 24 September 2026, not from
the templates. Raw HTML is in `backup-2026-09-24/` alongside the product export.

| # | Finding | Class | Evidence |
| --- | --- | --- | --- |
| F1 | The sticky purchase bar was hard-wired to `claude-code-website-launch-system` in the footer section group, which renders on every page. All eight product pages shipped markup reading *"The Claude Code Website Launch System · $19.99 · instant download"* with a button to `/#buy` — including the three $39.99 pages and the $29.99 page. | **Verified inconsistency, not a visible defect** | `sbs-footer-group.json`; every baseline HTML file |
| F1a | …but it was never *shown* on a product page: `initSticky()` returned early without `[data-sbs-hero-cta]`, which only `sbs-hero` emits and only the homepage uses. | Already mitigated by accident | `sbs.js` line 38; `data-visible="false"` in all eight |
| F2 | No closing purchase action for the product being viewed. On seven pages the last call to action was a **primary** button for a *different* product; on the eighth it was a primary button to `/#buy` on the homepage. | **Confirmed defect** | `PRIMARY LINK -> /products/…` in all eight baselines |
| F3 | Header links *What's included* → `/#included`, *How it works* → `/#how`, *FAQ* → `/#faq` left every product page for the homepage. Seven pages already had their own `#included`; all eight had `#walkthrough`; five used `#faq` and three used `#questions`. `#how` existed nowhere. | **Confirmed defect** | header extract from every baseline |
| F4 | The bundle page said *"sales are final"* twice. The store's refund policy lists five circumstances in which a full refund is given and states that statutory rights are unaffected. | **Confirmed contradiction** | product description + FAQ block vs `/policies/refund-policy` |
| F5 | *"No video is published yet"* on seven pages. | Confirmed stale copy | `sbs-demo` body setting |
| F6 | `block_order` in four templates listed `p6` twice and omitted the Shopify Automation toolkit entirely — six of seven standalone products shown. Shopify de-duplicated the id at render, so nothing appeared twice, but the catalogue row was wrong and one product was missing from it. | **Confirmed defect** | `product.json`, `seo-toolkit`, `cro-toolkit`, `ops-system` |
| F7 | *"Four narrower systems"* and *"Conversion is the third of four problems"* while seven standalone products are sold. | Confirmed stale copy | ecosystem headings |
| F8 | The Launch System description said *"No installation, no dependencies"* without naming Claude Code as a prerequisite. The other seven correctly say *"nothing to install beyond Python 3"*. | Confirmed inconsistency | product descriptions |
| — | The earlier review's *"Launch System promotional purchase blocks on other product pages"* — the visible version of F1 — **did not reproduce.** Reported here as F1/F1a rather than restated as found. | Already resolved | see F1a |

---

## 2. What changed, and where

Every fix is in a **shared component**, so it applies to all eight pages from
one implementation. No purchase logic was copied eight times.

### Theme code

| File | Change |
| --- | --- |
| `sections/sbs-sticky-buy.liquid` | Resolves the page's own product instead of a theme setting. On a product page it is now a real `{% form 'product' %}` add-to-cart with a distinct id (`sbs-sticky-form`); elsewhere it links to the configured product's page rather than a homepage anchor that resolved to nothing off the homepage. |
| `sections/sbs-final-buy.liquid` | **New.** The closing purchase panel: the page's own product, live price, native form, and printed delivery / requirements / licence / refund facts. One implementation, all eight pages. |
| `sections/sbs-cta.liquid` | Gains an `Emphasis` setting. On a product page it is now `secondary` — a ghost button under a standing *"A different product"* label — so a cross-sell cannot read as the page's purchase action. Its blank-URL fallback now resolves to the selected product's page instead of `/#buy`. |
| `sections/sbs-header.liquid` | Nav links gain `product_anchor`. On a product page a section link goes to that page's own section. |
| `sections/sbs-faq.liquid` | Gains `alias_anchor`, so renaming the anchor to `faq` everywhere keeps `#questions` addressable. |
| `sections/sbs-product.liquid` | Gains `description_anchor`, used only on the Launch System, whose description has no `id="included"` of its own. |
| `assets/sbs.js` | `initSticky()` keys off the buy panel, so the bar works on a product page at all; it counts **every** buy panel, so it hides over the closing one too. `placement` travels with a CTA click. `init()` is idempotent and `shopify:section:load` re-runs only the section-scoped initialisers, each of which now marks what it binds — including `initFaq`, which would otherwise have collected a second click handler per button in the theme editor. |
| `assets/sbs.css` | Closing-panel layout; the price qualifier no longer wraps mid-phrase; the sticky control's `<form>` is the flex item, which stops *"Add to cart"* wrapping to three lines at 390px. |
| `sections/sbs-header-group.json` | `product_anchor` set: `included`, `walkthrough`, `faq`. |
| `templates/product*.json` (8) | Closing panel inserted before the cross-sell with per-product copy; cross-sell set to secondary; FAQ anchor normalised to `faq` with the old id aliased; the duplicated `p6` replaced with the missing Shopify Automation card; the bundle card added to the Shopify toolkit's row; stale counts corrected; the *"no video"* sentence replaced. |

### Not changed

Product ids, handles, titles, variant ids, SKUs, prices, compare-at prices,
status, publication, inventory, digital-delivery configuration, entitlements,
metafields, media, policies, navigation structure, checkout, payments, apps.
`products-before.json` is the pre-change export of all eight; re-running the
export and diffing it is how that claim is checked, not asserted.

---

## 3. Per-product result

All eight verified on the preview theme. "Proof asset" is what a buyer can
inspect on the page today — the brief's per-product output previews are **not**
built; see §8.

| Product | What changed | Proof asset on the page | Purchase flow | State |
| --- | --- | --- | --- | --- |
| Website Launch System | closing panel; header anchors; `#included` supplied; ecosystem repaired (+Shopify card, count corrected); cross-sell demoted | written walkthrough of the download's structure | opening + closing + sticky, all this product, one variant | **live** |
| SEO & Website Audit Toolkit | closing panel; header anchors; FAQ anchor normalised; ecosystem repaired; cross-sell demoted | written walkthrough; free SEO sample linked from the description | same | **live** |
| Conversion & Revenue Optimization Toolkit | as above, plus the stale *"third of four"* heading | written walkthrough | same | **live** |
| Operations & Maintenance System | closing panel; header anchors; ecosystem repaired; cross-sell demoted | written walkthrough; a real command and its output in the description | same | **live** |
| Shopify Automation & Admin API Toolkit | closing panel; header anchors; bundle card added to its row; cross-sell demoted | written walkthrough; the export → review → import sequence in the description | same | **live** |
| Migration & Replatforming System | closing panel; header anchors; cross-sell demoted | written walkthrough | same | **live** |
| Agency & Client Delivery System | closing panel with a **team-licence route** (`team_license_inquiry_clicked`); header anchors; cross-sell demoted | written walkthrough | same | **live** |
| Complete Site Builder Stack | closing panel with a **comparison route** (`product_comparison_opened`); header anchors; FAQ refund answer corrected; cross-sell demoted | `sbs-bundle-value` arithmetic; written walkthrough | same | **live**; one description edit still staged, see §6 |

---

## 4. Tests, and what they actually cover

```bash
python3 docs/product-pages/qa-product-pages.py              # 310 static checks, preview
python3 docs/product-pages/qa-product-pages.py --live       # the same, against production
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser \
  node docs/product-pages/qa-product-browser.js             # 144 browser checks
python3 scripts/audit-theme-links.py                        # 0 errors, 5 known policy warnings
```

Both suites read the **rendered** page. Every defect in §1 was invisible in the
templates, which is why.

A preview theme is served against a session cookie, not the query string alone.
The first run of the static suite reported 145/254 because a stateless fetch had
silently returned the *published* theme. It now carries a cookie jar; without
that, the suite audits the wrong thing and says everything is fine.

**Static — per product:** the right product and price; one variant id across
every form; all three purchase forms present with unique ids; the sticky bar's
product, title and price; no primary button for another product; no primary
button to a homepage anchor; the cross-sell is secondary and labelled; each
header anchor resolves to an id that exists on the page; the closing panel
states delivery, requirements, licence and links the policy; no duplicate or
missing catalogue card; no *"no video"*, no *"sales are final"*, no asserted
scarcity, no countdown markup, no `Complete purchase` mislabel, no unresolved
Liquid, no public placeholder; exactly one `Product` schema whose price matches
the page and which carries no fabricated rating.

**Browser — 8 products × 390 / 768 / 1280:** no horizontal overflow; no console
errors from this theme; the sticky bar hidden at rest, shown mid-page, hidden
again over the closing panel, carrying the right product, fitting the viewport,
with a ≥44px tap target and a real add-to-cart; the buy button takes keyboard
focus; a double click submits once; every header anchor resolves in the DOM; no
overflow at 640px (a 200% zoom equivalent).

Two assertions were wrong and were corrected rather than worked around:
scarcity matched on the word *"countdown"*, which flagged the CRO and bundle
pages for describing the dark patterns they refuse; and *"hides over the
closing panel"* scrolled to the document end, where a tall footer has already
pushed the panel off screen and a visible bar is correct.

Shopify's own `monorail` / `shopify_pay_page_load` beacon fails in a headless
sandbox. Those errors are excluded by name; everything else counts.

### Not tested

- **Completed checkout and download delivery.** No authorised test-payment
  route exists in this session, and the brief forbids creating real paid orders
  or switching the live store into test mode. The purchase journey is verified
  **to the point of `/cart/add`** — form action, method, variant id, single
  submission. Cart contents, checkout, order line items, confirmation email and
  download delivery are **unverified**. The journey is not marked as passed.
- **Production rendering.** Everything above is the preview theme.
- **Performance before/after.** Not measured under comparable conditions, so no
  number is offered.

---

## 5. Measurement

**The storefront publishes custom events and nothing collects them.** Measured
again today: `webPixel` returns *"No web pixel was found for this app."* Every
`Shopify.analytics.publish` call — including the CTA events below — fires into
nothing until a custom pixel is created by a person in **Settings → Customer
events**. This release does not change that and does not claim otherwise. See
`analytics/README.md` and `docs/REMAINING-MANUAL-STEPS.md`.

No analytics provider was added and no ecommerce event was duplicated.

**Authoritative commerce events stay Shopify's.** `product_viewed`,
`product_added_to_cart`, `checkout_started` and `checkout_completed` are
emitted by Shopify to Web Pixels. The theme does not re-emit them; a button
click is not a purchase and is not recorded as one.

**Added here**, on existing theme plumbing, as an intent signal only:

| Event | Where | `placement` |
| --- | --- | --- |
| `product_cta_clicked` | closing panel add-to-cart | `final_panel` |
| `product_cta_clicked` | sticky bar | `sticky_bar` |
| `product_cta_clicked` | cross-sell button | `cross_sell` |
| `product_cta_clicked` | homepage closing CTA | `closing_cta` |
| `team_license_inquiry_clicked` | Agency page closing panel | `final_panel_secondary` |
| `product_comparison_opened` | bundle page closing panel | `final_panel_secondary` |

Payload: `label`, `href`, `product` (handle), `placement`, `source`. No personal
data, no credentials, no customer input. `placement` was added to `ENGAGE_KEYS`
so engagement events may carry it under the same id-only rule.

Not added, because they are not observable here: walkthrough opened (the
section is always visible, not a disclosure), video started/completed (no video
exists), sample download completed (a link click is not a completed download).

**Primary measure**, once a pixel exists: net sales attributable to
online-store sessions ÷ online-store sessions, over a fixed window in USD, net
of discounts and refunds, excluding tax and shipping. That is revenue per
session, not profit. **No baseline is recorded, because none was measured.**
Nothing in this document claims a sales effect.

---

## 6. Shared store data — APPLIED 24 September 2026

A product description is live the moment it is saved, whichever theme is
published, so these were staged separately and applied on the owner's explicit
authorisation, after the theme release.

```bash
python3 docs/product-pages/staged-description-changes.py           # show the diff
python3 docs/product-pages/staged-description-changes.py --apply   # applied 24 Sep 2026
```

Both were applied and read back. A second run reports *"already applied — nothing
to do"*, so the script is safe to re-run. Every protected field on both products
— handle, title, status, template suffix, price, currency, variant id, SKU,
compare-at price, availability, SEO title and description, publication date and
variant count — was diffed against `products-before.json` afterwards and is
unchanged.

1. ✅ **Complete Site Builder Stack** — *"sales are final"* replaced with the five
   circumstances the refund policy actually lists, plus the statutory-rights
   sentence. The FAQ copy of the same claim is already corrected in the theme;
   this is the description copy. With it applied the live suite reports
   **310/310**.
2. ✅ **Website Launch System** — *"No installation, no dependencies"* qualified so
   it names Claude Code and a terminal, matching the other seven pages.

Each edit is an exact-string replacement against a re-read of the live
description, skipped rather than forced if the text has changed, verified by
read-back, and idempotent.

**Also staged, not written:** `/policies/refund-policy` still says *"The Claude
Code Website Launch System is a downloadable file"* when eight products are
sold. Widening that sentence changes no eligibility, but a policy edit is the
owner's call and is not made here.

---

## 7. Release and rollback

### Released

Done on 24 September 2026 with the commands below. Kept for the next release.

```bash
# 1. re-run both suites against the preview
python3 docs/product-pages/qa-product-pages.py
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser node docs/product-pages/qa-product-browser.js

# 2. push to the PUBLISHED theme — only when authorised
SBS_ALLOW_LIVE=1 python3 scripts/theme_push.py 191811453220 theme/dev \
  assets/sbs.js assets/sbs.css \
  sections/sbs-final-buy.liquid sections/sbs-sticky-buy.liquid sections/sbs-cta.liquid \
  sections/sbs-header.liquid sections/sbs-product.liquid sections/sbs-faq.liquid
SBS_ALLOW_LIVE=1 python3 scripts/theme_push.py 191811453220 theme/dev sections/sbs-header-group.json
SBS_ALLOW_LIVE=1 python3 scripts/theme_push.py 191811453220 theme/dev templates/product.json \
  templates/product.seo-toolkit.json templates/product.cro-toolkit.json \
  templates/product.ops-system.json templates/product.shopify-toolkit.json \
  templates/product.migration-system.json templates/product.agency-system.json \
  templates/product.complete-stack.json

# 3. smoke-test production
python3 docs/product-pages/qa-product-pages.py --live
```

Push order matters: assets and Liquid, then the section group, then templates.
Shopify validates references at upload time and rejects a group whose section
file is not yet there.

### Rollback

Switching themes does **not** restore product data. The two halves roll back
separately.

**Theme** — `docs/product-pages/rollback-published-2026-09-24/` holds the files
**as the published theme served them immediately before this release**, pulled
from theme 191811453220. That is the authoritative rollback set. (The earlier
`backup-2026-09-24/` holds the same files from `theme/dev` plus the eight
baseline rendered pages and the product export.) Restore with:

```bash
SBS_ALLOW_LIVE=1 python3 scripts/theme_push.py 191811453220 \
  docs/product-pages/rollback-published-2026-09-24 \
  assets/sbs.js assets/sbs.css sections/sbs-sticky-buy.liquid sections/sbs-cta.liquid \
  sections/sbs-header.liquid sections/sbs-product.liquid sections/sbs-faq.liquid
SBS_ALLOW_LIVE=1 python3 scripts/theme_push.py 191811453220 \
  docs/product-pages/rollback-published-2026-09-24 sections/sbs-header-group.json
SBS_ALLOW_LIVE=1 python3 scripts/theme_push.py 191811453220 \
  docs/product-pages/rollback-published-2026-09-24 templates/product.json \
  templates/product.seo-toolkit.json templates/product.cro-toolkit.json \
  templates/product.ops-system.json templates/product.shopify-toolkit.json \
  templates/product.migration-system.json templates/product.agency-system.json \
  templates/product.complete-stack.json templates/agents.md.liquid
```

`sbs-final-buy.liquid` did not exist on production before this release;
restoring the templates above removes every reference to it, after which the
orphaned section file is inert and may be deleted at leisure.

The pre-release copies from `theme/dev` are also in
`docs/product-pages/backup-2026-09-24/`:
`sbs-sticky-buy.liquid`, `sbs-cta.liquid`, `sbs-header.liquid`,
`sbs-product.liquid`, `sbs.js`, `sbs.css`, `sbs-header-group.json`, and the
eight `product*.json`. `sbs-final-buy.liquid` is new; deleting the section from
each template's `order` removes it. Restore with the same `theme_push.py`
invocation, pointing at the backup directory, or `git revert` the commit and
push `theme/dev/` again. `sbs-faq.liquid` gains only an optional setting and is
inert when unset.

**Shared data** — `backup-2026-09-24/products-before.json` holds every field of
all eight products as at 24 September 2026, including the full description HTML.
The staged script is reversible by swapping `old` and `new`.

**If a purchase regression appears:** stop the rollout, restore the theme files
above, and re-run `qa-product-pages.py --live`. Do not republish a different
theme — `ap-neotech-home-03` drops every custom section, and `one-speaker`
returns the storefront to its demo content.

---

## 8. Not done

The brief is larger than this release. Priority 1 (purchase-path defects and
contradictory information) is complete; priority 2 is partly complete —
requirements, delivery, licence and refunds are now printed on every page, and
the closing panel restates the offer. The following are **not built**, and no
part of the page pretends they are:

- **Per-product output previews** (§5.2, §6): a rendered audit report, a
  migration readiness scorecard, a client-delivery pack, a reviewed Shopify
  batch. Each needs a genuine artefact from the product's own source and a
  provenance record. The written walkthrough already on each page is what the
  page shows today.
- **First-use walkthroughs** (§5.3) beyond the existing `sbs-demo` sections.
- **Decision-support and comparison sections** (§5.5, §5.6) as designed
  components; the ecosystem row and `/collections/all` remain as they are.
- **Per-product headline rewrites** (§6 A–H) and the bundle's customer-facing
  rename to *"Build, Rank & Convert Bundle"* — a title change touches cart,
  confirmation and delivery wording and is the owner's decision.
- **Homepage job-router, collection rework, resource-page mapping** (§8).
- **Bundle purchase arithmetic recalculated from live prices in the page**
  (§6.H): `sbs-bundle-value` already renders a comparison; it was not re-derived
  in this release. Verified separately today: three products individually
  $59.97, bundle $39.99, saving $19.98 — the existing copy is accurate.

---

## 9. Owner actions

1. ~~Authorise the production push.~~ **Done — released 24 September 2026.**
2. ~~Apply the two staged description edits.~~ **Done — applied 24 September 2026.**
3. **Create the custom pixel** in Settings → Customer events, or accept that no
   product-page engagement is measured. Nothing in this release depends on it.
4. **Place a test order** through an authorised route so the half of the
   purchase journey below `/cart/add` — checkout, order lines, confirmation
   email, download delivery — is verified. It is currently unverified.
5. ~~Decide on the policy sentence in `/policies/refund-policy` that still names
   only the Launch System.~~ **Done — the policy was rewritten as final sale
   across all eight products on 24 September 2026; see §10.**

---

## 10. Refund policy — final sale, then absolute, then unconditional (24 September 2026)

Owner instruction, after confirming the facts: **one order has ever been placed
(#1001, 28 August 2026, $99.00, the Launch System) and no refund has ever been
issued.** So this changed what is promised, not what has happened.

`docs/product-pages/staged-refund-policy.py` holds the new text and applied it.
Every shop policy was exported to `backup-2026-09-24/shop-policies-before.json`
first, so the previous wording is recoverable in full.

**What it now says.** All sales are final, across all eight products, named
individually. Not refundable: a change of mind; having read, downloaded or used
it; buying the wrong product or one already owned; wanting the bundle later, or
the reverse; the product not producing a hoped-for result; not having the
prerequisites the product page names before the price.

**Two exceptions were kept in the first pass, and the owner was told so. Both
were then removed on their explicit instruction — see "No carve-outs" below.**

1. **Failure to supply.** If the download link fails, the file is corrupt, the
   wrong product arrives, or the card is charged twice or in error, the store
   fixes it and refunds only if it cannot. That is not a return; it is the
   obligation to deliver what was paid for. It matters concretely here:
   **delivery has been proven end to end for exactly one product** — the Launch
   System, by order #1001 — and the other seven have archives attached but no
   completed test purchase, with the Admin API unable to read the delivery app's
   attachments to confirm them. A customer who pays for an untested download and
   is told in advance there is no remedy raises a chargeback, which costs more
   than the refund and puts the payment account at risk. Item 4 in §9 — place a
   test order for each product — is the thing that would let this carve-out be
   narrowed safely.
2. **Statutory rights.** A blanket no-refunds term is unenforceable against
   consumer law in the UK, the EU, Australia and several US states, and in some
   of those, stating it without qualification is itself a prohibited practice.
   The paragraph concedes nothing that was collectable anyway.

### No carve-outs

Both were removed the same day on the owner's instruction, after the trade-offs
had been put to them twice. The policy now reads: all sales are final, we do not
offer refunds, across all eight products, with no exception of any kind.

- The promise to refund where the store could not deliver is gone. On a further
  instruction the same day, so is the promise to supply a **replacement file**.
  The policy now commits to no outcome when a download fails: it states final
  sale, no refunds, and carries the contact address without saying what will
  happen. **Delivery is still proven end to end for one product only** — the
  Launch System, by order #1001 — so a customer of the other seven who cannot
  open their file has no stated remedy at all. Placing a test order per product
  is what would retire that exposure.
- The statutory-rights paragraph is gone. The policy is **silent** on the
  subject; it does not assert that such rights do not exist, because in the UK,
  the EU, Australia and several US states they do, regardless of what the page
  says. Writing that they did not would have been false, and was not done.

**Consistency was re-established in both directions.** The final-sale rewrite
contradicted copy written earlier the same day — the bundle description and the
closing panel on all eight pages had been corrected *towards* a more generous
refund line hours before. All three were realigned:

| Where | Change |
| --- | --- |
| `sections/sbs-final-buy.liquid` | the refund summary on all eight pages: final sale, no refunds, replacement file for a broken download |
| `templates/product.complete-stack.json` | the bundle's refund FAQ answer rewritten to match |
| Complete Site Builder Stack description | realigned via `staged-description-changes.py` |

Each of those was edited **three times** in one day, because the policy moved
three times: generous → final sale → absolute → unconditional. A fourth leftover
surfaced only on the last pass — the Launch System's own FAQ still described the
statutory-rights clause — which is the argument for the consistency check being
a rule about agreement rather than a search for a fixed phrase. Superseded entries were removed from the changeset script rather than
left to report "skipped" on every future run; this record is where the sequence
lives.

The QA suite was corrected too. It asserted `no "sales are final"`, which was
the right rule that morning and the wrong one that afternoon. It now checks
what actually matters — that each page states final sale, links the policy, and
does not offer a refund the policy excludes — and that check is what proves all
eight pages and the policy agree.
