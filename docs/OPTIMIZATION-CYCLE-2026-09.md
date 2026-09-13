# Optimization cycle — September 2026

Turning a product site with a good blog into a topic-organised learning
platform. Implemented, live, and tested; this is the record of what changed and
what was measured.

## 1. What changed

**Information architecture.** Four topic hubs, four learning paths, and an
editorial relationship graph behind every internal link. Previously the blog was
chronological and its "related articles" block rendered the three *newest*
guides regardless of subject.

**Data, not markup.** `content/content-graph.json` holds pillars, paths, and per
guide topic / level / type / goal / related / resource. `publish-graph.py`
writes it to Shopify metafields as **bare handles only**; the theme resolves
handles against the live blog, so no metafield can hold a stale title.

**Guide library.** `/blogs/guides` gained search plus topic, level, goal and
type filters, derived from what exists rather than hard-coded. Client-side, with
a shareable querystring and no faceted URLs.

**Workflow selector.** A two-question router on the homepage producing a
five-step route through real URLs, plus a permanent hub row that does not depend
on answering anything.

**Article template.** Hub label with "Step N of M", three-level breadcrumb,
two in-article progression cards, previous/next through the learning path,
editorially chosen related guides, and a free resource matched to the guide's
intent.

**Interactive checklists.** All four checklist resources became tickable with
progress saved per browser — same URLs, no duplicated content.

**Failure library.** A new 3,100-word linkable asset, 20 entries, 16 of them
observed on this site and labelled as such.

**Copy components.** Prompt, command, CLAUDE.md and code blocks each get their
own button label and event.

**Measurement.** 26 engagement events through Shopify's existing analytics. No
second vendor.

## 2. Files

Created: `content/content-graph.json`, `content/workflow-selector.json`,
`content/pillars/*.html` (4), `content/pages/failure-library.md`,
`theme/dev/sections/sbs-pillar.liquid`, `theme/dev/sections/sbs-selector.liquid`,
`theme/dev/templates/page.pillar.json`,
`scripts/{publish-graph,publish-pillars,publish-selector,validate-graph,validate-selector,gsc-page-intent,check-a11y-json}.py`,
`scripts/test-{library-filter,workflow-selector,checklist,copy-buttons,analytics-events}.js`,
`docs/analytics/{EVENTS,BASELINE-2026-09-06}.md`, `docs/seo/LEARNING-PLATFORM.md`.

Modified: `sbs-article.liquid` (rewritten), `sbs-blog.liquid` (rewritten),
`sbs-resource.liquid`, `sbs-schema.liquid`, `sbs-footer.liquid`, both section
groups, `layout/landing.liquid`, `assets/sbs.{css,js}`,
`templates/{index,blog,agents.md}`, `scripts/{md2html,render-preview,publish-pages,validate-graph}.py`,
`resources/_hub.html`, `content/articles.json`, `tests/run-all.sh`.

## 3. New URLs

| URL | What |
| --- | --- |
| `/pages/claude-code-web-development` | Topic hub, 12 guides, 9-step path |
| `/pages/claude-code-seo` | Topic hub, 6 guides, 4-step path |
| `/pages/claude-code-shopify` | Topic hub, 6 guides, 2-step path |
| `/pages/claude-code-production` | Topic hub, 8 guides, 5-step path |
| `/pages/claude-code-failure-library` | Linkable asset, 20 failure classes |

No existing URL moved. No redirects were created.

## 4. Pillar architecture

```
Claude Code for Web Development  → terminal setup · build a website · production
                                   CLAUDE.md · CLAUDE.md examples · prompts ·
                                   skills · hooks · subagents · MCP · plugins ·
                                   vibe coding tools · certification
Claude Code SEO                  → SEO workflow · technical SEO audit · Search
                                   Console · Core Web Vitals · Shopify SEO ·
                                   website audit
Claude Code Shopify Development  → build a Shopify store · Shopify SEO · Core Web
                                   Vitals · accessibility · security · website audit
Claude Code Production           → website audit · security · accessibility ·
                                   Core Web Vitals · GitHub Actions · enterprise ·
                                   production CLAUDE.md · hooks
```

A guide has one primary pillar and may be listed on others as a reading
recommendation.

## 5. Learning paths

| Path | Sequence |
| --- | --- |
| Website development (9) | terminal setup → build a website → production CLAUDE.md → CLAUDE.md examples → prompts → skills → hooks → subagents → MCP |
| SEO (4) | SEO workflow → technical SEO audit → Search Console → Core Web Vitals |
| Production (5) | website audit → security audit → accessibility audit → GitHub Actions → enterprise |
| Shopify (2) | build a Shopify store → Shopify SEO |

Plugins, certification and the vibe-coding comparison are in no path. They are
reference pieces and forcing them into a sequence would misdescribe them.

## 6. Internal linking, measured

Sampled on the live site after the change:

