# Fourth product implementation — September 2026

Claude Code Website Operations & Maintenance System, $39.99. Branch
`feature/operations-product`, commit `f1d06af` on top of master `1af7940`.

---

## PRODUCT

**What was built.** A complete operating system for the stage after launch,
built as a real downloadable product: 106 files, 63,278 words, and — for the
first time in this catalogue — working code.

| | Count | Verified by |
| --- | --- | --- |
| Modules | 17 (`01-getting-started` … `17-platforms`) | `validate-ops-system.py` |
| Module documents | 40, each with a mode line, `## Goal`, `## Common mistakes`, ≥ 400 words | validator |
| Slash commands | 19 in `commands/`, each Purpose / Preconditions / Inputs / Steps / Safety rules / Output format / Validation; index `COMMANDS.md` | validator (names, sections, index count) |
| Scripts | 11 in `scripts/` (+ `_common.py`): `check_http`, `check_ssl`, `check_dns`, `check_headers`, `crawl_links`, `audit_redirects`, `validate_sitemap`, `test_endpoints`, `compare_baseline`, `generate_report`, `read_config` | `--help` in the validator; `test-ops-scripts.py` offline; live control runs |
| Checklists | 9 | validator |
| Report templates | 8 in `15-reporting/` | validator |
| Platform guides | 4 (Shopify, WordPress, Astro/static, Node.js) | validator |
| Templates | `CLAUDE.md` (all 12 site fields + 10 operating rules), `ops-config.yml`, `endpoints.txt`, `redirects.csv`, `baseline.json`, `CHANGE-LOG.md` | validator (fields) |
| Automation | `run-checks.sh`, `crontab.sample`, `github/site-health.yml`, `github/post-deploy-check.yml` | validator; YAML parsed; `run-checks.sh` executed against the live store |
| Examples | a real, unedited `generate_report.py --run` against sitebuilderstack.com (`.md` + `.json`), plus three worked examples labelled as composites | — |
| Top level | `README.md` (with the command-reference table), `START-HERE.md`, `QUICK-START.md`, `LICENSE.md` (existing terms, product name substituted), `VERSION.md`, `CHANGELOG.md`, `PRODUCT-MANIFEST.md` (generated) | validator |

**The safety system** (`01-getting-started/SAFETY-SYSTEM.md`) — DISCOVER →
ANALYZE → BACKUP → CHANGE → TEST → VALIDATE → DOCUMENT; never modify
production without authorisation; never expose secrets; always create a
rollback point — is restated in every command's safety rules and in the
`CLAUDE.md` template's operating rules. Seventeen of nineteen commands are
audit-only; `/update-plan` and the remediation inside `/incident-diagnose`
propose What / Where / Why / Rollback / Risk and wait.

**Severity levels** SEV-1 Critical / SEV-2 Major / SEV-3 Moderate / SEV-4
Minor are defined in `13-incidents/SEVERITY-LEVELS.md` with a per-level
response table. **Log analysis** uses the seven-section format (Executive
Summary … Rollback). **The master audit** produces Website / Date /
Environment / Overall Score plus per-area scores and `operations-report.json`
(`generate_report.py`); the **monthly report** opens with
`Overall Health Score: NN/100`.

