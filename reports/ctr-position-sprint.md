# CTR and average-position sprint

8 September 2026. Branch `feature/ctr-position-sprint`.

## 1. Executive summary

Four actions, all implemented and verified in production. The strategy was to
improve pages Google is already rewarding rather than publish competing content.

Two findings changed what the work turned out to be.

**The Organization logo was not missing — it was wrong.** The schema carried a
`logo` property pointing at `og-share.png`, a 1200×630 landscape social card
with marketing copy on it, as a bare string with no dimensions. That is a
correct Open Graph image and a wrong Organization logo, which is why audits
reported the property as absent. A real square logo now exists.

**Internal linking to the priority pages was already strong**, not weak. Before
this sprint: 12 inbound contextual links to the Shopify guide, 9 to GitHub
Actions, 18 to the SEO guide and 37 to Production CLAUDE.md, with varied
anchors. Adding "3–6 more" to each would have been the over-optimisation the
brief warns against. The work went where the imbalance actually was.

## 2. Metadata changes

| URL | Old title | New title | Old meta | New meta |
| --- | --- | --- | --- | --- |
| `/blogs/guides/build-shopify-store-with-claude-code` | Build a Shopify Store With Claude Code | **unchanged** | Connect Claude Code to Shopify and build a store with it: the theme workflow, Theme Check with JSON output, the Admin GraphQL API, and digital delivery. (152) | Build a production Shopify store with Claude Code: the theme workflow, Theme Check with JSON output, sections and schema, the Admin API and deployment. (151) |
| `/blogs/guides/claude-code-github-actions` | Claude Code GitHub Action | **Claude Code GitHub Actions: PR Reviews** | Using anthropics/claude-code-action: setup, interactive vs automation mode, three working workflows, inline PR review comments, and keeping the bill down. (154) | Use Claude Code with GitHub Actions for pull-request review: the workflow file, permissions and secrets, inline comments, security, and troubleshooting. (152) |

### Why the Shopify title was not changed

The requested wording, *"Build a Shopify Store With Claude Code: Complete 2026
Workflow"*, renders at **83 characters** once the site's ` – Site Builder Stack`
suffix is appended, against a 62-character limit the theme enforces because
Google truncates at roughly 600 CSS pixels. It would have been cut mid-phrase,
losing both "Workflow" and the brand.

Shorter variants including "2026" also overrun: *"Build a Shopify Store With
Claude Code 2026"* renders at 64. The current title renders at **59**, uses the
phrasing the measured queries actually contain — "how to have claude make a
shopify website", "claude store builder", "building storefront with claude
code" — and is on a page whose average position moved from ~61.6 to ~10.9 with
that title in place. The site's own Search Console report says of pages already
ranking: *protect rather than optimise*.

The "production", "workflow" and "2026-current" signals went into the
description and the body instead, where there is room.

The GitHub Actions title had room (25 characters) and was genuinely weak. The
new one pluralises to match the recorded query "claude code github actions" and
names the dominant intent, at 59 rendered.

### Metadata validation, on the rendered HTML

Both pages: exactly one `<title>`, one meta description, one canonical (self,
absolute), one `h1`, one `og:title`, one `og:description`, `twitter:card`
present, no `&amp;amp;` entities, no duplicated brand in the title.

## 3. Shopify article changes

Words: 6,900 → **7,325** (band 5,000–7,500).

| Added | What it covers |
| --- | --- |
| **The four Shopify surfaces** | A table separating Shopify CLI, Admin API, Storefront API and Liquid, with the wrong-tool case for each. The Storefront API was not mentioned anywhere before; it is what a session reaches for when told to "fetch products from the API", and it is the wrong answer on a themed store. |
| **The Theme Check loop** | The nine-step sequence: change → run with `--output json` → capture → **classify real versus false positive** → fix one → re-run → push to the development theme → check the rendered page at 375px → confirm schema settings still render. |
| **A classification prompt** | Naming this theme's two known false positives, so "zero offences" becomes "zero offences outside this known list". |

Theme Check coverage itself was added on 7 September and is unchanged: install
via the Shopify CLI, `--output json`, the real JSON shape, `--fail-level`,
`--init`, `--list`. Every flag was verified by running
`npx @shopify/cli@latest theme check --help`, and the JSON schema by running it
against this theme. No flag was invented.

