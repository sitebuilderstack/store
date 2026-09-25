# Engagement implementation — task checklist

Branch `feature/engagement` from master `0c91637` (tag `engagement-baseline`). Status words: implemented · tested locally · tested in preview · published · scheduled · draft · blocked.

## Discovery
- [x] Repository, theme workflow, publish scripts, analytics (`Shopify.analytics.publish` + Plausible pageviews), email integration (Shopify customer form in `sbs-optin.liquid`) inspected
- [x] Baseline screenshots (`docs/engagement/baseline/`) and performance reading (technical-seo-audit guide: LCP 712 ms, CLS 0, 176 requests, 1.1 MB)
- [x] Search Console / analytics aggregates: **unavailable to this session** (no authorised API access configured) — recorded, not invented
- [x] Baseline suite: 43/43 passing on master `0c91637` (run 2026-09-16)

## Foundation
- [x] Shared config: `content/content-graph.json` gains `modules`, `labs`, `challenges`; `validate-graph.py` checks cross-references
- [x] `sbs-projects.js` — versioned browser storage (`sbs-projects` v1), migration from `sbs-learning`, export/import/markdown
- [x] Analytics allowlist in `sbs.js` (`engagement_module_started` … `related_product_clicked`), deduplication, payload = ids/categories only
- [x] Lazy loading: `sbs.js` loads `sbs-engage.js` / `sbs-labs.js` / `sbs-projects.js` only on pages that need them

## Feature 1 — Try This on Your Project
- [x] Snippet `sbs-try.liquid` + placeholder replacement in `sbs-article.liquid`; no-JS fallback
- [x] Seven generators in `sbs-engage.js` (claude-md section, SEO audit prompt, Shopify next workflow, landing validation, maintenance checklist, migration verification, regression plan)
- [x] Placed in 6 existing guides + 3 new articles
- [x] Copy / download / save / next step; inputs preserved on validation error

## Feature 2 — Labs
- [x] Hub `/pages/labs`; `page.lab.json` + `sbs-lab.liquid` + `sbs-labs.js`; fixtures inlined per lab
- [x] A Launch Readiness · B Technical SEO · C Conversion Functionality · D Website Operations
- [x] Public sample artifacts uploaded; walkthrough (recording or screenshot walkthrough) of one lab
- [x] Deliberate-wrong-answer test

## Feature 3 — My Projects
- [x] `/pages/my-projects` + `sbs-projects.liquid`; create/rename/select/export/import/delete; tasks; continue action
- [x] Migration test; corrupt/quota/blocked storage handling; in-memory fallback

## Feature 4 — Weekly Website Fix
- [x] Blog `weekly-fix` (archive + Atom feed); `article.challenge.json` + `sbs-challenge.liquid`; hub `/pages/weekly-fix`
- [x] Four challenges written; #1 published; #2–#4 scheduled or drafts; runbook; reminders via the existing Shopify customer form (tag `weekly-fix`) or omitted

## Articles
- [x] Inventory + cannibalisation check; research file with sources and dates
- [x] 1 `claude-code-website-maintenance` · 2 `website-migration-seo-checklist-claude-code` · 3 `claude-code-playwright-website-testing`
- [x] Tested examples: maintenance fixture; redirect validator vs local fixtures; Playwright suite run with a deliberate failure
- [x] Downloads uploaded; CMS records; inbound links; hubs/tracks; schema checked

## Testing, release, docs
- [x] Logic tests (generators, storage, import validation, lab scoring, challenge state); browser journey test; storage-disabled; malformed import
- [x] Widths 390/820/1280; console/network; a11y; navigation/product/cart regression
- [x] Dev theme → preview → live; rollback steps; docs; completion report

## Status (17 September 2026, end of cycle)

Everything above: implemented, tested locally, tested in preview, and **published** (theme pushed to live `191797854500`; pages, guides, challenge #1 live; challenges #2–#4 **scheduled**). See `COMPLETION-REPORT-2026-09-17.md`.
