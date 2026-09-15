# Seventh product implementation — September 2026

Claude Code Agency & Client Delivery System, $39.99. Branch `feature/agency-system` on master `3c6693e`.

## PRODUCT

```text
Name:            Claude Code Agency & Client Delivery System
Price:           $39.99
Product Handle:  claude-code-agency-client-delivery-system
Product URL:     https://sitebuilderstack.com/products/claude-code-agency-client-delivery-system
SKU:             SBS-CCACDS-V1
Template:        product.agency-system (layout: landing)
Published:       Online Store (gid://shopify/Publication/294258901284); image attached
```

## DOWNLOAD

```text
ZIP filename:         claude-code-agency-client-delivery-system-v1.0.zip
ZIP size:             240486 bytes
SHA-256:              8fe8d23f5607bfd6d8be154ed075ab9126ef30b75fa00d6c13cfa256fe39c1b5
Total files:          201 (201 archive entries, single top-level directory)
Modules:              21 (one README each: audience, goal, procedure, common mistakes)
Claude Code commands: 37 (11 INTERNAL USE, 14 CLIENT-FACING, 12 internal → client after review)
Templates:            29 + the client-project skeleton (16 files)
Checklists:           17 (14 phase checklists + definition of done, launch, access transfer)
Reports:              12 shapes
Worksheets:           3
Scripts:              4 (new_client, project_status, estimate, validate_client), standard library only
Example projects:     1 — Harbourline Physio (fictional), 38 files
Words:                56,977
```

## WEBSITE

```text
Product page:         PASS — headline, lede, problem, solution, included, commands, use cases, who, safety, compare, delivery, not promised
Price:                PASS — $39.99 on the product, the page, the header menu; literals on the page: $19.99 / $29.99 / $39.99 only
CTA:                  PASS — "Get the Agency & Client Delivery System — $39.99" (rendered)
SEO metadata:         PASS — title "Claude Code Agency & Client Delivery System | SiteBuilderStack"; description exactly as specified; canonical correct
Structured data:      PASS — one Product block, Offer 39.99 USD InStock; BreadcrumbList; FAQPage (no duplicates)
Catalog integration:  PASS — homepage seven-card row (4-column grid for 7/8 cards), header 8th slot, footer, collection intro, "Deliver" lifecycle stage + picker key, ecosystem card on every product page
Cross-sells:          PASS — product page table to all six technical products with the engagement each enables; Operations cross-sell CTA
Internal links:       PASS — CTAs in the build-a-website, website-audit, CRO workflow and Shopify SEO guides; web-development and production pillars; website-audit guide's section CTA points at it
Digital delivery:     NOT TESTABLE — archive built; attachment in the Digital Products app is a manual step; delivery provable only by a fulfilled order
Mobile layout:        PASS — a11y/overflow clean at 375 and 1440 on the product page, homepage and lifecycle page
Existing products:    PASS — six other prices unchanged; nav/mobile/picker browser tests 0 failures
```

## PRODUCT VALIDATION

```text
README:                    PASS — what, who, problems, quick start, lifecycle, structure, commands, templates/reports/checklists, workflows, safety, customisation
START-HERE:                PASS — ten minutes to a client project and /client-discovery
Command links:             PASS — every template/checklist/worksheet/reference/script reference in every command resolves (validator)
Templates:                 PASS — 29 render; CSVs parse with declared columns; YAML parses; JSON parses
CSV/YAML/JSON validation:  PASS — validator + validate_client.py
Example project:           PASS — one client, one project, consistent across 38 files; status and estimate outputs reproduced by the scripts
ZIP:                       PASS — make-archive → verify-archive round-trip; 201 entries; no artefacts; no credential patterns
No secrets:                PASS — credential patterns, plaintext credential fields, private hosts: none (validator; 43-case self-test)
No real client data:       PASS — the only client is fictional; hosts are .example; the validator refuses any other host in examples/
Scripts:                   PASS — 23-assertion offline harness (creation refuses overwrite; status from files; estimate range; validation of .env/credential/placeholder)
```

## PRICE

```text
CUSTOMER PRICE: $39.99 USD
```

## MANUAL ACTIONS

1. Attach `dist/claude-code-agency-client-delivery-system-v1.0.zip` (SHA above) to the product in the Digital Products app — the product is live and buyable with nothing to download until then. The migration archive is still unattached too (see `docs/REMAINING-MANUAL-STEPS.md`).
2. Place a test order, verify the download's SHA-256, refund.
3. Merge `feature/agency-system` to master, delete the branch and push the mirror on your word.
