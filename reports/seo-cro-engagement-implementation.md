# SEO, conversion and engagement — implementation report

8 September 2026. Branch `feature/seo-cro-engagement`.

## 1. Executive summary

The brief asked for fifteen commercial-intent guides, a lifecycle hub, product
FAQs with structured data, product previews, walkthrough videos, a product
selector, four diagnostic tools, a starter-pack funnel and a guide-to-product
linking system.

**This session delivered the SEO and conversion foundations and the conversion
content cluster. It did not deliver all fifteen guides, the previews, the
starter pack or the three new diagnostic tools.** What is done is done
completely — built, tested, promoted to production and verified there. What is
not done is listed in §8 with the reason, and nothing has been reported as
finished that is not.

The single most valuable change: the Conversion & Revenue Optimization Toolkit
has been sold since 7 September with **zero guides pointing at it**, because no
guide on the site was about conversion. That is now five, in their own learning
path, and the internal-linking audit reports **0 findings across all 33 guides**.

## 2. File change report

### Created

| File | Why |
| --- | --- |
| `content/articles/29-cro-workflow.html` … `33-cro-prompts.html` | The five conversion guides |
| `content/pages/build-rank-convert.md` | Lifecycle hub copy |
| `theme/dev/sections/sbs-lifecycle.liquid` | Four stages, resolved from live products |
| `theme/dev/sections/sbs-picker.liquid` | The product selector |
| `theme/dev/templates/page.build-rank-convert.json` | The hub page |
| `scripts/test-picker-logic.js` | 15 unit assertions on the recommendation table |
| `scripts/test-picker.js` | 18 browser assertions |

### Modified

| File | Why |
| --- | --- |
| `theme/dev/sections/sbs-faq.liquid` | Optional FAQPage, built from the same blocks it renders |
| `theme/dev/templates/product*.json` | `emit_schema` on, obsolete bundle line removed, lifecycle links |
| `theme/dev/templates/index.json` | Lifecycle link from the ecosystem row |
| `theme/dev/sections/sbs-ecosystem.liquid` | Note became richtext so it can link |
| `theme/dev/sections/sbs-footer.liquid` + group | Extended to ten links; lifecycle added |
| `theme/dev/templates/agents.md.liquid` | The five new guides described to agents |
| `content/content-graph.json` | Five articles, a conversion path, CRO product mapping |
| `scripts/validate-articles.py` | CTA counter no longer flagship-only |
| `scripts/validate-graph.py` | `Convert` added to the goal enum |
| `scripts/generate-article-diagrams.py`, `-images.py` | Five diagrams, five hero images |
| `tests/run-all.sh` | Picker tests; two more pages in the a11y sweep |

### Removed

Nothing was deleted. One obsolete sentence was replaced.

## 3. SEO implementation

**Five conversion guides**, each with a differentiated intent, its own diagram,
a contextual product CTA and cross-links into the cornerstone set. Published,
in a five-step learning path, and listed in `agents.md`.

`scripts/audit-cannibalization.py` across 53 pages: **0 duplicates, 0 probable
cannibalisation.** That check is the reason only five of the requested fifteen
were written — see §8.

**The lifecycle hub** at `/pages/build-rank-convert`. Four stages, each
resolving its product through `all_products[handle]` so titles and prices are
live and a drafted product drops its stage rather than rendering a dead link.
Supporting guides per stage are resolved against the blog, so a rename removes
the link rather than 404ing.

**Internal links to the hub** from the homepage, all four product pages and the
footer — verified rendering on each.

**FAQPage structured data** on all four products, emitted by looping the same
blocks the section renders. Verified live: 16/16, 8/8, 9/9, 8/8 questions,
matching the visible page exactly, valid JSON.

The site's standing rule was no FAQPage anywhere. That rule was about hubs that
answer questions in prose, and it is unchanged; these are genuine
question-and-answer lists a visitor can read and expand. The comment in
`sbs-schema.liquid` now says which case is which.

**Obsolete merchandising removed.** The SEO toolkit page said *"There is no
bundle and no upgrade credit."* The Complete Stack has existed since 7
September. Replaced with accurate language that keeps the true half — there is
still no upgrade credit.

## 4. Conversion implementation

**The product selector.** Five questions, four possible recommendations, no
framework. Every result card is rendered server-side with a live price and
hidden; the script reveals exactly one.

