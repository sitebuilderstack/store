# Growth sprint report — 3 September 2026

Two tracks: Google search growth, and sales conversion. What changed, what the evidence
was, and what is still not done.

Companion documents:
[`SALES-FUNNEL.md`](SALES-FUNNEL.md) ·
[`PRODUCT-DEMO-SCRIPT.md`](PRODUCT-DEMO-SCRIPT.md) ·
[`emails/`](emails/) ·
[`../seo/GSC-STRIKING-DISTANCE.md`](../seo/GSC-STRIKING-DISTANCE.md) ·
[`../seo/GSC-CTR-OPPORTUNITIES.md`](../seo/GSC-CTR-OPPORTUNITIES.md) ·
[`../seo/GSC-CONTENT-OPPORTUNITIES.md`](../seo/GSC-CONTENT-OPPORTUNITIES.md) ·
[`../seo/LINK-EARNING-CAMPAIGN.md`](../seo/LINK-EARNING-CAMPAIGN.md)

---

## Track A — Google

### The data available

First impression on record: **27 August 2026**. Eight days of history. Every window in the
reports is clamped to what exists; nothing is extrapolated.

| | 28 days to 3 Sept |
| --- | --- |
| Impressions | 884 |
| Clicks | 1 |
| Average position | 61.4 |
| Queries with impressions | 110 |
| Pages with impressions | 13 |
| Indexed (of 35 sitemap URLs) | 18 |

### The striking-distance system

`scripts/gsc-opportunities.py` fetches live Search Console data, tiers it by position,
scores it, and writes three reports. It is analysis only — it never modifies the site.

The scoring model is `impressions × proximity × (1 + 0.35 × commercial relevance)`.
Deliberately simple: a score is a sort order, not a forecast.

**It is built to refuse to flatter the data.** Two conditions are computed and printed into
the report itself, so a future regeneration cannot quietly drop them:

- When every Tier A row has under 5 impressions, the report says the tier is noise and
  should not be treated as a work list. That is currently true — the three Tier A rows are
  a literal MCP tool name and two long verbatim sentences lifted from an article body.
- When most pages with volume sit past position 40, the report says that gap is an
  authority problem rather than an on-page one. Also currently true.

### Pages improved, and the evidence for each

| Page | Evidence | Change |
| --- | --- | --- |
| `claude-code-skills` | 335 impressions — the most of any page — at position 71.1, and the shortest article on the site at 1,858 words. Roughly a third of its queries are install/list intent: "how to add skills to claude code", "how to download skills in claude code", "list claude code skills", "claude code skills and commands" | Added three sections: adding a skill someone else wrote, finding and running the skills you have, and the merge of custom commands into skills. Facts checked against `code.claude.com/docs/en/skills`. 1,858 → 2,480 words |
| `claude-code-seo-website-optimization` | "claude code seo" (35 impressions) and "claude code for seo" (22) — the highest demand on the site — both landing here at position ~50 | Added a direct answer at the top: can Claude Code do SEO, in three paragraphs, before the nuanced framing |
| `build-shopify-store-with-claude-code` | "connect shopify to claude code" (6 impressions, position 60), "claude shopify" (3) | Added a "How to connect Claude Code to Shopify" section: the two real connections and the one that is admin-only |

No other page was touched. The rest are high-quality and rewriting them on this little data
would risk more than it gains.

### Internal linking

A correction was needed first. The product page was described earlier in this project as
under-linked, on the basis of Search Console's `referringUrls` field showing two. That field
is a sample, not an exhaustive list: the product page has **12 inbound links from indexed
guides** plus header and footer, and the build pillar has 11. Neither is under-linked.

The real gap was the opposite. Four of the ten pages published in the previous sprint had
**zero** inbound links from any page Google has actually indexed — the only kind of link
that can raise crawl priority right now. Eight indexed guides now link to them
contextually. Every target is above zero.

### CTR opportunities

**None found, and that is the correct result.** No query has both enough impressions and a
position visible enough to judge. The report says so rather than inventing rewrites. A low
CTR at position 50 means nobody scrolled that far.

### Content decisions

**No new guides were published in this sprint.** The brief allowed two to four; the data
did not justify any. Nineteen guides and five resources is enough surface area, 16 of 35
URLs are still uncrawled, and adding more would make the crawled-to-published ratio worse.
The one genuine content gap the data showed — install and listing intent on the skills page
— was filled by expanding the page that already ranks for it rather than by creating a
competitor to it.

### Link earning

Prepared, not executed. `LINK-EARNING-CAMPAIGN.md` covers seven categories ranked by return
per hour, per-asset outreach angles, three templates, and the rules. `link-prospects.csv`
carries 14 researched category rows with a `source` column and **no fabricated contacts** —
an invented email address is worse than an empty row.

