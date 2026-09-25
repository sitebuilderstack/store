# Fifth product implementation — September 2026

Claude Code Shopify Automation & Admin API Toolkit, $39.99. Branch
`feature/shopify-automation-toolkit`, commit `37448da` on master `22b4222`.

---

## PRODUCT

```text
Name:            Claude Code Shopify Automation & Admin API Toolkit
Price:           $39.99
Product Handle:  claude-code-shopify-automation-admin-api-toolkit
Product URL:     https://sitebuilderstack.com/products/claude-code-shopify-automation-admin-api-toolkit
SKU:             SBS-CCSHOP-V1
```

## DELIVERABLE

```text
ZIP filename:         claude-code-shopify-automation-admin-api-toolkit-v1.0.zip
ZIP size:             254,759 bytes (249 KiB)
SHA-256:              813cb8235f21ed97eca61db9664e28d078f3d7f59b8eebac4ac244d011c5675f
Total files:          167 (167 archive entries, single top-level directory)
Modules:              19 (30 module documents)
Claude Code commands: 34 (21 READ ONLY, 12 WRITES TO SHOPIFY, 1 stop-with-confirmation)
Scripts:              32 Python (+ _lib.py), standard library only
GraphQL examples:     18 documents, all with variables
Templates:            10 (product.yaml, collection.yaml, products.csv, product-seo.csv, metafields.csv, redirects.csv, alt-text.csv, CLAUDE.md, .env.example, .gitignore)
Reports:              6 templates
Checklists:           7
Examples:             10 worked workflows + a real sample audit (md + json) + cron + GitHub Actions
Words:                65,764
```

Every count is generated into `PRODUCT-MANIFEST.md` at build time and
asserted by the publisher before the listing can be created.

## SHOPIFY API

```text
Admin API:        GraphQL
API Version:      2026-07 — verified stable: the store served 2026-07 exactly for a
                  request pinned to it (X-Shopify-API-Version); 2026-10 also answers
                  (release candidate, not targeted); a version older than supported
                  is silently mapped to 2025-10, which the client now reports.
Centralised:      SHOPIFY_API_VERSION in .env; DEFAULT_API_VERSION in
                  scripts/shopify_client.py is the fallback and the only other place —
                  the validator refuses a second constant or a hard-coded version
                  in any other script.
REST Dependency:  None. The validator refuses any REST Admin API call in a script
                  or GraphQL document. REST is mentioned only in the fundamentals
                  module (as what legacy integrations used) and in the client's
                  docstring.
Validation:       scripts/validate_graphql.py executed every read document against
                  the live 2026-07 schema and introspected every mutation's name and
                  argument types, with includeDeprecated; deprecation response
                  headers were surfaced by the client. Result at ship: 18 documents,
                  0 invalid, 0 deprecated; 0 deprecation headers across every read
                  script.
```

Deprecations found and moved off (recorded in `reference/api-version-upgrade.md`):
`collectionUpdate(input:)` → `collection:`; `Collection.ruleSet` → `sources`;
`collectionAddProductsV2` → `collectionUpdate` with `sourcesToUpdate`
selections; `productUpdateMedia` → `fileUpdate`; `productByHandle` →
`productByIdentifier`; `currentBulkOperation` → `bulkOperations`;
`ShopPlan.displayName` → `publicDisplayName`; `Shop.productTypes/Vendors/Tags`
→ `QueryRoot`; `Publication.name` → `catalog.title`.

## WEBSITE CHANGES

Theme (dev `191811453220` → verified → live `191797854500`, code first,
schema propagation confirmed by reading the files back, then group JSON and
templates; every setting read back):

- `templates/product.shopify-toolkit.json` — new; `layout: landing`, 18
  tiles, 10 walkthrough steps, 10 FAQ entries with `emit_schema`,
  four-card ecosystem, CTA to the Operations System.
