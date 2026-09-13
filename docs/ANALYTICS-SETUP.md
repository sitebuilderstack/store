# Analytics Setup

Nothing is installed. This is where to put it when you decide what you want.

**A principle worth holding to:** do not add tracking you will not look at.
Every script costs performance, adds a consent obligation, and creates a data
protection responsibility. A store with three products and one conversion type
needs very little.

---

## What you get without adding anything

Shopify's own analytics already records sessions, traffic sources, conversion
rate, and orders, with no configuration and no additional script. **For a store
this size it may genuinely be enough.** Look at it for a month before adding
anything else.

One thing it does not give you is which product a visitor was looking at when
they clicked away, which now matters with three. The theme's own
`data-sbs-track` events cover the placements that route between them:
`product_nav_clicked` (header menu), `product_ecosystem_clicked` (the
three-product rows on the homepage and the product pages) and
`product_cta_clicked` (the closing CTA on a product page). They are three
separate names on purpose — merging them would make all three unreadable.

## Insertion points

**`{{ content_for_header }}`** in `layout/landing.liquid` is present and is the
required hook. Shopify injects its own analytics, the Customer Events pixel
framework, and app-injected scripts through it. Removing it breaks analytics and
several platform features.

**Customer Events** (Settings → Customer events) is the right place for
third-party pixels. Scripts added there run in a sandbox, are covered by
Shopify's consent handling, and survive theme changes. **Prefer it to editing
the theme.**

**Theme edits** are the last resort. If you must, add to
`layout/landing.liquid` before `</head>`, and remember the ONE theme's
`layout/theme.liquid` serves the remaining templates — a script added to one
will not run on the other.

## If you add GA4

1. Create the property; get the measurement ID
2. Add it via Customer Events, not the theme
3. **Verify it is receiving data in the GA4 interface** — not that the tag is
   present, that events arrive
4. Mark the purchase event as a conversion
5. Exclude your own traffic
6. Confirm the consent banner gates it where required

## Consent

If you sell to the EU, UK, or certain US states, non-essential analytics needs
consent. Shopify provides a consent banner and a Customer Privacy API that
Customer Events respects automatically. **This is a legal question, not a
technical one** — the answer depends on where your customers are and what you
collect.

The store already has a `/pages/privacy-policy` page describing what is
collected. **If you add analytics, update it.** A privacy policy that does not
match what the site does is worse than none.

## What to actually watch

For this store, four numbers:

| Metric | Why |
| --- | --- |
| Sessions | Is anyone arriving? |
| Conversion rate | Is the page working? |
| Traffic source | Which channel is worth more effort? |
| Refund rate | Is the product matching expectations? |

Everything else is interesting rather than useful, at this stage.

## Search Console and Bing

Not analytics, but the more valuable instrumentation for a new store — they tell
you what queries you appear for, which is direct feedback on whether the copy
matches what people search.

Set up only after the storefront password is removed; a password-protected store
cannot be indexed. See `13-Search-Engines/` in the product.
