---
title: "Building a Shopify store with Claude Code: the rules it cannot infer"
subtitle: "Two ways in, one theme that must never be pushed by accident, a token that must never reach a Liquid file, and the checkout failure no fetch can see"
canonical: https://sitebuilderstack.com/blogs/guides/build-shopify-store-with-claude-code
tags: shopify, claude, ai-tools, ecommerce, liquid
---

Shopify is a hosted platform, which changes the shape of the work. You are not building a web application; you are building a theme that runs inside someone else's rendering pipeline, plus a catalogue that lives in someone else's database. Both are reachable programmatically. Both have rules an agent will not infer from the files, and a session that does not know them produces code that looks right and does not render — or a store that looks perfect and cannot take money.

This is a condensed version of the [full Shopify guide on Site Builder Stack](https://sitebuilderstack.com/blogs/guides/build-shopify-store-with-claude-code), written from building that store.

## There are exactly two connections

| You want to change… | Use | What it is |
|---|---|---|
| Theme files — Liquid, CSS, JS, JSON | the theme files | ordinary files in a directory Claude Code can read, edit and push |
| Store data — products, pages, policies, redirects, metafields | the Admin API | a GraphQL endpoint you call with an access token |
| Payments, tax, domains, app installs | the Shopify admin, by hand | deliberately not available to either |

There is no "Shopify mode". Four things carry Shopify's name — the CLI (theme development), the Admin API (everything behind the login), the Storefront API (what a customer can see) and the older REST API — and a session told to "use the Shopify API" will pick one. Say which.

## Develop against a theme that is not live

Themes have roles. Exactly one is MAIN — the live storefront; everything else is unpublished. All development happens against an unpublished theme, and publishing is a separate, deliberate act. Enforce it mechanically: whatever push mechanism you use, make it refuse the live theme's id unless something explicit overrides it. Five lines convert "I hope nobody passes the wrong theme ID" into a thing that cannot happen by accident.

## Credentials, and the leak that is specific to Shopify

An Admin API token can read customer data and change your catalogue, and a coding agent introduces a new way to leak one: it will happily write a working script that hard-codes the token, because that is the shortest path to what you asked for. Say otherwise, explicitly.

Two consequences are Shopify-specific. **Theme files are public** — anything in assets, snippets, sections or templates is served to browsers, so a token in a Liquid file is not merely committed, it is published. And **token caching needs a home outside the repository**, because a cache file beside the code is one `git add -A` away from the same fate.

## Four things about theme architecture worth telling a session directly

- **JSON templates can choose their layout.** `"layout": "landing"` renders a template inside `layout/landing.liquid` instead of the default — how one page type gets different chrome without conditionals in the main layout.
- **Section schemas define the settings.** The `{% schema %}` block produces the theme editor's controls; hard-coded copy in a section is copy that needs a developer to change.
- **Push order matters.** Section-group JSON files reference sections by filename, and a section's `max_blocks` must be raised and pushed *before* a group that exceeds it.
- **Liquid fails softly.** A broken tag renders as empty output or visible text, not an error. "The push returned success" is not evidence that anything works — fetch the preview URL and check the response.

## Policy pages are not a template type

The gotcha that cost the most time: if you want policy pages styled differently, the obvious move is `templates/policy.json`. Shopify rejects it. The next move is `templates/policy.liquid` — which uploads successfully and is then silently ignored, because `policy` is not a template type at all. You get a successful push and an unchanged page, which reads exactly like a caching problem and is not one. The working approach is to branch inside the layout on the request path.

## The Admin API bites in unexpected places

A mutation that fails validation returns HTTP 200 and changes nothing — read `userErrors`, every time. Publishing is a separate call from creating: a product can exist and be invisible on the storefront. And "report what the API returned, not what you sent" catches partial successes, which are the awkward case.

Several things that feel like theme work are store data: navigation menus (the theme renders whatever handle it is pointed at), URL redirects (bulk-creatable, one mutation each — build them into the same script as the change that needs them), policies (managed as store data at `/policies/<handle>`, linked from checkout automatically).

## Digital products: the failure that decides whether the business works

Two things must be true. The variant must not require shipping, or checkout asks for an address for a download. And something must actually deliver the file — Shopify's core does not do digital delivery; an app attaches the file to the variant and emails a link on order completion. Everything else can be correct — product, price, checkout, payment — and the customer receives nothing. Only a real order proves it.

## QA before you take money

Every page returns 200 (crawl; report real status codes). No broken internal links. No Liquid errors rendering as text (grep bodies for `{{` and `{%`). Product page correct. Add to cart works — in a browser. **Checkout completes — a real test order.** Delivery works — receive the email, click the link, open the file. Policies present. Mobile at 320px with no horizontal overflow.

The checkout check has a specific trap: "This store can't accept payments right now" is injected by JavaScript. It is absent from the initial HTML, so every fetch-based check reports a healthy checkout for as long as the payment provider stays unactivated. Render it in a browser.

## Going live, in order

Publish the theme (keep the previous one — it is your rollback). Re-crawl the real domain. Confirm delivery with a real order before the password comes off. Remove the password. Verify apex and www resolve, HTTPS works, one redirects to the other. Validate the sitemap Shopify generates — never replace it with a hand-written one; it is correct on the day it is written and wrong thereafter.

## Structured data without lying

Product markup with values from Liquid objects, never hard-coded, so it stays true after the first price change. And never review, rating or aggregate markup without real reviews — a helpful session generating "5.0 from 127 reviews" for a store with none is an entirely plausible accident and a reliably penalised one.

The [full guide](https://sitebuilderstack.com/blogs/guides/build-shopify-store-with-claude-code) has the `CLAUDE.md`, the push guard and the QA table in full. Running the catalogue at scale afterwards — products, collections, SEO fields, metafields, redirects, bulk operations — is the [Shopify Automation & Admin API Toolkit](https://sitebuilderstack.com/products/claude-code-shopify-automation-admin-api-toolkit); the platform-specific SEO is in [Shopify SEO with Claude Code](https://sitebuilderstack.com/blogs/guides/shopify-seo-with-claude-code).

---

*Adapted from [How to build a Shopify store with Claude Code](https://sitebuilderstack.com/blogs/guides/build-shopify-store-with-claude-code) on Site Builder Stack. Independent; not affiliated with Anthropic or Shopify.*