- `sections/sbs-header.liquid` — sixth product slot; `sbs-header-group.json`
  — Shopify toolkit in slot 5, bundle in 6.
- `sections/sbs-footer.liquid` — links 11 and 12; `sbs-footer-group.json` —
  "Shopify Automation Toolkit", "Compare all five".
- `sections/sbs-ecosystem.liquid` — `max_blocks` 6; five cards lay out 3+2.
- `templates/index.json` — fifth card; "Five products…".
- `templates/product.json`, `product.seo-toolkit.json`,
  `product.cro-toolkit.json`, `product.ops-system.json` — Automate Shopify
  card; "The other four".
- `templates/page.build-rank-convert.json` — Automate Shopify stage (5 of 6);
  picker options appended to Q2 and Q5 with a `shopify` key.
  `sections/sbs-picker.liquid`, `assets/sbs.js` — key added between
  `operate` and `all` so the bundle still loses ties.
- `templates/collection.json` — "Five products…". `templates/agents.md.liquid`
  — product entry, recommendation paragraph, "five products and one bundle".

Content and pages (published): `content/products/shopify-toolkit.html`;
`content/pages/build-rank-convert.md` (Shopify paragraph); `case-study.md`
(five products); `content/content-graph.json` (`products.shopify-toolkit`;
product CTA on `shopify-admin-api-claude-code` and
`build-shopify-store-with-claude-code`); inline CTAs in
`19-shopify-seo.html`, `28-shopify-admin-api.html`,
`31-shopify-conversion-audit.html`; a paragraph in the Shopify pillar.

Scripts and tests: `validate-shopify-toolkit.py` (+ 29-check self-test),
`build-shopify-toolkit.sh`, `publish-shopify-toolkit-product.py`
(`--check-only`, create-only price, forbids every neighbour of $39.99),
`test-shopify-toolkit.py` (mock Admin API, 96 assertions),
`generate-product-image.py` (`shopify` entry; tile text kept inside shorter
tiles), `upload-files.py` (slug blocked), `audit-storefront-claims.py`,
`audit-agents-claims.py`, `test-picker-logic.js`, `test-picker.js`,
`tests/run-all.sh` (four new checks; page in the render loop).

Docs: `README.md`, `docs/STORE-ARCHITECTURE.md`, `docs/BUNDLE-ARCHITECTURE.md`,
`docs/REMAINING-MANUAL-STEPS.md`, `docs/analytics/EVENTS.md`, this file.

## STORE INTEGRATION

```text
Product page       live at the URL above; H1, headline "Automate Shopify with Claude Code.",
                   subheadline, problem, solution, what's included (19-row table), commands,
                   use cases, who it is for, safety, the API, comparison, delivery/licence,
                   what is not promised; buy button "Get the Shopify Automation Toolkit — $39.99"
Catalog placement  header menu (5th of 6), footer Products column, homepage five-product row,
                   /collections/all, lifecycle page stage 5, picker outcome, four cross-sell cards
Internal links     two guides' section CTA, three inline guide CTAs, the Shopify pillar,
                   the lifecycle page, the case study, agents.md
Cross-sells        this page: the four other products + Operations CTA; the four product
                   pages and the homepage: an Automate Shopify card
SEO metadata       title "Claude Code Shopify Automation & Admin API Toolkit | SiteBuilderStack";
                   description exactly as specified; canonical correct; product in Shopify's
                   generated sitemap (71 URLs, 0 failures)
Structured data    one Product (39.99 USD, InStock, image, SKU), one BreadcrumbList, one FAQPage
Digital delivery   digital-product settings identical to the others; the ZIP is blocked from
                   public upload; NOT attached (manual)
Analytics          existing events only; validate-pixel 49 events, 0 findings
Bundle             unchanged; recommendation in docs/BUNDLE-ARCHITECTURE.md
```

## VALIDATION