## 4. GitHub Actions article changes

Words: 2,129 → **3,218**. Band raised 3,000 → 4,200 with the reason recorded in
`validate-articles.py`, and a "split it rather than raise this again" rule.

**Security — the section did not exist at all.** Zero mentions of
`pull_request_target`, forks or prompt injection, in a guide about running a
model over code strangers can write.

- `pull_request` versus `pull_request_target`, with the concrete takeover: a
  workflow that checks out `head.sha` under `pull_request_target` and runs
  `npm install` executes attacker code with your API key and a writable token.
- The rule: if the workflow checks out the PR's code, do not use
  `pull_request_target`. Split into two workflows joined by `workflow_run`.
- Least privilege, with an explicit job-level `permissions` block and why a
  review workflow does not need `contents: write`.
- **Prompt injection**, which has no setting that fixes it: the diff, title,
  description and comments are all attacker-controlled on a fork PR. Four
  mitigations, and a prompt that treats PR content as data — stated as raising
  the cost, not as a guarantee.
- Fork PRs: secrets are absent by design, the action fails rather than
  reviewing, and that is the boundary working.

**Troubleshooting** went from four cases to nine: workflow never appears
(YAML/default branch/tabs), permission denied (three distinct causes), secret
unavailable (arrives as an empty string, so the error surfaces elsewhere),
duplicate comments on every push, and API failures split into auth, rate limit
and context length.

## 5. Internal links added

| Source | Destination | Anchor |
| --- | --- | --- |
| `production-claude-md-web-development` | `claude-code-github-actions` | runs Claude Code in GitHub Actions |
| `claude-code-technical-seo-audit` | `/products/claude-code-seo-website-audit-toolkit` | SEO & Website Audit Toolkit |
| `google-search-console-claude-code` | `/products/claude-code-seo-website-audit-toolkit` | SEO & Website Audit Toolkit |
| `claude-code-website-audit` | `/pages/build-rank-convert` | Build, Rank, Convert |
| `how-to-build-a-website-with-claude-code` | `/pages/build-rank-convert` | The lifecycle page |

Five links, not twenty. Measured inbound counts before the sprint were 12, 9, 18
and 37 for the four priority pages — the brief's premise that they needed 3–6
more each did not match the site.

The one genuine gap was that **Production CLAUDE.md, the best-performing page,
did not link to GitHub Actions** while already linking to Shopify and SEO. That
is now fixed, and it is the only change to that article.

The real imbalance was commercial: contextual body links ran 45 to the Launch
System against 2 for the SEO toolkit. The four product links above correct that
by intent rather than by volume.

**The validator caught over-linking.** Two guides briefly reached four product
CTAs against a 2–3 target; the direct bundle links were removed and the
lifecycle-page links kept, since that page routes to the right product rather
than pushing the most expensive one.

## 6. Structured data

**File changed:** `theme/dev/snippets/sbs-schema.liquid`, plus a new
`logo_image` setting in `config/settings_schema.json` and `settings_data.json`.

**New asset:** `assets/logo.png`, 600×600, generated by
`scripts/generate-brand-assets.py` from the same mark the header uses. Square,
on the brand ink rather than transparent, with margins that survive a circle
crop. Uploaded to the Shopify CDN.

Before: `"logo": "…/og-share.png?width=1200"` — a bare string, landscape, a
social card.

After:

```json
"logo": {
  "@type": "ImageObject",
  "url": "https://sitebuilderstack.com/cdn/shop/files/logo.png?v=1788910863&width=600",
  "width": 600,
  "height": 600,
  "caption": "Site Builder Stack"
}
```

The height is **computed** from the source image, not hard-coded. The first
version hard-coded 600×600, which was correct for the square logo and a false
claim for the landscape fallback — the kind of error invisible until something
consumes the dimensions.

`logo_image` is a separate setting from `share_image` so a social card and a
logo cannot be confused again. It falls back to `share_image` rather than
emitting nothing, and the fallback is visible in the template rather than
silent.

**No duplicate Organization.** Exactly one node, on the homepage; article
`publisher` references it by `@id` rather than repeating it. Verified across
four page types. Product, BlogPosting, BreadcrumbList, FAQPage, WebSite, Person
and CollectionPage all still parse — 0 invalid JSON-LD.

