# How SiteBuilderStack.com Was Built With the Claude Code Website Launch System

This store sells a system for building production websites with Claude Code. It was built
with that system. This is what happened, including the parts that went wrong.

Nothing here is a customer story, because there are no customers yet to quote. It is a
first-hand account of one build, with the evidence attached.

## What had to exist

A working business, not a demo:

- A Shopify storefront with a custom theme rather than a purchased one wearing a new logo
- One digital product, priced, with delivery that actually delivers
- Legal pages that describe what the store really does
- Enough published content to be worth finding
- Structured data, sitemap, and search-engine registration
- Payments that take money
- A way to tell whether any of the above was true

The last one turned out to be the hard part.

## The method

The Launch System's workflow runs thirteen stages in dependency order — Research, Plan,
Architect, Design, Build, Write, Optimize, Secure, Test, Deploy, Index, Monitor, Improve.
The order is the point: each stage produces something the next one can be checked against.

The modules used, in the order they came up:

| Stage | Module | What it produced |
| --- | --- | --- |
| Plan → Architect | `01-Master-System` | The site's structure and the build order |
| Before any code | `02-Claude-Code-Configuration` | A `CLAUDE.md` naming the platform rules that are not guessable |
| Build | `04-Shopify` | The theme layer, catalogue, policies, digital delivery |
| Optimize | `03-SEO-System` | Metadata, structured data, internal linking, sitemap validation |
| Secure | `11-Security` | Credential handling, headers, the rule that no token reaches a template |
| Test | `12-Accessibility` | Contrast, keyboard, target size, the rendered-DOM audit |
| Deploy → Index | `13-Search-Engines` | Search Console, Bing Webmaster Tools, IndexNow |
| Launch | `14-Checklists` | What to check before and after taking money |

The `CLAUDE.md` step is the one worth calling out. A Shopify theme has rules an assistant
cannot infer by reading the repository — `policy` is not a valid template type, the
`agents.md` template runs in a restricted Liquid context where referencing `shop` renders
empty with no error, and a section's `max_blocks` must be raised and pushed *before* a
section group that exceeds it. Every one of those cost time before it was written down.

## Five things that were broken and looked fine

None of these were visible to somebody looking at the site. All were found by fetching
something and measuring what came back.

### 1. The primary call-to-action was invisible

**Symptom:** nothing. The button was there, the right size, in the right place.

**Cause:** its text and its background computed to the same colour. A generic link rule
outranked the button rule by a single point of CSS specificity.

**Found by:** computing the contrast ratio of every text node against its actual composited
backdrop in a rendered DOM. It came back at 1:1.

**Lesson:** reading the stylesheet would never have found this. Specificity bugs are only
visible after the cascade has resolved.

### 2. The homepage title was the raw `.myshopify.com` domain

**Symptom:** none in a browser tab.

**Cause:** Shopify's homepage title comes from Online Store → Preferences, not the theme.
When that field is empty, `page_title` falls back to the store's internal domain. There is
no Admin API mutation for it, so no script could set it or check it in the admin.

**Fix:** the layout now supplies the homepage title from a theme setting instead.

**Found by:** fetching the homepage and reading the `<title>` out of the response.

### 3. Every call-to-action on every non-home page was dead

**Symptom:** a click that did nothing. No error, no navigation.

**Cause:** the buttons linked to `#buy`, a fragment that only exists on the homepage.

**Found by:** resolving each fragment link against the page it appears on rather than
assuming a `#` link is always valid.

### 4. The store could not accept payments

**Symptom:** at checkout, "This store can't accept payments right now."

**Cause:** Shopify Payments was configured but never activated.

**Why every check missed it:** the notice is injected by JavaScript. It is absent from the
initial HTML, so every fetch-based check reported a healthy checkout for as long as this
lasted.

