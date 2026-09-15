# Content roadmap — conversion & revenue

Written 2026-09-06, after the Conversion & Revenue Optimization Toolkit
launched. Figures refreshed 2026-09-07.

The guides are the store's distribution. Twenty-seven are published and every one
of them serves the Launch System or the SEO toolkit; **none serves the conversion
toolkit at all.** That is the gap this roadmap closes, and the internal-linking
audit now measures it directly: `reports/internal-linking-audit.md` reports 21
guides pointing at the Launch System, 6 at the SEO toolkit, and 0 at the
conversion toolkit.

The bundle launched on 2026-09-07, which changes the shape of the gap slightly
but not its size. Every guide now carries a one-line bundle upsell beneath its
own product CTA, so the conversion toolkit is at least *reachable* from the
content library. It is still not *recommended* by anything, because recommending
it from a guide about GitHub Actions would be a mismatch a reader would notice.

## The constraint, stated honestly

The site's binding constraint is authority, not on-page optimisation. Over 90
days to 2026-09-07: 1,093 impressions, 3 clicks, 134 queries, and **8** query/page
rows in positions 4–20 — most of which are one person's certification quiz
question. So the striking-distance playbook does not apply yet, and neither does
"optimise what we have".

The harder number is indexation. **24 of 57 sitemap URLs are "discovered —
currently not indexed"**, against 18 indexed. Publishing more pages competes for
crawl budget the site has not earned, which is the argument for writing few and
linking them properly rather than writing many.

New topical coverage on topics with genuine search demand and no existing page
remains the only lever shown to move anything here — but it should be paced
against indexation, not against a content calendar.

Which means: **write the articles, publish them, wait.** Do not expect any of
these to rank inside a month, and do not judge them on that.

## Priorities

Ordered by three things, in this order: does the topic have search demand, does
it have a natural product tie, and is it something this site can say something
non-obvious about. A guide that repeats what is already on the first page of
results is a cost, not an asset.

### Tier 1 — publish first

**1. Claude Code Conversion Rate Optimization**
The head term for the whole cluster and the hub the rest link into. Covers the
four modes, the finding format, the honesty labels, and why an audit that fixes
things in the same session is not an audit. Ties directly to the toolkit's
master audit. *Product tie: strong. Demand: moderate and growing. Uniqueness:
high — the mode convention is not a thing anyone else writes about.*

**2. How to Audit a Shopify Store for Conversions With Claude Code**
The highest-intent piece in the set. Reads the theme rather than the rendered
page: `image_url` with no width, `loading="lazy"` on the first image in a loop,
required checkout fields, an app pixel duplicating the native `purchase` event.
Every one of those is checkable and specific. *Product tie: the Shopify module.
Demand: strong — "shopify conversion rate optimization" is a busy query with a
lot of thin content on it.*

**3. Analytics Event QA: Proving Your Tracking Is Not Lying**
The both-directions rule, applied to conversion events. Positive test plus five
negative tests. Includes the duplicate-purchase-on-refresh case, which is common,
expensive and almost never written about. *Product tie: the analytics module.
Uniqueness: high. This is the article most likely to be linked to.*

**4. When Not to A/B Test**
Contrarian, useful, and short. Most sites cannot run a useful experiment and
almost nothing written about CRO says so. Includes the actual arithmetic.
*Product tie: the experimentation module. Uniqueness: very high.*

### Tier 2 — next

**5. Conversion Funnel Mapping With Claude Code**
Turning a repository and an analytics export into a funnel with the unmeasured
steps marked as unmeasured rather than estimated.

**6. The Checkout Audit: 8 Things That Cost Mobile Sales**
Keyboard covering the submit button, cost revealed at the shipping step, forced
accounts, address forms wrong for a market. Device-specific and reproducible.

**7. Writing Conversion Copy With Claude Code Without Inventing Evidence**
The `[NEEDS PROOF]` marker, the claims table, and why asking a model for
persuasive copy reliably produces statistics that do not exist.

**8. Measurement Plans: The Document That Stops Your Analytics Rotting**
Questions first, events second, both-directions QA, and a deprecation plan.

### Tier 3 — after the first four have had a quarter

**9. Trial-to-Paid: Diagnosing a SaaS Funnel With Claude Code**
Segmenting activated from non-activated before anything else.

**10. Dark Patterns Your AI Will Suggest, and What to Do Instead**
The prohibition list with the honest alternative for each. Genuinely useful, and
the one piece here most likely to be shared outside the developer audience.

## What each article must do

Every one of these ties to the toolkit, and the tie has to be earned:

- **It stands alone.** Someone who never buys anything should get a working
  method out of it. The guides are already written this way and it is why they
  get linked to.
- **It links to the product once, in context**, using the existing
  `sbs-inline-cta` aside — not a banner, not three times.
- **It links to two or three sibling guides**, and into the hub.
- **It contains something checkable.** A number, a selector, a file path, a
  reproduction. Articles without one read as summaries of other articles.

## What is deliberately not on this list

**A "conversion rate optimization checklist" listicle.** The first page of
results is already twenty of them and there is nothing to add.

**"X% conversion increase" case studies.** There are no customers with results
to report, the toolkit prohibits predicting lifts, and inventing one would
contradict the product on its own core claim. If a real, measured, permitted
case study becomes available, it goes to the top of Tier 1.

**Anything that needs a testimonial.** There are none.

## The hub question

The four topic hubs (`/pages/claude-code-web-development`, `-seo`, `-shopify`,
`-production`) organise every guide. Conversion has no hub, and four articles do
not justify one. **Revisit at six articles**, not before — a hub with four
children is a page with four links on it, and it competes with the articles it
is supposed to organise.

Until then, articles 1–4 link to each other and article 1 acts as the informal
entry point.

## How to tell whether this worked

Not by traffic in the first month. The honest measures, at the horizons they
apply to:

| When | What to look at |
| --- | --- |
| Week 1 | Indexed at all. Request indexing; check coverage. |
| Month 1 | Impressions in Search Console for any query, on any of the four. |
| Month 3 | Whether any query has reached positions 4–20 — the point at which optimisation becomes worth doing. |
| Month 6 | Whether any article has produced a session that reached a product page. |

`product_ecosystem_clicked` and `product_cta_clicked` are already instrumented,
so the last row is measurable without adding anything.

## Sequencing note

Publish one at a time and let each be indexed before the next. Four articles
published on one day compete with each other for the same crawl budget and give
you no way to tell which one worked.
