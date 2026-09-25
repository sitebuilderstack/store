# Website Launch & Conversion Review — SAMPLE

> **This is a sample of the report format, produced by reviewing Site Builder
> Stack's own website.** It is not a customer engagement, and no customer is
> described here. Every observation below was captured from
> `sitebuilderstack.com` on 24 September 2026 and can be checked by anyone.
> Reviewing our own site is deliberate: it is the only site we can publish a
> real report about without inventing a client.

**Site:** sitebuilderstack.com
**Prepared for:** Site Builder Stack (self-review, published as a sample)
**Review date:** 24 September 2026
**Reviewed by:** Site Builder Stack

---

## Scope

Five pages, as served publicly on the review date. A review of what those pages
show. Not a security assessment, not an accessibility or legal audit, and not an
analysis of visitor behaviour — no analytics was used, and nothing below claims
to know what visitors did.

### Pages examined

| # | URL | Status on review date |
| --- | --- | --- |
| 1 | `/` | 200 |
| 2 | `/products/claude-code-website-launch-system` | 200 |
| 3 | `/collections/all` | 200 |
| 4 | `/pages/build-rank-convert` | 200 |
| 5 | `/blogs/guides` | 200 |

---

## Summary

The technical layer is in good order: every page returned 200, each carries a
self-referencing canonical, titles and descriptions are within length and
unique, and the purchase path is a real Shopify cart form rather than a link to
somewhere else. The messaging on the homepage and the product page is concrete
and specific about what is being sold.

The clearest finding is a **naming mismatch on the primary call to action**:
the homepage's main button says "Get the Launch System — $19.99" and lands on
`/#buy`, a section of the homepage — not the product page. A visitor who clicks
the price expecting the product page stays on the homepage. The second finding
is that **the catalogue page presents eight products with no ordering by need**,
which pushes the choice onto a visitor who has usually not yet decided what
problem they have.

**Findings: 4 — 0 critical, 2 high, 1 medium, 1 low.** Four is what the evidence
supported; the format does not require a fixed number.

---

## Findings

### HIGH — The primary homepage CTA lands on a homepage section, not the product

**Page:** `/`

**What was observed**

> The first button in the page's main region reads **"Get the Launch System —
> $19.99"** with `href="/#buy"`. The `#buy` anchor is a homepage section headed
> "Get it — Everything, one price". The product page is reached by a second
> button further down.

**Why it matters**

A button carrying a price sets an expectation: the next screen is where you buy.
Landing on another section of the same page asks the visitor to re-orient and
find the real path. This is a message-match problem between the button and its
destination, not a design problem.

**Recommended action**

Decide which is the intended destination for the priced CTA — the buy section or
the product page — and make the label match. If the buy section is intended,
label it "See what's included"; if the product page is intended, point the href
there. Do not change both.

**How to validate the fix**

Click the first CTA on `/` and confirm the resulting URL and what is at the top
of the viewport. The label should describe where you arrive.

**If you want Claude Code to do it**

```text
Read-only. On the homepage template, list every element with a class containing
"sbs-btn", in document order, with its visible text and its href. For each, say
what a visitor would expect the destination to be from the text alone, and what
the destination actually is. Do not change anything; output a table.
```

---

### HIGH — The catalogue page lists eight products without ordering them by need

**Page:** `/collections/all`

**What was observed**

> Title "Products – Site Builder Stack", H1 "Everything Site Builder Stack
> sells", eight products with nine price mentions, and one call to action:
> "Back to the homepage". No sorting, no filtering, and no "start here".

**Why it matters**

Eight similarly-named systems at three price points is a decision the page does
not help with. The site does solve this elsewhere — `/pages/build-rank-convert`
orders the products by lifecycle stage, and the homepage's product row explains
which suits which problem — but a visitor who arrives at the catalogue directly
does not get that.

**Recommended action**

Give the catalogue page the same framing as the lifecycle page, or link to it
prominently at the top. This is a content decision, not a template change.

**How to validate the fix**

Open `/collections/all` as a first-time visitor and time how long it takes to
decide which product answers "my site is live and I need to keep it running".

---

### MEDIUM — The product page's "Get it" button scrolls within the page

**Page:** `/products/claude-code-website-launch-system`

**What was observed**

> The page's primary button reads "Get it — $19.99" with `href="#buy"`, and the
> `#buy` section lower down contains the real Shopify form — `<form
> action="/cart/add">` with "Add to cart — $19.99" and a dynamic payment button.
> The page is 3,405 words with fifteen `<h2>` sections.

**Why it matters**

The mechanism works and the cart form is real, so this is not broken. But on a
long page a priced button that scrolls rather than buys costs an extra decision
at the moment of highest intent, and on a phone the scroll can overshoot.

**Recommended action**

Consider making the top button submit the cart form directly, keeping the
scroll link as a secondary "see what's included". Test on a phone before and
after; do not change the cart form itself.

**How to validate the fix**

Tap the top button on a phone and confirm what happens next is the cart, not a
position on the page.

---

### LOW — The catalogue page's title is the least specific of the five

**Page:** `/collections/all`

**What was observed**

> `<title>Products – Site Builder Stack</title>` — 29 characters, against 52–62
> on the other four pages, all of which name what is sold.

**Why it matters**

"Products" describes the page type, not the products. In a result list it
competes on brand alone.

**Recommended action**

Name what the products are, for example "Claude Code systems for websites". Keep
it under 60 characters including the store name.

**How to validate the fix**

Fetch the page and count the rendered title length; check it is not truncated in
a result preview.

---

## Priority definitions

| Priority | Meaning |
| --- | --- |
| **Critical** | The page cannot do its job, or is telling search engines not to show it |
| **High** | A visitor is likely to be lost at a specific point, or an important signal is wrong |
| **Medium** | Worth fixing; the cost of leaving it is real but bounded |
| **Low** | Tidy-up. Do it when touching the page anyway |

---

## Not checked

- **Visitor behaviour.** No analytics was accessed. Nothing above says what
  visitors did, only what the pages show.
- The 36 guides, 8 checklists, 4 tools, labs and challenge pages — outside the
  five URLs reviewed.
- Checkout itself. The cart form was observed; no order was placed.
- Security, beyond what a public response reveals.
- Accessibility against WCAG. (This site runs its own rendered audit
  separately; that is not part of this service.)
- Field performance. No lab or field measurement was taken for this report.
- Whether any recommendation would improve traffic, rankings or revenue.

---

## What happens next

One round of written clarification questions, within 14 days, at
admin@sitebuilderstack.com.

This report recommends; it does not implement.
