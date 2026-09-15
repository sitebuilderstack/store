---
title: "I built a Shopify store with Claude Code, then used it to sell the system I built it with"
subtitle: "Five things that were broken and looked fine, one rule that came out of it, and what sitebuilderstack.com sells now"
canonical: https://sitebuilderstack.com/pages/case-study
tags: claude, ai-tools, web-development, shopify, developer-tools
---

[Site Builder Stack](https://sitebuilderstack.com) is a small Shopify store that sells systems for building and running websites with Claude Code — and it was built with the first of those systems. This is a condensed version of the [full case study on the site](https://sitebuilderstack.com/pages/case-study), which has the evidence attached. It is a first-hand account of one build, including the parts that went wrong. There is no customer story in it, because it is about the store itself.

## What had to exist

A working business, not a demo:

- A Shopify storefront with a custom theme, not a purchased one wearing a new logo
- A digital product, priced, with delivery that actually delivers
- Legal pages that describe what the store really does
- Enough published content to be worth finding
- Structured data, a sitemap, and search-engine registration
- Payments that take money
- **A way to tell whether any of the above was true**

The last one turned out to be the hard part.

## The method

The workflow runs thirteen stages in dependency order — Research, Plan, Architect, Design, Build, Write, Optimize, Secure, Test, Deploy, Index, Monitor, Improve. The order is the point: each stage produces something the next one can be checked against.

The step worth calling out is the `CLAUDE.md`. A Shopify theme has rules an assistant cannot infer by reading the repository: `policy` is not a valid template type; the `agents.md` template runs in a restricted Liquid context where referencing `shop` renders empty with no error; a section's `max_blocks` must be raised and pushed *before* a section group that exceeds it. Every one of those cost time before it was written down. The [production CLAUDE.md guide](https://sitebuilderstack.com/blogs/guides/production-claude-md-web-development) is the long version of that lesson.

## Five things that were broken and looked fine

None of these were visible to somebody looking at the site. All were found by fetching something and measuring what came back.

**1. The primary call-to-action was invisible.** The button was there, the right size, in the right place — and its text and background computed to the same colour, because a generic link rule outranked the button rule by a single point of CSS specificity. Found by computing the contrast ratio of every text node against its composited backdrop in a rendered DOM: 1:1. Reading the stylesheet would never have found it.

**2. The homepage title was the raw `.myshopify.com` domain.** Shopify's homepage title comes from Online Store → Preferences, not the theme; when that field is empty, `page_title` falls back to the store's internal domain, and there is no Admin API mutation for it. Found by fetching the homepage and reading the `<title>` out of the response.

**3. Every call-to-action on every non-home page was dead.** The buttons linked to `#buy`, a fragment that only exists on the homepage. Found by resolving each fragment link against the page it appears on rather than assuming a `#` link is always valid.

**4. The store could not accept payments.** Shopify Payments was configured but never activated. Every fetch-based check reported a healthy checkout, because the "can't accept payments right now" notice is injected by JavaScript and absent from the initial HTML. Found by rendering the checkout in a real browser.

**5. A fulfilled order delivered nothing.** The order was placed with a phone number and no email address; the delivery app sends by email only; every status the platform reported said success. "Fulfilled" is a claim about a process, not about the customer receiving anything.

## The failure mode behind all five

Every one of these was reported as healthy by something — and it kept happening to the checks themselves:

| The check said | What was true | Why |
| --- | --- | --- |
| 0 broken links | 9 of 28 pages never fetched | 429s were counted as nothing to report |
| Checkout healthy | Store could not take payments | The notice is injected by JavaScript |
| Checkout accepts email | Never actually checked | It read `innerText`; the wording was in a `placeholder` |
| Page has a Liquid error | The page was fine | A regex matched prose *about* Liquid errors |
| Delivery working | Delivered nothing | It never looked at whether the order had an email |

Five checks, each written carefully, each passing, none capable of failing on the condition it existed to catch. The rule that came out of it, and that now applies to every check in the repository:

> **After a check passes, break the thing it checks and confirm it goes red.**

A link crawler reporting "0 broken links" without ever having found one is not evidence of anything. This costs about a minute per check, and it has caught more real problems than any other single practice in the build.

## What I would tell someone starting the same build

- **Write the platform's non-obvious rules down before you write code.** Not the architecture — an assistant can read that. The things that fail silently.
- **Fetch the page. Do not read the template.** Four of the five failures were invisible in source and obvious in the response.
- **Render it in a browser at least once.** The payment failure was invisible to every fetch-based check.
- **Make every check fail once on purpose.**
- **Separate auditing from fixing.** An assistant told to "check and fix" will fix things before anyone decides they matter, and the record of what was wrong disappears into a commit.

## What the store sells now

The methodology is published in full and free to read — 33 guides at the time of writing, and five checklists you can work through without giving anyone an email address. Start with [How to build a website with Claude Code](https://sitebuilderstack.com/blogs/guides/how-to-build-a-website-with-claude-code) and the [four-pass website audit](https://sitebuilderstack.com/blogs/guides/claude-code-website-audit) that found the five failures above.

The paid products are the same methodology as runnable files — commands, scripts, templates, checklists — one per stage of a website's life:

| Stage | Product |
| --- | --- |
| Build | [Website Launch System](https://sitebuilderstack.com/products/claude-code-website-launch-system) |
| Rank | [SEO & Website Audit Toolkit](https://sitebuilderstack.com/products/claude-code-seo-website-audit-toolkit) |
| Convert | [Conversion & Revenue Optimization Toolkit](https://sitebuilderstack.com/products/claude-code-conversion-revenue-optimization-toolkit) |
| Operate | [Website Operations & Maintenance System](https://sitebuilderstack.com/products/claude-code-website-operations-maintenance-system) |
| Automate Shopify | [Shopify Automation & Admin API Toolkit](https://sitebuilderstack.com/products/claude-code-shopify-automation-admin-api-toolkit) |
| Migrate | [Website Migration & Replatforming System](https://sitebuilderstack.com/products/claude-code-website-migration-replatforming-system) |
| Deliver (for clients) | [Agency & Client Delivery System](https://sitebuilderstack.com/products/claude-code-agency-client-delivery-system) |

[The lifecycle page](https://sitebuilderstack.com/pages/build-rank-convert) explains which one applies to the problem you have — including a short quiz that will tell you when the answer is "none yet".

What is deliberately *not* on the site: reviews, ratings, testimonials, customer counts, or any `AggregateRating` markup. An empty section is better than a fabricated one.

---

*Originally published as [How SiteBuilderStack.com was built with the Claude Code Website Launch System](https://sitebuilderstack.com/pages/case-study). Site Builder Stack is an independent product and is not affiliated with Anthropic; "Claude" and "Claude Code" are trademarks of Anthropic, PBC.*
