# Three guides — publication handoff, 24 September 2026

**Status: PUBLISHED 24 September 2026**, on the owner's instruction, after the
drafts were reviewed. Inbound links released and the URLs submitted to IndexNow. The sample resources and cover images *are* live on the Shopify CDN,
because a draft cannot be reviewed against a download that does not exist yet.

Publication was not authorised for this work, and writing access is not
permission to publish. The exact command to publish is in §8.

---

## 1. The three articles

| Article | Primary keyword | URL (on publication) | Status | Product | Free resource | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| How to Bulk Edit Shopify SEO Titles and Meta Descriptions With Claude Code | bulk edit Shopify SEO titles and meta descriptions | `/blogs/guides/bulk-edit-shopify-seo-claude-code` | **Live** (id 636223422756) | [Shopify Automation & Admin API Toolkit](/products/claude-code-shopify-automation-admin-api-toolkit) | `shopify-seo-review-worksheet.zip` | Passed |
| Shopify Digital Product Page Template: Copy, Layout, and Claude Code Prompts | Shopify digital product page template | `/blogs/guides/shopify-digital-product-page-template` | **Live** (id 636223455524) | [Conversion & Revenue Optimization Toolkit](/products/claude-code-conversion-revenue-optimization-toolkit) | `digital-product-page-template.zip` | Passed |
| Website Scope of Work Template: Turn a Client Brief Into a Clear Plan With Claude Code | website scope of work template | `/blogs/guides/website-scope-of-work-template-claude-code` | **Live** (id 636223488292) | [Agency & Client Delivery System](/products/claude-code-agency-client-delivery-system) | `website-scope-of-work-kit.zip` | Passed |

All three draft URLs return **404** today, verified. They are correctly absent
from the public blog and the sitemap.

### Word counts

Prose, excluding the copy-ready prompts and reference tables the brief required:

| Article | Prose | Prompts/code | Tables | Total |
| --- | --- | --- | --- | --- |
| Bulk Shopify SEO | 2,169 | 785 | 696 | 3,650 |
| Digital product page | 1,700 | 477 | 399 | 2,576 |
| Scope of work | 1,805 | 597 | 523 | 2,925 |

Prose sits inside the 1,600–2,600 editorial range in all three. The totals are
higher because a copyable prompt is reference material, not padding.

## 2. Duplication decision

Checked before writing. Two existing guides share keywords with article 1:

- **`shopify-seo-with-claude-code`** (2,570 words) — covers what the SEO fields
  are and Shopify-specific traps. **Zero** occurrences of "bulk"; no
  export/review/apply workflow.
- **`shopify-admin-api-claude-code`** (2,384 words) — covers API mechanics:
  clients, `userErrors`, metafields, rate limits. Two passing mentions of
  "bulk"; no SEO metadata workflow.

Neither satisfies the narrow intent "bulk edit SEO titles and meta
descriptions", so article 1 is a new canonical rather than a revision, and it
links to both as supporting guides. Articles 2 and 3 have no existing
counterpart at all — there was no scoping or client-delivery article on the
blog. **No existing guide was renamed, retitled or removed.**

## 3. What was verified, and how