| Item | Result |
| --- | --- |
| `validate-shopify-toolkit.py` | PASS — 0 failures |
| `validate-shopify-toolkit.py --self-test` | PASS — 29/29 faults detected |
| `test-shopify-toolkit.py` (mock Admin API) | PASS — 96 assertions |
| `validate_graphql.py` against the live 2026-07 schema | PASS — 18 documents, 0 invalid, 0 deprecated |
| Every read script live against our store, checked for deprecation headers | PASS — 0 headers |
| Write scripts on temporary draft resources (product create/update/metafields/alt text, collection create/update, redirect import, bulk mutation), then cleanup | PASS — counts back to baseline 5 / 1 / 4 |
| `build-shopify-toolkit.sh` (validate, manifest, archive, round-trip, content check) | PASS |
| Shipped ZIP extracted and run: connection check, store audit, GraphQL validation, workflow YAML | PASS |
| `tests/run-all.sh` (offline) | PASS — 35/35 |
| `publish-shopify-toolkit-product.py --check-only` | PASS |
| `audit-storefront-claims.py` | PASS — 0 failed claims |
| `audit-agents-claims.py` | PASS — prices `[19.99, 39.99, 59.97]` match live; counts verified |
| `validate-articles.py`, `validate-graph.py`, `validate-pixel.py` | PASS |
| `audit-seo-site.py`, `validate-sitemap.py`, `audit-live-links.py`, `audit-internal-linking.py`, `audit-indexation.py` (live) | PASS — 0 findings each |
| Browser: header menu (6 products), mobile menu, picker (incl. Shopify path; bundle loses ties), analytics events | PASS on dev preview and live |
| A11y + overflow: new page at 320/375/768/1024/1440; homepage, lifecycle, collection, two product pages at 375 | PASS (clean) |
| Performance (live, 412px) | PASS — LCP 732 ms, CLS 0, TTFB 39 ms |
| Price validation | PASS — served page contains only `$39.99` and `$19.99`; repository sweep finds the forbidden neighbours only in the publishers' own forbid lists and one historical Liquid comment |
| Existing products | PASS — live prices 19.99 / 19.99 / 19.99 / 39.99 / 39.99 unchanged; ops image byte-identical after the generator change; all existing tests pass |
| Cart | PASS — `verify-digital-delivery.py` cart price check passes for the first product; the new product's variant is configured identically |
| `verify-digital-delivery.py` | FAIL (expected) — delivery unproven for five products including this one |
| Checkout with a real order | NOT TESTABLE from here |
| GitHub Actions sample executing in a real repository | NOT TESTABLE from here — YAML parsed only |
| Inventory writes | NOT TESTED by design — no script ships; the guarded pattern is documented |

## PRICE

```text
CUSTOMER PRICE: $39.99 USD
```

Store variant price `39.99`; button renders "— $39.99" from the live price;
Product schema `39.99 USD`; the publisher refuses any other figure for this
product and leaves the price alone on update runs unless `--set-price`.

## MANUAL ACTIONS

1. **Attach the archive** `dist/claude-code-shopify-automation-admin-api-toolkit-v1.0.zip`
   to the product in the Digital Products app, then place a test order and
   confirm the download. Until then the product can take money it cannot
   deliver (the same state as the four other unproven products; banner in
   `docs/REMAINING-MANUAL-STEPS.md`). Or set it to Draft.
2. **Merge** `feature/shopify-automation-toolkit` to master and **push the
   public mirror** (`bash scripts/publish-public-mirror.sh --push`) — done
   only on your word, as before.
3. Bundle: nothing to do; the recommendation for a Shopify-specific bundle,
   if ever, is in `docs/BUNDLE-ARCHITECTURE.md`.
4. Walkthrough video: the demo section says none is published, as on the
   other pages.

---

No credential appears in the product, the archive, the repository or this
report. The scratch `.env` used for live testing lives outside the
repository with mode 600 and holds a token minted from the store's own
client credentials; nothing in it was copied anywhere.