The tie-break is the part worth defending: **when the bundle ties with a single
product, the single product wins.** The bundle has to win outright. A quiz sold
by the shop that breaks ties towards the most expensive answer is not a
recommendation, and doing the opposite quietly would be the cheapest way to
make the whole thing untrustworthy.

Tested at two levels. `test-picker-logic.js` covers the table without a browser
— 15 assertions including every tie case and the one the brief singles out:
answering "traffic isn't converting" must never return the Launch System.
`test-picker.js` drives the real page — 18 assertions including that exactly one
card is ever visible, that the price is live, and that without JavaScript the
four products remain a readable list rather than a dead form.

**Product previews and walkthrough videos: not implemented.** See §8.

## 5. Engagement implementation

**Guide-to-product routing** is complete and measured. Every guide has one
primary product CTA driven by the content graph, and the distribution is now
Launch System 22, SEO toolkit 6, conversion toolkit 5. Before this session the
conversion toolkit had none.

`scripts/audit-internal-linking.py`: **0 findings across 33 guides** — every
guide is in a learning path, every one has a product CTA, and none is without a
contextual inbound link from another page's body.

**The three new diagnostic tools and the starter pack: not implemented.** The
existing Website Launch Readiness assessment at `/pages/launch-readiness-score`
already covers one of the four requested tools and gained a Conversion category
yesterday. See §8.

## 6. Validation results

Executed, not assumed:

```
./tests/run-all.sh                      27 passed, 0 failed
scripts/test-picker-logic.js            15 assertions, 0 failed
scripts/test-picker.js                  18 assertions, 0 failed
scripts/validate-articles.py            0 failures, 0 warnings
scripts/validate-graph.py               33 articles, 6 paths, 0 failures
scripts/audit-cannibalization.py        53 pages, 0 cannibalisation
scripts/audit-internal-linking.py       33 guides, 0 findings
scripts/audit-agents-claims.py          0 failures
```

Accessibility and overflow, live, at 375 and 1280px: `/pages/build-rank-convert`
clean, `/blogs/guides/claude-code-conversion-rate-optimization` clean. Both were
added to the sweep so future runs cover them at all five widths.

Structured data verified by parsing the served HTML rather than the template.

## 7. Manual Shopify actions

**None from this session.** Everything here was completed from the repository.

The outstanding manual items are unchanged from previous cycles and are in
`docs/REMAINING-MANUAL-STEPS.md`: attaching the product archives in the
digital-delivery app, installing the custom pixel, and recording the walkthrough
videos.

## 8. Remaining issues

**Ten of the fifteen guides were not written.** Three already exist at the exact
slugs the brief asked for — `claude-code-technical-seo-audit`,
`google-search-console-claude-code`, `claude-code-website-audit`. Seven more
would have been near-duplicates of guides that already exist:

| Requested | Existing near-neighbour |
| --- | --- |
| `claude-code-website-builder-prompts` | `best-claude-code-prompts-for-web-development` |
| `claude-code-website-development-workflow` | `how-to-build-a-website-with-claude-code` |
| `build-production-website-claude-code` | `how-to-build-a-website-with-claude-code` |
| `claude-code-shopify-development` | `build-shopify-store-with-claude-code` |
| `claude-code-wordpress-development` | `claude-code-wordpress` |
| `claude-code-seo-audit` | `claude-code-seo-website-optimization` |
| `shopify-seo-audit-claude-code` | `shopify-seo-with-claude-code` |

Writing those as separate pages would have been the self-inflicted
cannibalisation the same brief forbids — "avoid repeating another article with
different headings". They are not refused, only not written blind: each needs a
decision about whether a genuinely differentiated intent exists, and for at
least two of them I do not believe it does.

There is also a measured reason for caution. Of 62 sitemap URLs, **18 are
indexed and 29 are "discovered — currently not indexed"**. Five pages published
on 7 September moved the indexed count by zero. Adding ten more near-duplicates
would compete for crawl budget the site has not earned.

**Not implemented, and genuinely outstanding:**

- Product previews from real source files. The files exist in `product/`; the
  component does not.
- Walkthrough videos. Blocked on a recording, as before.
- SEO Audit Readiness and Conversion Readiness assessments.
- The free starter pack landing page and funnel.