| Claim | How |
| --- | --- |
| `ProductInput` has separate `seo`, `title`, `handle`, `descriptionHtml` fields; `SEOInput` has exactly `title` and `description` | GraphQL introspection against the live Admin API, version 2025-07 |
| The export shown in article 1 | A real read-only query against this store, 24 Sep 2026. No writes. |
| Legacy custom apps cannot be created after 1 Jan 2026; existing ones keep working; new ones go through the Dev Dashboard | [Shopify changelog](https://changelog.shopify.com/posts/legacy-custom-apps-can-t-be-created-after-january-1-2026), quoted verbatim, fetched 24 Sep 2026 |
| Google does not use the meta description verbatim; no length limit but snippets are truncated to device width | [Google — snippets](https://developers.google.com/search/docs/appearance/snippet), quoted verbatim, fetched 24 Sep 2026 |
| The before/after in article 2 | `docs/product-pages/backup-2026-09-24/` (captured before) versus the live page (after), same day |
| The three products' names, status and paths | Fetched by the product IDs given in the brief |

**Not verified, and labelled as such in the articles:**

- No write to a live product was performed to demonstrate article 1. The apply
  step is instructional; the export step is real. The article says so.
- The Harbourline Physiotherapy project in article 3 is **fictional** and is
  labelled as such in the article, in all four kit documents, and in the kit
  README. The effort figures are invented and are stated not to be market rates.
- The before/after in article 2 is an **implemented change with no measured
  result.** No conversion data exists and none is claimed.
- No search-volume, keyword-difficulty, ranking or traffic figure appears
  anywhere. No Search Console export was used; the supplied keywords were
  treated as editorial targets.

## 4. Free resources

Built from `downloads/` by `scripts/build-downloads.py` (added to its `KITS`
list) and uploaded with `scripts/upload-files.py --allow-archive`.

| Archive | Contents | CDN | Verified |
| --- | --- | --- | --- |
| `shopify-seo-review-worksheet.zip` | blank CSV, 5-row worked example, README | 3,891 bytes | 200, `application/zip` |
| `digital-product-page-template.zip` | copy template, review checklist, README | 7,360 bytes | 200, `application/zip` |
| `website-scope-of-work-kit.zip` | template, brief, completed scope, change request, README | 12,717 bytes | 200, `application/zip` |

Checked: no paid product content, no credential-shaped strings, every CSV field
quoted, UTF-8, and no cell beginning `=`, `+`, `-` or `@`. No email gate on any
of them.

The four scope documents were cross-checked for internal consistency: nine
pages in both the inventory and the deliverables table, requirements F1–F7
present, two review rounds, and the change request citing F7, the nine-page
inventory and assumption A1 by name.

## 5. Cover images

Three new motifs added to `scripts/generate-article-images.py`, matching the
existing visual system (dark ground, grid, accent rail, eyebrow, title,
kicker). 1200×630, distinct accent per article, each motif drawn from its own
subject — a review table with decisions, a product page as stacked blocks, a
two-column in/out scope split. Alt text describes what the image shows.

## 6. Internal links

**Outbound, live in the drafts** — every destination returned 200:

- Article 1 → the Shopify Automation toolkit, `shopify-seo-with-claude-code`, `shopify-admin-api-claude-code`
- Article 2 → the CRO toolkit, the Launch System (minor alternative), `shopify-conversion-audit-claude-code`, `claude-code-cro-prompts`
- Article 3 → the Agency system, `/pages/team-licenses` (secondary), `claude-code-website-audit`, `production-claude-md-web-development`

No internal UTM parameters. The three articles are **not** cross-linked to each
other; they serve different readers and forcing it would not help anyone.

**Inbound, STAGED and not applied** — `docs/content/staged-inbound-links-2026-09-24.py`

Four one-sentence additions to published articles. The script **refuses to
apply while any target is still a draft**, because those links would 404. Run
it after publication.

## 7. Measurement

No new analytics provider and no duplicated events. The existing theme already
fires `article_viewed`, copy-button events via `data-sbs-copy`, and
`product_cta_clicked` with a placement — the three drafts use the existing
`<pre data-sbs-copy="prompt">` and `sbs-inline-cta` conventions, so they
inherit that instrumentation with nothing added.

**The standing gap is unchanged and worth restating:** the store publishes
custom events and `webPixel` still returns *"No web pixel was found for this
app."* Until a pixel exists, none of these events is collected. Article-level
engagement is therefore **not measurable today**, and no baseline is claimed.

What *is* measurable now, after publication, without any new instrumentation:

- Impressions, clicks and CTR per article and per query — Search Console
- Sessions and landing pages — Shopify Analytics and Plausible
- Product page sessions from a blog referrer — Shopify Analytics
- Orders — Shopify, which is the only authoritative source for a purchase

A sample-link click is not a completed download, and a product click is not a
purchase. Neither should be reported as the other.

## 8. Published — what was run

```bash
python3 scripts/publish-articles.py \
  bulk-edit-shopify-seo-claude-code \
  shopify-digital-product-page-template \
  website-scope-of-work-template-claude-code
```

Then, in order — all three completed:

```bash
# 1. confirm the three URLs are live and render
python3 docs/content/qa-guides-2026-09-24.py --live

# 2. release the staged inbound links (refuses if anything is still a draft)
python3 docs/content/staged-inbound-links-2026-09-24.py --apply

# 3. submit to IndexNow — submission is not indexing, and neither is a promise
python3 scripts/indexnow-submit.py
```

## 9. Rollback

| Changed | Restore |
| --- | --- |
| Three new draft articles | Delete them in the admin, or `articleDelete` by the ids in §1. Nothing else referenced them. |
| `content/articles.json` | Three appended entries; `git revert` the commit. |
| `scripts/publish-articles.py` | Gained a `--draft` flag. Default behaviour without the flag is unchanged. |
| `scripts/build-downloads.py` | Three names appended to `KITS`. |
| `scripts/generate-article-images.py` | Three motifs and three specs appended. |
| Six CDN files | Delete in Shopify admin → Content → Files if the articles are abandoned. |
| Published articles | **None were modified.** The inbound links are staged, not applied. |

## 10. Remaining actions

1. ~~Publish.~~ **Done, 24 September 2026.**
2. ~~Release the staged inbound links.~~ **Done — four applied, verified in the
   live bodies.**
3. **Decide the artifact sharing.** All three tools are private. Sharing is done
   from each artifact's Share control; nothing here can change it.
4. **The pixel**, still, if article engagement is ever to be measured.
