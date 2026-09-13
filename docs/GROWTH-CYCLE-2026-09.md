# Growth implementation — September 2026

Engagement, SEO content and a second product. Implemented, live, tested.

## 1. Executive summary

Six things shipped:

- The homepage router became a **learning-path engine**: three questions, eleven seven-step roadmaps through real pages, with progress the visitor ticks off and returns to.
- **Sequential navigation** now runs through the guides: hub label, "Step N of M", previous/next, and an end-of-guide "continue your learning path" block chained from the graph.
- **Four free interactive tools** at `/pages/tools`, all producing a result before asking for anything.
- **A second product** — the $39 Claude Code SEO & Website Audit Toolkit — built as an actual downloadable bundle, not just a listing.
- **Four pillar guides**, 16,572 words, every volatile fact verified against primary sources.
- **Two platform hubs**, WordPress and Astro, taking the site to six.

## 2. Files

**Created.** `content/articles/24-27` (4 guides) · `content/pillars/claude-code-{wordpress,astro}.html` · `content/tools/` (5) · `content/products/seo-toolkit.html` · `product/Claude-Code-SEO-Website-Audit-Toolkit/` (55 files) · `theme/dev/sections/sbs-tool.liquid` · `theme/dev/snippets/sbs-field.liquid` · `theme/dev/templates/page.tool.json`, `page.tools.json`, `product.seo-toolkit.json` · `scripts/{publish-tools,publish-seo-toolkit-product,validate-toolkit,validate-tool-pages}.py` · `scripts/build-toolkit.sh` · `scripts/test-{tools,route-engine}.js`

**Rewritten.** `sbs-selector.liquid` (router → engine) · `sbs-article.liquid` (contextual CTA, continue block) · `scripts/validate-selector.py`

**Modified.** `sbs.js`, `sbs.css`, `sbs-product.liquid`, `sbs-footer.liquid`, both section groups, `index.json`, `blog.json`, `agents.md.liquid`, `content-graph.json`, `workflow-selector.json`, `articles.json`, `resources/_hub.html`, `generate-article-images.py`, `audit-storefront-claims.py`, `audit-agents-claims.py`, `verify-digital-delivery.py`, `validate-graph.py`, `publish-graph.py`, `tests/run-all.sh`

## 3. Engagement

### Learning-path engine

Three questions — goal (11), stage (5), experience (3). Stage decides which step is marked "start here", so somebody already live is not sent to the getting-started guide; earlier steps are dimmed rather than auto-ticked, because ticking them would claim progress nobody reported.

Progress persists in `localStorage` keyed `<goal>:<step>`, so several roadmaps hold progress at once and changing goal is not destructive. Mark complete, resume, reset, change goal. A shared URL beats saved state. 29 browser assertions.

### Sequential guide navigation

Hub label with "Step N of M", three-level breadcrumb, two in-article progression cards, previous/next, and an end-of-guide block showing **Next / Then / Going deeper**. "Then" is found by chaining through the next guide's own `next` metafield, so reordering a path updates it with no edit. It renders only where there is a genuine next step — a guide at the end of a path, or in no path, gets nothing invented.

### Four free tools

CLAUDE.md generator · SEO audit prompt generator · launch readiness score · website prompt builder. Everything runs in the browser; nothing typed is transmitted. **The test types a sentinel string into every field and searches every analytics payload for it**, so the privacy claim is asserted rather than stated. 39 assertions.

### Product walkthrough

Already existed as an honest no-video state and was left alone; the toolkit reuses the same section with its own eight steps. Its recording script gained an extended cut, thumbnail direction and a transcript outline in the previous cycle.

## 4. The SEO toolkit

| | |
| --- | --- |
| Title | Claude Code SEO & Website Audit Toolkit |
| Price | $39 USD, one payment |
| URL | `/products/claude-code-seo-website-audit-toolkit` |
| Files | 55 |
| Prompts | 20 |
| Modules | 14 |
| Templates / checklists | 4 / 3 |
| Words | 26,135 |
| Archive | 90,025 bytes |
| SHA-256 | `30849435bbc992faca442515c5f7a015fad6292664802d9b52c141a87c0f8e24` |
| Delivery | Shopify Digital Products app — **file not yet attached** |

Every quantity on the product page is read from the bundle at publish time; the publisher refuses to run if they disagree.

## 5. Articles