| Page | Unique internal links | Guides | Hubs | Resources |
| --- | --- | --- | --- | --- |
| `/` | 40 | 17 | 4 | 9 |
| `/blogs/guides` | 42 | 23 | 4 | 5 |
| `/blogs/guides/claude-code-skills` | 30 | 6 | 4 | 6 |
| `/pages/claude-code-seo` | 27 | 6 | 4 | 8 |

Every sampled page reaches all four hubs in one hop, via the footer's Learn
column. A guide previously linked three guides — the three newest in the blog,
whatever they were about — and no hub.

## 7. Engagement features

- **Workflow selector** — 6 goals × 3 levels, 18 routes, every URL validated against the published manifests.
- **Guide library** — search + 4 filters, shareable querystring, empty state, reset.
- **Interactive checklists** — 140 items on the launch checklist; progress in `localStorage`, per page, never transmitted.
- **Copy components** — prompt / command / CLAUDE.md / code, with a live-region confirmation.
- **Contextual resources** — each guide offers the resource matching its intent, and each hub offers two.
- **Product walkthrough** — already existed as an honest no-video state showing the modules; its recording script gained an extended cut, thumbnail guidance and a transcript outline.

## 8. SEO

- Four hubs targeting `claude code web development`, `claude code seo`, `claude code shopify`, `claude code production workflow`.
- `CollectionPage` + `ItemList` on hubs, built from the same metafield the page renders, so markup and visible content cannot disagree. Three-level breadcrumbs matching the visible trail.
- Four meta descriptions and one title rewritten from real query data. No article body was rewritten: `gsc-page-intent.py` showed the gaps were in the snippets, not the content.
- Tag archives stay `noindex, follow`; filtered library views are client-side and generate no indexable URLs.
- Sitemap at 43 URLs, all 200 / self-canonical / indexable. New URLs submitted to IndexNow and Bing.

## 9. Analytics

26 events, listed in `docs/analytics/EVENTS.md`, all verified firing by driving
the real interaction and capturing what `Shopify.analytics.publish` received.
No personal data; checklist state never leaves the browser. They need a custom
pixel subscribed before anything is collected — that is a manual step.

## 10. Tests

`./tests/run-all.sh --with-render`: **45 passed, 0 failed.**

| Area | Result |
| --- | --- |
| Repo checks incl. 2 new validators | 14 passed |
| Browser behavioural (5 scripts, 79 assertions) | passed |
| Rendered a11y + overflow, 5 pages × 5 widths | 25 passed, all clean |
| SEO crawl of the live site | no findings |
| Sitemap | 43 URLs, 0 failures |
| Core Web Vitals (lab) | LCP 496–524 ms, CLS 0 on every page |

Every validator is control-tested: `validate-graph` 16 cases, `validate-selector`
10 cases, each proven to fire on a broken input and stay silent on a clean one.

### Defects found

Six, split evenly — **three introduced during this work and caught before
shipping**, and **three pre-existing**. Not one was found by reading code.

| # | Defect | Origin |
| --- | --- | --- |
| 1 | `article.handle` in Liquid is the qualified handle (`guides/x`, not `x`), so the first lookup rendered every hub page empty | introduced, caught |
| 2 | `display:grid` beats the UA `[hidden]` rule at any specificity — all three selector steps painted at once with their links focusable, and the library filter form was visible with JS off | introduced, caught |
| 3 | `sbs-inline-cta` was already the authored product aside in all 23 guides; the new navigation card collided with it | introduced, caught |
| 4 | The copy button appended itself inside the `<pre>` and read `textContent` at click time, so every copied block ended with "Copy" | pre-existing |
| 5 | `render-preview.py` raised on every run (Shopify's comment banner vs plain `json.load`), so the rendered a11y checks behind `--with-render` had never executed | pre-existing |
| 6 | With it running, it reported an unlabelled input and an empty button that do not exist live — it ignored the schema defaults Shopify falls back to | pre-existing, surfaced by fixing #5 |

Numbers 1 and 2 were only findable by asserting what the browser **paints**
rather than what the DOM attribute claims. The tests now assert paint.

## 11. Before / after

Only the before exists. `docs/analytics/BASELINE-2026-09-06.md` records what was
measured on the day this shipped: 3 clicks, 1,039 impressions, 0.29% CTR,
average position 55.5, and **7 of 125 queries in positions 4–20**. Engagement has
no before at all — the site had no analytics of its own until now. No after
figures are claimed.

## 12. Manual actions remaining

1. **Subscribe a custom pixel** to the events (Settings → Customer events), or they publish with no listener.
2. **Record the walkthrough video.** Script, shot list, extended cut, thumbnail and transcript outline are in `docs/growth/PRODUCT-DEMO-SCRIPT.md`. The section switches to a player automatically when the files are uploaded.
3. **Request Indexing** for the five new URLs in the Search Console UI. There is no supported API for it.
4. **Set the store contact email** in Shopify admin — no API mutation exists.
5. **Outreach.** The failure library and the starter kit are the assets worth pitching; `docs/seo/link-prospects.csv` has the tracker.