![Shopify checkout showing the message "This store can't accept payments right now" in place of the payment methods, with the product and the ninety-nine dollar total visible in the order summary beside it.](https://cdn.shopify.com/s/files/1/0987/3925/7636/files/evidence-checkout-payments-disabled.png?w=1100&h=1400)

**Found by:** rendering the checkout page in a real browser instead of fetching it.

### 5. A fulfilled order delivered nothing

**Symptom:** an order marked paid and fulfilled, and no download.

**Cause:** the order was placed with a phone number and no email address. The delivery app
sends by email only. Every status the platform reported said success.

**Found by:** checking whether the order actually had an email field, rather than trusting
the fulfilment status.

**Lesson:** "fulfilled" is a claim about a process, not about the customer receiving
anything.

## The failure mode behind all five

Every one of these was reported as healthy by something. That pattern turned out to be the
real subject of this build, and it kept happening to the checks themselves:

| The check said | What was true | Why |
| --- | --- | --- |
| 0 broken links | 9 of 28 pages never fetched | 429s were counted as nothing to report |
| Checkout healthy | Store could not take payments | The notice is injected by JavaScript |
| Checkout accepts email | Never actually checked | It read `innerText`; the wording is in a `placeholder` |
| Page has a Liquid error | The page was fine | A regex matched prose *about* Liquid errors |
| Delivery working | Delivered nothing | It never looked at whether the order had an email |

Five checks, each written carefully, each passing, none of them capable of failing on the
condition it existed to catch.

The rule that came out of it, and that now applies to every check in this repository:

> **After a check passes, break the thing it checks and confirm it goes red.**

A link crawler reporting "0 broken links" without ever having found one is not evidence of
anything. This costs about a minute per check and it has caught more real problems than any
other single practice in the build.

## What shipped

All verifiable at the time of writing:

| | |
| --- | --- |
| Storefront | Custom theme on a landing layout, one product, now $19.99 |
| Digital delivery | Working, verified end to end after the email fix |
| Published guides | 19, totalling more than 54,000 words |
| Free resources | 5, ungated, also downloadable as raw Markdown |
| Structured data | Organization, WebSite, Person, ProfilePage, Product, Blog, BlogPosting, BreadcrumbList |
| Sitemap | 35 URLs, validated rather than hand-written |
| Search engines | Google Search Console, Bing Webmaster Tools, IndexNow, all verified |
| Core Web Vitals | LCP 564–748 ms, CLS 0.0000, measured on the live site at 412 px |
| Accessibility | WCAG 2.2 AA checks passing at 320 px and 1280 px |
| Test suite | 9 checks, all passing |

That table is a snapshot of the first launch and has not been rewritten since. The
catalogue has grown: there are now four products — the Launch System at $19.99, the
[SEO & Website Audit Toolkit](/products/claude-code-seo-website-audit-toolkit) at $19.99,
the [Conversion & Revenue Optimization Toolkit](/products/claude-code-conversion-revenue-optimization-toolkit)
at $19.99, and the [Website Operations & Maintenance System](/products/claude-code-website-operations-maintenance-system)
at $39.99. The guide count, sitemap size and test count have all grown too. Updating the
numbers in place would make the record less useful, not more.

What is deliberately **not** on the site: reviews, ratings, testimonials, customer counts,
or any `AggregateRating` markup. There are no customers yet. An empty section is better
than a fabricated one, and review markup without reviews is a manual-action risk.

## What I would tell someone starting the same build

**Write the platform's non-obvious rules down before you write code.** Not the architecture
— an assistant can read that. The things that fail silently.

**Fetch the page. Do not read the template.** Four of the five failures above were invisible
in source and obvious in the response.

**Render it in a browser at least once.** The payment failure was invisible to every
fetch-based check because the notice arrives with JavaScript.

**Make every check fail once on purpose.** This is the whole lesson of the build.

**Separate auditing from fixing.** An assistant told to "check and fix" will fix things
before anyone decides they matter, and the record of what was wrong disappears into a
commit.

## The free version of all of this

The methodology is published in full and free to read — 19 guides, and five checklists you
can work through without giving anyone an email address:

- [How to build a website with Claude Code](/blogs/guides/how-to-build-a-website-with-claude-code) — the full workflow
- [How to build a Shopify store with Claude Code](/blogs/guides/build-shopify-store-with-claude-code) — the platform specifics
- [Claude Code website audit](/blogs/guides/claude-code-website-audit) — the four-pass method that found the five failures
- [Running a technical SEO audit](/blogs/guides/claude-code-technical-seo-audit) — including the checks that could not fail
- [Free resources](/pages/resources) — launch, SEO, security and audit checklists

## Build your own production workflow

The [Claude Code Website Launch System](/products/claude-code-website-launch-system) is the
assembled version: 113 files across 17 modules, 100 reusable prompts, and the checklists
and audits described above, as one download.

It will not stop you making these mistakes. It will make you find them before a customer
does.
