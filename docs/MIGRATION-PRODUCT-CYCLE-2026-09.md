# Sixth product implementation — September 2026

Claude Code Website Migration & Replatforming System, $29.99. Branch
`feature/migration-system`, commit `1610683` on master `8aa6b27`.

---

## PRODUCT

```text
Name:            Claude Code Website Migration & Replatforming System
Price:           $29.99
Product Handle:  claude-code-website-migration-replatforming-system
Product URL:     https://sitebuilderstack.com/products/claude-code-website-migration-replatforming-system
SKU:             SBS-CCWMRS-V1
Template:        product.migration-system (layout: landing)
Published:       Online Store (gid://shopify/Publication/294258901284)
```

## DELIVERABLE

```text
ZIP filename:         claude-code-website-migration-replatforming-system-v1.0.zip
ZIP size:             307058 bytes
SHA-256:              11a313c41a5686d9c00b74b879d0f2fff5d860436cc4ada004f746555ab77bce
Total files:          190 (190 archive entries, single top-level directory)
Modules:              20 (19 phase modules + 20-platform-guides with 7 guides; 33 module documents)
Claude Code commands: 37 (26 READ ONLY, 9 MODIFIES FILES, 2 PRODUCTION IMPACT POSSIBLE)
Scripts:              28 Python (+ _common.py, _inv.py), standard library only
Templates:            17 (migration-config.yaml, 9 CSV/MD templates, CLAUDE.md, 6 redirect samples)
Reports:              6 templates (plan, pre-migration audit, launch readiness, post-migration, executive summary, master audit shape)
Checklists:           13
Example:              examples/wordpress-to-astro/ — 33 files, real script output against a fixture site
Words:                78,700
```

Every count is generated into `PRODUCT-MANIFEST.md` at build time and
asserted by the publisher before the listing can be created.

## PRODUCT VALIDATION

| Check | Result | How |
| --- | --- | --- |
| Files, structure, safety rules, modes | PASS | `scripts/validate-migration-system.py` — 0 failures; self-test 38/38 faults detected |
| Crawler vs controlled content | PASS | `scripts/test-migration-system.py`: two local fixture sites; inventory columns, sitemap seeding, --list, indexability, canonical-to-old-host all asserted |
| URL comparison | PASS | UNCHANGED / REDIRECTED / REMOVED / MISSING asserted; redirecting target rows no longer count as pages |
| Redirect tester | PASS | valid → PASS, missing → MISSING, loop → LOOP, chain → CHAIN, 404 target → DEAD, 302 → WRONG-CODE; generator refuses loops and homepage dumps |
| Metadata comparison | PASS | lost description → MISSING; canonical to old host → REVIEW; moved page's self-canonical → MATCH |
| Sitemap validation | PASS | staging URL in sitemap → CRITICAL; clean sitemap passes |
| Robots validation | PASS | production robots allows; the same file with --staging fails |
| Canonical validation | PASS | canonical to old host → CRITICAL |
| Old-domain scan | PASS | old host and staging host found in the repo and rendered pages; node_modules skipped |
| ZIP validation | PASS | make-archive → verify-archive round-trip, 190 entries, no artefacts, no credential patterns |
| Live smoke (read-only) | PASS | crawl, robots, sitemap, canonicals, tracking, link audit, DNS, performance capture against sitebuilderstack.com |
| Harness total | PASS | 104 assertions, 0 failures; every script answers --help |

Bugs found and fixed by the harness before shipping: `host_of()` dropped
non-default ports (a staging site on :8080 would have been treated as the
production host); `load_config()` referenced a name before assignment;
`html_to_markdown.py` wrote a directory input with one file to a single
file; `compare_metadata.py` marked a moved page's self-canonical as REVIEW;
`schema_compare.py` reported Article → BlogPosting as a loss; `url_map.py`
and the comparisons treated a redirecting target URL as an existing page;
`generate_redirects.py` collapsed a query-string source to `/` (a 410 on the
homepage) and lacked the explicit loop and homepage-dump checks its docs
promised; the url-map path turned REMOVE-with-target into 410 instead of 301.

## WEBSITE CHANGES