## 7. Crawl and indexing

Every priority URL: **200, self-canonical, indexable**, present in Shopify's
generated sitemap. `validate-sitemap.py`: **0 failures**. Nothing was written to
Shopify's sitemap.

`robots.txt` blocks only parameterised blog URLs (`/blogs/*+*` and its encodings),
not the guides or the products.

Rendered inbound links per product, measured on live pages:

| Page | Launch | SEO | Conversion | Stack |
| --- | ---: | ---: | ---: | ---: |
| Homepage | 12 | 6 | 3 | 3 |
| `/blogs/guides` | 2 | 2 | 2 | 2 |
| `/collections/all` | 3 | 3 | 3 | 3 |
| `/pages/build-rank-convert` | 7 | 7 | 7 | 7 |
| A representative guide | 5 | 2 | 2 | 3 |

All four are reachable from the homepage, the guide index, the collection, the
lifecycle hub and every guide. **The constraint is crawl budget on a
fourteen-day-old domain, not missing links** — 18 of 62 URLs are indexed and
five pages published on 7 September moved that count by zero.

## 8. Testing results

Executed:

```
./tests/run-all.sh                    27 passed, 0 failed
scripts/validate-articles.py          0 failures, 0 warnings
scripts/validate-graph.py             0 failures
scripts/validate-sitemap.py           0 failures
```

Structured data validated by parsing the served HTML on four page types: 0
invalid, 1 Organization node total.

Metadata validated on the rendered HTML of both modified guides, not the source.

Accessibility and overflow on both modified guides at 320, 375 and 1280px:
**clean** — no horizontal overflow from the new tables, code blocks or lists.

`shopify theme check` was run against `theme/dev` on 7 September to verify the
JSON output shape documented in the Shopify guide. It reports 118 offences on
that partial checkout, of which the errors are `MissingTemplate` for vendor
files deliberately kept out of version control and one `LiquidHTMLSyntaxError`
on a valid tag built across a loop boundary — both confirmed individually as
false positives, and both now named in the article as the known list.

## 9. Search Console handoff

Requesting indexing does not guarantee indexation.

| URL | Reason | Content | Links | Metadata |
| --- | --- | --- | --- | --- |
| `/blogs/guides/build-shopify-store-with-claude-code` | Position ~10.9, 65 impressions, 0 clicks | **Yes** | Yes | **Description** |
| `/blogs/guides/claude-code-github-actions` | Position ~12.5, 94 impressions, 0 clicks | **Yes** | Yes | **Title + description** |
| `/blogs/guides/production-claude-md-web-development` | Position ~6.3, protect | One added paragraph | **Yes** | No |
| `/blogs/guides/claude-code-technical-seo-audit` | Product link added | Minor | Yes | No |
| `/blogs/guides/google-search-console-claude-code` | Product link added | Minor | Yes | No |
| `/blogs/guides/claude-code-website-audit` | Lifecycle link added | Minor | Yes | No |
| `/blogs/guides/how-to-build-a-website-with-claude-code` | Lifecycle link added | Minor | Yes | No |
| `/products/claude-code-website-launch-system` | Reported URL unknown to Google | No | Yes | No |
| `/products/claude-code-seo-website-audit-toolkit` | Discovered, not indexed | No | **Yes** | No |
| `/products/claude-code-conversion-revenue-optimization-toolkit` | Discovered, not indexed | No | Yes | No |
| `/products/complete-site-builder-stack` | Reported URL unknown to Google | No | Yes | No |

All eleven were submitted to IndexNow, which covers Bing and Yandex but not
Google. Google requires manual inspection in Search Console.

## 10. Remaining issues

- **The Shopify title still lacks a year signal.** Not solvable within a
  62-character budget that includes a 21-character brand suffix. Shortening the
  suffix sitewide would free the room and is a larger decision than this sprint.
- **Indexation is the binding constraint**, not metadata. 18 of 62 URLs
  indexed. Metadata changes cannot help a URL Google has not fetched.
- Unchanged from previous cycles: product archives are not attached in the
  digital-delivery app, the custom pixel is not installed, and no walkthrough
  video exists.