| Guide | Words | SEO title |
| --- | --- | --- |
| `/blogs/guides/claude-code-wordpress` | 4,676 | Claude Code WordPress Workflow |
| `/blogs/guides/claude-code-astro` | 4,020 | Claude Code Astro Workflow |
| `/blogs/guides/claude-code-vs-cursor-web-development` | 3,722 | Claude Code vs Cursor |
| `/blogs/guides/claude-code-github-actions-cloudflare` | 4,154 | Claude Code CI/CD With Cloudflare |

Four volatile facts were checked against primary sources rather than recalled, and two of them contradicted what I would otherwise have written: **Cloudflare now says to start new projects with Workers, not Pages**, and **Astro is on v7** with loaders required in `src/content.config.ts`. Current pricing for both Claude and Cursor was read from the vendors' own pages.

The comparison discloses the commercial interest in its first paragraph and publishes **no benchmark numbers**, because no controlled head-to-head was run.

## 6. Internal linking

Ten existing guides gained contextual links to the new ones. Both new hubs carry six-guide clusters. Every page reaches all six hubs in one hop through the footer. The tools are linked from all six hubs, the resources hub, the footer, and contextually from articles.

## 7. Technical SEO

- 55 sitemap URLs, all 200 / self-canonical / indexable.
- `CollectionPage` + `ItemList` on the two new hubs, built from the same metafield the page renders.
- `Product` schema on the toolkit reads price and currency from the variant.
- No FAQ schema anywhere, including on the product pages that have visible FAQs.
- Filtered library views stay client-side; no faceted URLs generated.
- Blog pagination verified: no "Older" link exists because 27 guides fit one page, and out-of-range pages are `noindex, follow` with distinct titles.

## 8. Analytics

29 events, all through Shopify's existing analytics. New this cycle: `route_started`, `route_goal_selected`, `route_stage_selected`, `route_level_selected`, `route_generated`, `route_step_clicked`, `route_step_completed`, `route_completed`, `route_reset`, `tool_started`, `tool_completed`, `tool_result_copied`, `tool_reset`, `learning_path_next_clicked`, `resource_cta_clicked`, `checklist_printed`.

Payloads carry an event name and a short label. Nothing typed into a tool is ever sent.

## 9. Accessibility

Every new page audited at 320, 375, 768, 1024 and 1440px: contrast, heading order, accessible names, alt text, tap targets, focus visibility and horizontal overflow. All clean.

One real defect found and fixed: the product page overflowed at 320px because `.sbs-bundle > *` was missing from the stylesheet's existing `min-width: 0` list. The homepage never showed it because `.sbs-hero` clips its overflow — the new page rendered the same tiles unclipped and exposed it.

## 10. Performance

No framework was added. The four tools, the roadmap engine and the checklists are vanilla JavaScript in the existing `sbs.js`. Every form and every roadmap panel is server-rendered and hidden, so revealing one causes no layout shift and no fetch.

## 11. Testing

`./tests/run-all.sh --with-render`: **47 passed, 0 failed.**

Repository checks include four new validators, each control-tested in both directions: `validate-toolkit.py` (8 cases), `validate-selector.py` (12), `validate-tool-pages.py` (2), plus the extended `validate-graph.py` (17).

Browser tests: route engine 29 assertions, tools 39, library 15, checklist 16, copy buttons 14, analytics events 13.

## 12. Manual actions

1. **Attach the toolkit's file in the Digital Products app, then place a real test order.** Until that happens the product is purchasable and would deliver nothing. `verify-digital-delivery.py` fails on this deliberately.
2. Record the walkthrough video — script, extended cut, thumbnail direction and transcript outline are ready.
3. Subscribe a custom pixel to the analytics events.
4. Request indexing for the new URLs in Search Console.
5. Set the store contact email in Shopify admin.

## 13. Next five

1. **Attach the delivery file.** Nothing else on this list matters while a customer can pay and receive nothing.
2. **Earn one external link.** With 90% of queries past position 40, authority is the binding constraint and no on-page work moves it.
3. **Record the walkthrough.** The infrastructure has been waiting for two cycles.
4. **Subscribe the pixel and let the events run for a month**, so the next cycle has an engagement baseline instead of none.
5. **Write the second WordPress and Astro guides.** Both hubs are foundations with one primary guide each; a second gives each a real learning path.