**Scripts, as shipped.** Standard library only (the validator refuses any
other import), `--help` and `--json` on each, exit 0 / 1 / 2 / 3 documented
in `scripts/README.md`. Control-tested against the live store during
development; findings the scripts made about our own site are in §TEST
RESULTS. Design decisions worth knowing: `fetch()` decodes gzip and returns
case-insensitive headers (both were bugs found by the crawler returning "0
links" and the redirect probe reporting www as unfixed); `crawl_links`
deduplicates by link and rates an external 401/403/429 as WARNING rather than
FAIL (bot blocks); `check_headers` includes the exposure probes and treats a
200 that is an HTML page as a soft-404 (Shopify serves the homepage for
`/.env`); `compare_baseline` ignores timing changes under an absolute floor
(0.3 s) because single requests are noisy; `generate_report` skips a previous
merged report found in its input folder and exits 3 when no usable input is
given.

**What it deliberately does not do:** no penetration testing (no auth
attempts, payloads, fuzzing, load; the validator refuses files that recommend
sqlmap, nikto, metasploit, hydra, gobuster, ffuf and the like), no automated
changes, no scanning of sites the operator does not own, no predicted
percentage improvements, no uptime guarantee.

## DELIVERABLE

`dist/claude-code-website-operations-maintenance-system-v1.0.zip` — 222,382
bytes, 106 entries under a single top-level directory, executable bits kept
on `.py` and `.sh`.

SHA-256: `f48b88fe48b23020dc00950acf269928bd6eabf3f5a25322ba510c962413210c`

Built by `scripts/build-ops-system.sh`: validate → generate manifest (counted,
not typed) → re-validate → `make-archive.py` → `verify-archive.py` round-trip
→ a second content check inside the archive (no `__pycache__`, no dotfiles,
no credential patterns, no `myshopify.com`) → checksum. Extracted with Python
into a scratch directory and run as a customer would: `check_http.py`,
`generate_report.py --run` (score 95/100), `run-checks.sh daily`, both
GitHub workflows parsed.

`dist/` is gitignored, as for the other three products.

## WEBSITE CHANGES

Theme (pushed to dev `191811453220`, verified, then live `191797854500` in
the required order — code files, wait for schema propagation confirmed by
reading `sections/sbs-header.liquid` back, then group JSON and templates;
every pushed setting read back from the theme API):

- `templates/product.ops-system.json` — new; `layout: landing`; 18 contents
  tiles, 10 walkthrough steps, 9 FAQ entries with `emit_schema`, ecosystem row
  (the other three + bundle), CTA to the bundle.
- `sections/sbs-header.liquid` — fifth product slot (`product_5`; the schema
  had four). `sbs-header-group.json` — Operate in slot 4, bundle moved to 5.
- `sections/sbs-footer-group.json` — "Operations & Maintenance System" in
  the Products column; "Compare all four"; "Build → Rank → Convert → Operate".
- `templates/index.json` — fourth ecosystem card; copy "Four products…";
  `sections/sbs-ecosystem.liquid` chooses a 2×2 grid for four cards.
- `templates/page.build-rank-convert.json` — Operate stage before the
  bundle; heading "Build, then rank, then convert, then operate"; picker
  options for operate appended to Q1, Q2, Q5 with `operate:` scores.
  `sections/sbs-picker.liquid` + `assets/sbs.js` — `operate` key between
  `convert` and `all` so the bundle still loses ties.
- `templates/product.json`, `product.seo-toolkit.json`,
  `product.cro-toolkit.json` — Operate cross-sell card; bundle card reads
  "The first three". `product.complete-stack.json` — "And after launch?" CTA.
- `templates/collection.json` — "Four products…". `templates/agents.md.liquid`
  — product entry, bundle wording, recommendation paragraph, "four products
  and one bundle".
- `layout/theme.liquid`, `layout/landing.liquid` — title suffix suppressed
  when the title already contains the brand in either spelling (fix).
- `sections/sbs-demo.liquid` + `assets/sbs.css` — richtext note in a `<div>`
  (fix). `sections/sbs-product.liquid` — `.sbs-rte pre` overflow rules (the
  new page's code block widened a 375 px viewport to 649 px before this).

Content and pages: `content/products/ops-system.html` (description);
`content/pages/build-rank-convert.md` and the page's title / SEO title / meta
description (URL unchanged); `content/pages/case-study.md` (four products);
`content/products/seo-toolkit.html`, `cro-toolkit.html`, `complete-stack.html`
(a sentence linking to the fourth product); `content/content-graph.json`
(`products.operations`; product CTA switched to it on
`claude-code-website-security-audit`, `claude-code-github-actions`,
`claude-code-github-actions-cloudflare`, `claude-code-enterprise`) — all
published.

Scripts and tests: `validate-ops-system.py` (+ `--self-test`, 22 detections),
`build-ops-system.sh`, `publish-ops-system-product.py` (create-only price,
`--check-only` for offline tests, refuses any price but $39.99 and the three
$19.99 comparisons), `attach-product-image.py`, `test-ops-scripts.py`,
`generate-product-image.py` (`ops` entry), `upload-files.py` (slug added to
`BLOCKED`), `audit-storefront-claims.py` (ops bundle, `scripts` and
`slash commands` claims, README excluded from counted directories),
`audit-agents-claims.py` (explicit `BUNDLE_COMPONENTS`; ops counts),
`test-picker-logic.js` / `test-picker.js` (operate cases; five products),
`publish-pages.py`, `verify-digital-delivery.py` (cents rounding fix),
`tests/run-all.sh` (`run_if_bundle_ops`, four new checks, new page in the
render loop).

Docs: `README.md`, `docs/STORE-ARCHITECTURE.md`, `docs/BUNDLE-ARCHITECTURE.md`
(bundle recommendation), `docs/REMAINING-MANUAL-STEPS.md`,
`docs/analytics/EVENTS.md`, this file.

## PRODUCT PAGE

`https://sitebuilderstack.com/products/claude-code-website-operations-maintenance-system` — live, 200.

- Title tag: `Claude Code Website Maintenance & Operations System | SiteBuilderStack` (exact; the suffix bug fixed to make it so).
- Meta description: exact per specification.
- H1: product title. Description opens with the headline "Your website is live. Now keep it healthy." then subheadline, The problem, The solution, What is included (17-row module table), The commands, The scripts, Who it is for, Platforms, Before and after, The recurring workflow, What it will not do, How it fits with the other three (four-column comparison), Delivery and licence, What is not promised.
- Buy button renders "Get the Operations System — $39.99" from the live price.
- Structured data: one `Product` (sku `SBS-CCWOMS-V1`, price 39.99 USD, InStock, image), one `BreadcrumbList`, one `FAQPage`. No duplicates.
- Image: `assets/product-ops-system.png`, 1600×1200, generated from the bundle in the existing design ("OPERATE · Monitor • Diagnose • Maintain • Protect"; counts drawn from the files), attached as featured media with descriptive alt text.
- Header menu shows five products with live prices; footer links it.
- Accessibility + overflow audit clean at 320 / 375 / 768 / 1024 / 1440 on live. LCP 740 ms, CLS 0 at 412 px (`audit-performance.js`).

## INTEGRATION

- Lifecycle: OPERATE is the fourth stage on the homepage row, the lifecycle page (stage 4 of 5, before the bundle), the picker (new `operate` outcome; "live + converting problem" still returns the Conversion toolkit; the bundle still loses every tie — asserted by the unit test), the header, the footer, `agents.md`, the collection intro.
- Cross-sells: Operate card on the three product pages; "after launch" CTA on the bundle page; the ops page cross-sells the three and the bundle.
- Internal links: product CTA on four operations-relevant guides through the content graph; lifecycle page copy; case study; three product descriptions.
- Bundle: **unchanged** — price, contents, attachments. Recommendation in `docs/BUNDLE-ARCHITECTURE.md`: leave it; consider a four-product bundle only on evidence; do not fold the $39.99 product into the $39.99 bundle. Note the visible comparison: the bundle (three products) and the operations system (one product) are both $39.99 — the product page and FAQ address it.
- Analytics: existing events only (`product_nav_clicked`, `product_ecosystem_clicked`, `product_recommended`, `product_selector_cta_clicked`, buy form); `EVENTS.md` wording updated; `validate-pixel.py` 49 events, 0 findings. The pixel remains uninstalled (documented earlier).
- Delivery: digital-product settings identical to the others (no shipping, untracked, 0 g); the archive is refused by `upload-files.py` unconditionally; not attached — see below.

## TEST RESULTS

| Test | Result |
| --- | --- |
| `validate-ops-system.py` | PASS — 0 failures |
| `validate-ops-system.py --self-test` | PASS — 22/22 faults detected |
| `test-ops-scripts.py` (offline fixture: 404, chain, loop, exposed `.env`, redirecting sitemap URL, slow page, missing text, self-signed TLS) | PASS — 44 assertions |
| `build-ops-system.sh` (validate, manifest, archive, round-trip, content check) | PASS |
| Archive extracted and run as a customer | PASS — score 95/100 from the shipped copy |
| `tests/run-all.sh` (offline) | PASS — 31/31 (was 27) |
| `publish-ops-system-product.py --check-only` | PASS — counts and price match |
| `audit-storefront-claims.py` | PASS — 0 failed claims (ops tiles, counts, scripts, slash commands verified) |
| `audit-agents-claims.py` | PASS — prices `[19.99, 39.99, 59.97]` match live; ops counts verified |
| `validate-graph.py`, `validate-articles.py`, `validate-pixel.py` | PASS |
| `audit-seo-site.py` (live crawl) | PASS — no findings |
| `validate-sitemap.py` (live) | PASS — 0 failures; the product is in Shopify's generated product sitemap (not hand-edited) |
| `audit-live-links.py` | PASS — 0 issues |
| `audit-internal-linking.py`, `audit-cannibalization.py`, `audit-indexation.py` | PASS — 0 findings (102 crawled, 70 in sitemap) |
| Browser: header menu, mobile menu, picker (incl. operate path), route engine, analytics events | PASS on dev preview and on live |
| A11y + overflow: ops page (5 widths), `/`, lifecycle, collection, bundle, three product pages | PASS ("clean"); one preview-only console line from Shopify's `shop.app` frame under the preview bar, absent on live |
| Price validation | PASS — the served page contains only `$39.99` (this product) and `$19.99` (comparison); a repository sweep for `$39`, `$39.00`, `$39.95`, `$49`, `$59`, `$89` finds them only in the publisher's own forbid list and in historical cycle reports |
| Live product prices after all publishes | PASS — 19.99 / 19.99 / 19.99 / 39.99 / 39.99, unchanged for the four existing products |
| `verify-digital-delivery.py` | FAIL (expected) — delivery unproven for four products, including this one; cart-price check now PASS after the rounding fix |
| Checkout with a real order | NOT TESTABLE from here — requires the owner |
| GitHub Actions samples executing in a real repository | NOT TESTABLE from here — parsed only |
| `check_ssl.py`, `check_dns.py`, `check_http.py`, `check_headers.py`, `crawl_links.py`, `validate_sitemap.py`, `audit_redirects.py`, `test_endpoints.py`, `compare_baseline.py`, `generate_report.py`, `run-checks.sh` against sitebuilderstack.com | PASS — ran; real findings: HSTS max-age 7889238 s (< 180 days), no `Referrer-Policy` / `Permissions-Policy` / `Cache-Control` on HTML (all Shopify-set), apex and www resolve differently (www redirects, so accepted), two outbound OWASP links in the guides go through three-hop redirect chains, one help.shopify.com link returns 403 to a crawler UA. None is a defect this cycle introduced; the OWASP link targets are worth updating in a content pass. |

## REMAINING MANUAL ACTIONS

1. **Attach the archive** `dist/claude-code-website-operations-maintenance-system-v1.0.zip` to the product in the Digital Products app, then place a real test order and confirm the download. Until then the product can take money it cannot deliver — the same state the SEO toolkit, CRO toolkit and bundle are in (banner in `docs/REMAINING-MANUAL-STEPS.md`). Alternatively set it to Draft.
2. **Merge** `feature/operations-product` to master and **push the public mirror** (`bash scripts/publish-public-mirror.sh --push`); neither was done without your word.
3. **Bundle decision** — read `docs/BUNDLE-ARCHITECTURE.md` § "The fourth product". Nothing needs changing today.
4. **Price observation** — the operations system ($39.99) costs the same as the bundle of the three others ($39.99) and twice any one of them. The page explains why; if you would rather it did not invite the comparison, the number is yours to change in the admin (the publisher no longer overwrites it).
5. **Walkthrough video** — the demo section says none is published, as on the other pages.
6. Optional content fix surfaced by the product's own crawler: update the two `owasp.org` links in the security guides to their final URLs.

---

Nothing in this cycle changed an existing product's price, an existing URL,
or the bundle. No credential appears in the product, the repository, the
archive or this report; the validator, the build and the archive check each
assert that independently.
