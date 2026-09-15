# Cornerstone guides — publication and search-readiness

Published 27 August 2026. Shareable report:
https://claude.ai/code/artifact/bf074877-05fb-4f43-ac03-c7020dfca643

## Blocker (unchanged)

Digital delivery is still not configured while the store is live and selling.
Installed apps are Messaging and site-builder-stack-app only; no file is
attached to the product or its variant. `requiresShipping` is correctly false
and the price is $19.99 (was $99 at the time). Zero orders so far, so nobody has been affected.

App installation is admin-only. Install Shopify's Digital Downloads app (or an
equivalent), attach `dist/claude-code-website-launch-system-v1.0.zip`, then
place a real test order end to end and refund it.

## What went live

Blog `guides` ("Claude Code Guides"), five articles, 26,095 words.

| # | Handle | Words | Title | Desc |
|---|--------|-------|-------|------|
| 1 | how-to-build-a-website-with-claude-code | 5,395 | 60 | 156 |
| 2 | best-claude-code-prompts-for-web-development | 4,964 | 65 | 155 |
| 3 | production-claude-md-web-development | 4,822 | 61 | 154 |
| 4 | build-shopify-store-with-claude-code | 5,680 | 66 | 157 |
| 5 | claude-code-seo-website-optimization | 5,234 | 67 | 155 |

Each has a featured image, one original diagram, three product CTAs, and links
to the other four. Tag taxonomy is closed at eight terms and enforced by
`scripts/publish-articles.py`, which refuses a tag outside it.

Rendered title length includes the theme's ` – Site Builder Stack` suffix. The
authored SEO titles are 39–46 characters; the distinctive part is front-loaded
so the suffix is what truncates.

## Verification

All measured against the live response, not the template source.

- `scripts/validate-articles.py` — 0 failures (anchors, cross-links, heading
  order, CTA count, figure attributes, word-count targets)
- `scripts/audit-articles-live.py` — 0 failures across all five
- `scripts/validate-sitemap.py` — 0 failures; 14 URLs, all 200, self-canonical,
  indexable
- `scripts/audit-live-links.py` — 17 pages, 33 URLs, 0 broken, 0 multi-hop
- `scripts/audit-rendered-a11y.js` — clean at 320/390/768/1440
- `tests/run-all.sh` — 9/9

Not measured, and marked as such rather than passed: Core Web Vitals field data
(needs traffic) and actual indexing status (needs Search Console).

## Agent discovery

`templates/agents.md.liquid` backs `/agents.md`, `/llms.txt` and
`/llms-full.txt`. All three return 200 `text/markdown`, 4,635 bytes.

It renders in a **restricted Liquid context** — only `request` and `agents`
resolve. No `blogs`, `pages`, `settings` or `product` object exists, and
referencing one renders empty with no error. The five guide URLs are therefore
literal strings. **Renaming an article handle requires editing this file by
hand; nothing will warn you.**

## Not done, deliberately

No submission to Google Search Console, Bing Webmaster Tools, or IndexNow —
outward-facing actions on accounts we hold no authorisation for.

The development theme was not published wholesale. Live carried
`home_seo_title` and `home_seo_description` that dev did not, so publishing
would have silently wiped the homepage title and description (defect D-06,
reintroduced). Individual files were pushed instead. The two themes now differ
in nothing.

## Defects found and fixed

- **og:title emitted `&amp;ndash;`** on every non-home page. The captured title
  held the `&ndash;` entity; `escape` then escaped its ampersand. Now a literal
  en dash, with a comment saying why it must stay one.
- **WCAG 2.2 SC 2.5.8** — breadcrumb links and links that are the whole content
  of a list item are standalone targets, not inline-in-text, and were 20–22px.
  Fixed with `inline-block` + padding scoped by `li > a:only-child` so links
  inside sentences are untouched.
- **Blog index had no meta description.** Set via the blog's
  `global.description_tag` metafield.
- **Four checkers were wrong.** `audit-live-links.py` reported the article that
  documents `href="#"` placeholders as having one; `audit-articles-live.py` did
  the same with Liquid error text; `audit-theme-links.py` crashed on the
  `/* */` banner Shopify writes into generated JSON; `run-all.sh` asserted a
  stale JSON-LD block count. All four fixed and control-tested against a
  deliberately broken input.