| Area | Change |
| --- | --- |
| Product page | `content/products/migration-system.html` (2,044 words), `theme/dev/templates/product.migration-system.json` — 20 module tiles, 10-step walkthrough, 10 FAQs with schema, 6 ecosystem cards, Operations cross-sell |
| Header | `sbs-header.liquid` seventh product slot; menu: migration sixth, bundle seventh |
| Footer | Products column: migration inserted at 6, "Compare all six", links shifted to slot 12 |
| Homepage | ecosystem row: six cards ("Six products, six different problems"); `sbs-ecosystem` 3+3 |
| Product pages | migration card added to every other product's ecosystem row ("The other five") |
| Lifecycle page | `sbs-lifecycle` max_blocks 7; "Migrate" stage between Operate and Automate Shopify, bundle last; page copy adds the Migrate paragraph |
| Picker | `migrate` key in Liquid handles, `sbs.js` PICK_KEYS/PICK_WHY/totals, new options on Q1/Q2/Q5; tests updated (7 products, 7 stages) |
| Collection | intro copy: six products |
| Case study | catalogue paragraph: six products, $29.99 |
| agents.md | product entry with counts asserted by `audit-agents-claims.py` |
| Guides | migration CTAs in WordPress, Astro, Shopify build, GitHub Actions/Cloudflare (DNS), technical SEO audit, Search Console; WordPress guide's section CTA now points at the migration system |
| Pillars | WordPress, Astro, Shopify pillars link the product |
| Content graph | `migration-system` product entry; graph and article metafields republished |
| Delivery | `upload-files.py` refuses the migration slug on the public CDN |
| Tests | `tests/run-all.sh`: four migration checks (validator, self-test, harness, listing) and the product URL in the render loop — 39 checks passing |

## PRODUCT PAGE

```text
Headline:            Move Your Website Without Losing What Matters.      PASS
Subheadline:         present (sbs-lede)                                  PASS
CTA:                 "Get the Migration System — $29.99" (rendered)      PASS
SEO title:           Claude Code Website Migration & Replatforming System | SiteBuilderStack   PASS (72 chars; the title guard does not double the brand)
Meta description:    Plan, execute, and validate website migrations with Claude Code. Preserve URLs, redirects, SEO, metadata, content, analytics, and critical functionality.   PASS
Product schema:      one Product block, Offer 29.99 USD, InStock; BreadcrumbList; FAQPage   PASS (no duplicates)
Image:               assets/product-migration-system.png 1600×1200, "MIGRATE · Discover • Map • Move • Validate", attached with alt   PASS
Price literals:      $19.99, $29.99, $39.99 only (comparison table); no $29 / $29.00 / $29.95 / $39 / $49 / $59 / $69   PASS
Accessibility:       clean at 375 and 1440 (rendered a11y audit); no horizontal overflow   PASS
Performance:         LCP good, CLS good (audit-performance.js)   PASS
```

## INTEGRATION

```text
Homepage:            six-card product row, MIGRATE sixth              PASS
Header / footer:     7 product links; mobile menu 7 of 7, no overflow  PASS (test-nav-menu, test-mobile-menu)
Lifecycle + picker:  7 stages, 7 fallback products, migrate path wins  PASS (test-picker-logic 0 failures; test-picker 0 failures)
Storefront claims:   0 failed claims (audit-storefront-claims)         PASS
agents.md claims:    0 failures (audit-agents-claims)                  PASS
Articles / graph:    validate-articles 0/0; validate-graph 0; internal-linking 0 findings   PASS
Live audits:         audit-seo-site no findings; validate-sitemap 0 failures; audit-indexation 0 findings; audit-live-links 0; validate-pixel 0 findings   PASS
Offline suite:       tests/run-all.sh 39 passed, 0 failed              PASS
Other prices:        Launch 19.99, SEO 19.99, CRO 19.99, Stack 39.99, Ops 39.99, Shopify 39.99 — unchanged   PASS
Digital delivery:    NOT PROVABLE via the Admin API (six of seven products); the migration archive is NOT yet attached   see MANUAL ACTIONS
```

## MANUAL ACTIONS

1. **Attach the archive** in the Digital Products app to the new product:
   `dist/claude-code-website-migration-replatforming-system-v1.0.zip`
   (SHA-256 `11a313c4…b77bce`). Until then the product is live and buyable
   with nothing to download.
2. Place a real test order for the product (refund afterwards), open the
   download link, and check the file's SHA-256 against the value above.
3. The lifecycle page, case study and pillar pages were republished during
   the cycle (`publish-pages.py` publishes every page when run; the copy was
   already final). Nothing further to do.
4. Merge `feature/migration-system` to master, delete the branch and push
   the mirror when you say so — not done here, per the usual pattern.

## Git

```text
git status:      clean on feature/migration-system (dist/ ignored)
git diff --stat: 239 files changed, 12,183 insertions(+), 124 deletions(-)  (master..feature/migration-system)
```