**Referring domains: 0.** Nothing was earned. The highest-leverage blocker is that the
GitHub repository is still unpublished.

---

## Track B — Sales

### Product demonstration

`sections/sbs-demo.liquid`, on the homepage above the outcome paths.

**There is no video, and the section does not pretend there is.** With `video_url` empty it
renders an eight-step written walkthrough of the actual download — real folder names, the
real START-HERE workflow table, the real thirteen-stage sequence, the real prompt library
listing. No play button, no dead player, no "coming soon" overlay.

Set `video_url` and it becomes a real `<video>` with poster, WebVTT captions,
`preload="metadata"` and a transcript link. **Both branches were tested**: the player
renders correctly with a URL set, and the walkthrough replaces it when empty.

`PRODUCT-DEMO-SCRIPT.md` is the shot list, the captions, the file names to produce and the
install steps.

### Outcome paths

`sections/sbs-outcomes.liquid` — "What are you trying to build?", five cards: new website,
Shopify store, SaaS product, existing site, Google rankings.

Every card shows a real stage chain and names the **actual file the buyer opens**, taken
from the product's START-HERE workflow table. Each links to the matching free guide rather
than the product — five identical product links in one section would be a sitewide
exact-match anchor pattern, and a guide is the better next click for someone still
deciding. One product CTA sits below the grid.

### Case study

**`/pages/case-study`** — "How SiteBuilderStack.com Was Built With the Launch System".
1,562 words.

Sections: what had to exist, the method with the module-to-stage mapping, five real
failures with symptom/cause/how-found/lesson, the checkout screenshot as evidence, the
table of five checks that could not fail, what shipped with verifiable numbers, lessons,
and a CTA.

No fabricated anything. No testimonials, no revenue figures, no conversion claims. The one
screenshot is a real capture of the checkout showing "This store can't accept payments
right now".

Linked from: homepage demo section, footer Product column, About page, resources hub, and
three guides.

### Email funnel

Five emails written in full, in `emails/`. Value → Education → Proof → Use case → Offer,
over eight days.

**Not configured, and it cannot be from here.** Two blockers:

1. **No email platform.** Three apps installed: Messaging, the Admin API app, Digital
   Products. Marketing automations are not creatable through the Admin API.
2. **The signup form has never produced a subscriber.** Zero customers carry the
   `claude-md-kit` tag; the only customer with an email is `NOT_SUBSCRIBED`.

Whether `contact[tags]` actually applies the tag is **specifically unverified** — storefront
hCaptcha blocks automated submission, correctly, so it could not be tested. `funnel-metrics.py`
reports tagged and subscribed counts separately so the answer appears the moment somebody
signs up.

### Analytics

`scripts/funnel-metrics.py` measures the funnel from Shopify Analytics, ShopifyQL and the
Admin API. **No tracking script was added.** At single-digit human sessions, heatmaps and
session recording would produce noise while costing performance and creating a
data-protection obligation.

---

## Validation

| Check | Result |
| --- | --- |
| Test suite | 9/9 |
| Article validator | 19 articles, 0 failures |
| Site-wide SEO audit | 0 findings (3 documented platform notes) |
| SEO audit self-test | All 11 rules fire; silent on clean, noindex and alias records |
| Accessibility, 320px and 1280px | Clean on homepage, case study, guides |
| Core Web Vitals | LCP 676 ms, CLS 0.0000, 1,070 KB — unchanged by the new sections |
| Broken links | 0 |
| Checkout | Adds at $99.00 USD, hands off to Shopify checkout |

Two bugs found and fixed during validation:

- The case study's `h1` contains `SiteBuilderStack.com`, an unbreakable token that pushed
  the page into horizontal scroll at 320px. Fixed with `overflow-wrap: break-word` on
  headings.
- The theme link auditor treated the demo section's deliberately empty `video_url` as a
  placeholder link. Fixed to distinguish an empty setting (rendered conditionally, fine)
  from `#` (a link that goes nowhere, still an error) — control-tested both ways.

---

## Outstanding

| Item | Blocker |
| --- | --- |
| GitHub repository | No credentials in this environment |
| Email platform | Must be installed and configured in the Shopify admin |
| First signup | Nobody has completed the opt-in form |
| `contact[tags]` behaviour | Cannot be tested without solving hCaptcha |
| Demo video | Needs recording; script is ready |
| Store contact email | Admin UI only; still shows the legacy address in the privacy policy |
| Referring domains | 0; outreach is prepared, not sent |
