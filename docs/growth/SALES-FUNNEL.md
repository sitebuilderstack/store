# Sales funnel

What the path from search result to purchase looks like, what measures each step, and
which steps currently have no data because nobody has taken them yet.

Regenerate the numbers with `python3 scripts/funnel-metrics.py --days 28`.

## The path

```
Google / Bing search
        ↓   guides rank; 19 published
Guide article
        ↓   every guide links to a free resource and the product
Free resource  (/pages/resources, 5 ungated checklists)
        ↓   the hub and every guide offer the Starter Kit
Email signup   (CLAUDE.md Starter Kit)
        ↓   5-email sequence over 8 days
Case study / demo
        ↓   proof, then outcome paths
Product page
        ↓
Cart → Checkout → Purchase
```

## What measures each transition

| Transition | Measured by | Status |
| --- | --- | --- |
| Search → guide | Search Console impressions and clicks per page | Working: 884 impressions, 1 click |
| Guide → resource | Shopify sessions by landing page, plus internal referrers | Working |
| Resource → signup | Customers tagged `claude-md-kit` | **Zero. Never fired** |
| Signup → sequence | Email platform's automation stats | **No platform installed** |
| Sequence → case study | Sessions on `/pages/case-study` from email | Blocked on the above |
| Case study → product | Sessions on the product page | Working |
| Product → cart | Shopify Analytics → add to cart | Working |
| Cart → purchase | Orders | Working; 0 orders to date |

## Current numbers

From `scripts/funnel-metrics.py`, 28 days to 3 September 2026:

| Step | Count |
| --- | --- |
| Sessions, homepage | 159 |
| Sessions, top guide (`how-to-build-a-website-with-claude-code`) | 11 |
| Sessions, product page | 10 |
| Sessions, resources hub | 7 |
| Sessions, case study | 6 |
| Customer records | 2 |
| Starter Kit signups | **0** |
| Marketing subscribers | **0** |
| Orders | **0** |

**Read those session figures with suspicion.** Traffic on a store this new is mostly
crawlers and this project's own automation. Search Console's 884 impressions and 1 click
is the more honest picture of human interest. Do not compute a conversion rate from the
session numbers — the denominator is not people.

## The two blockers

**1. No email platform.** Three apps are installed: Messaging, the custom Admin API app,
and Digital Products. Marketing automations cannot be created through the Admin API, so
the five-email sequence in [`emails/`](emails/) cannot be scripted. Somebody has to install
an email app and build the automation in its UI.

**2. The signup form has never produced a subscriber.** It has been live for days with zero
entries. Until one person completes it, everything downstream is theory.

Specifically unverified: whether the `contact[tags]` field on the form actually applies the
`claude-md-kit` tag. Storefront hCaptcha blocks automated submission — correctly — so it
could not be tested from here. `funnel-metrics.py` reports tagged and subscribed counts
separately so the answer is visible the moment somebody signs up: subscribers with no tag
means the tag is not applying, and the automation trigger has to key off consent and date
instead.

## What is worth measuring, and what is not

**Worth it:** impressions and clicks per page, signups, product-page sessions, add-to-cart,
orders. All available from Shopify Analytics, the Admin API and Search Console with no
added script.

**Not worth it yet:** scroll depth, heatmaps, session recording, per-element click tracking.
At single-digit human sessions these produce noise, and each one costs performance, adds a
consent obligation and creates a data-protection responsibility. Revisit when there is
traffic to segment.

**Never:** fingerprinting, or any tracking not disclosed in the privacy policy.

## The honest read

The funnel is built and instrumented end to end. **It has never been walked.** Zero
signups, zero orders. Every number below the search step is currently a description of
plumbing rather than behaviour, and the first job is not optimising the funnel — it is
getting enough qualified traffic into the top of it that the rest becomes measurable.
