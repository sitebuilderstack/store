---
title: "Moving a website without losing what matters"
subtitle: "A migration is a mapping and validation exercise, not a copy. Every URL, redirect, title, image, form and tag has a 'before' and must have an accounted-for 'after'."
canonical: https://sitebuilderstack.com/products/claude-code-website-migration-replatforming-system
tags: seo, web-development, wordpress, shopify, devops
---

The new site builds, deploys, looks right — and three weeks later the search traffic is half what it was, a partner's link lands on a 404, the contact form has been posting to nothing, the images break when the old hosting is cancelled, and nobody can say which of the 1,400 old URLs were supposed to go where. The deployment succeeded. The migration failed. Most of what was lost was not on anyone's list, because nobody made the list.

This is the method behind the [Website Migration & Replatforming System](https://sitebuilderstack.com/products/claude-code-website-migration-replatforming-system) on Site Builder Stack. The phases apply whether you move by hand or with its scripts.

```text
DISCOVER → INVENTORY → BASELINE → MAP → BUILD → MIGRATE → VALIDATE → CUT OVER → MONITOR → ROLL BACK IF NECESSARY
```

## Inventory: the list nobody makes

The baseline is every URL the source serves, with its status, final URL after redirects, title, description, canonical, robots directive, H1, indexability, word count, links in and out, images, forms and structured-data types. One crawl is not enough: a crawl finds linked pages; it does not find the pages that rank without links. Merge the sitemap, the Search Console page export, the analytics pages report and, if you have them, server logs — then re-crawl with that list so every known URL has a real status row.

Reconcile the three numbers — crawl, sitemap, CMS — and explain every gap: pagination, tag and author archives, attachment pages, feeds, parameter URLs. Each explained group gets one mapping decision rather than four hundred.

## Baseline: what "preserved" is measured against

Freeze the SEO state before anything moves — titles, descriptions, canonicals, robots, H1s, schema types, indexability, per URL — and take the exports only a person can: Search Console performance (3 and 12 months) and coverage, rankings, backlinks, the existing redirect list. Store them somewhere the old host's shutdown cannot delete. After launch, the only way to say "metadata preserved on 98% of pages" is to have this file from before.

Record the tracking too: which analytics loaders and IDs are on which pages, and the numbers. After launch, a drop has to be told apart from a tracking gap, and that needs the before.

## Map: the contract

One row per source URL, one decision per row: KEEP (same path), MOVE (new path, redirect), MERGE (into another page, redirect), REMOVE (retired — a 301 to the closest relevant page, or a 410). The map is not finished while any row says REVIEW. Rules handle the long tail (`/blog/(.*)` → `/posts/\1`); the head — the top pages by traffic and links — is decided by hand.

The rule that holds up: a page with external links or search impressions gets a specific target; a page with neither may be retired to its section; **nothing goes to the homepage unless it was the homepage.** A hundred old URLs redirecting to `/` is a soft-404 pattern search engines treat as "gone" and visitors treat as broken.

## Redirects: generated, validated, tested where they will live

Generate the redirect configuration from the map for the platform — nginx, Apache, Netlify `_redirects`, Vercel, Shopify's exact-match list, Cloudflare — and validate before emitting: no loops, no chains inside the map, no duplicate sources, no homepage dump, no targets on the old host. Collapse the source's existing redirects into it rather than dropping them; an old campaign URL that redirected for three years still gets hits.

Where they live is the question people get wrong. Same domain, new platform: on the new host, deployed with the site. **Domain change: on the *old* domain**, which must keep serving 301s to the new one for at least a year — cheapest at the edge, never left to lapse. Then test every rule on the real origin: valid, chain, wrong code (a framework's default 302), wrong destination, missing, loop, dead.

## Validate on staging — and know what staging cannot prove

Crawl the staging build seeded with every mapped destination, so a missing page shows up as a row, not as silence. Compare with the source through the map: URL coverage, metadata page by page (a moved page whose canonical followed it is a match; a canonical pointing at staging is a review item), structured data (Article → BlogPosting is a change, not a loss), internal links (broken, old domain, staging host, through a redirect), media (broken, on the old host, missing alt), tracking on every page once.

Two staging-specific expectations: staging *should* be noindexed — and production must not be, which is the number one launch failure — and canonicals on staging must point at the production domain, never at staging, which is number two.

Staging cannot prove redirects on the production host, DNS, TLS on the real name, or third parties pointed at the real URL. List those for cutover instead of assuming them.

## Cut over with the record in front of you

Record the whole DNS zone before the panel is opened — the MX, SPF, DKIM, DMARC and verification records live beside the A record and vanish in the same click. Lower TTLs 48 hours ahead. Change only the web records in the plan, one at a time, read back. Minutes after: critical pages on the production domain, robots and canonicals, redirects on the real origin, tracking in the real-time view, TLS on apex and www, from a second network. A migration is never permission to touch mail.

## Rollback is a procedure, not a hope

Readiness is checked as facts before launch: the source still answers; a backup exists *and someone has restored from it*; the DNS record has MX rows; an owner and a decision window are named; the TTL was lowered. The rollback restores the recorded records one at a time and verifies the source pages. Never destroy the source before the target is validated — it is the rollback and, usually, the media host. Cancel the old hosting at thirty days, not on launch day.

## Score it

Six percentages — URL coverage, redirect integrity, metadata preservation, canonical integrity, internal links, media integrity — plus analytics, forms and critical pages as pass/fail. Any blocker (a critical page down, redirect gaps, production noindexed, canonicals to staging, no verified backup) is NO-GO regardless of the number. Anything not measured is *not checked*, not scored. The score orders the work; it is not a prediction of rankings.

Then the three windows: 24 hours (propagation, first crawls, the 404 log), 7 days (Search Console catches up; the long tail appears), 30 days (rankings settle; decommission decision). Most "SEO disasters" in the first week are a missing tag or a 302.

The full system — twenty modules, seven platform guides, 37 commands, 28 standard-library scripts and a complete fictional migration — is on [Site Builder Stack](https://sitebuilderstack.com/products/claude-code-website-migration-replatforming-system). The platform specifics start with [Claude Code for WordPress](https://sitebuilderstack.com/blogs/guides/claude-code-wordpress) and [Claude Code for Astro](https://sitebuilderstack.com/blogs/guides/claude-code-astro).

---

*Adapted from the Website Migration & Replatforming System on Site Builder Stack. Independent; not affiliated with Anthropic.*
