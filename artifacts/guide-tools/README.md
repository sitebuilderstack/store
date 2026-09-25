# Guide tools — three Claude Artifacts

One interactive tool per article, published 24 September 2026. Each is a
self-contained page: the shared tokens, the markup and the logic are inlined at
build time, so a published artifact depends on nothing served beside it.

| Tool | Article it belongs to | Artifact |
| --- | --- | --- |
| `seo-review` | [Bulk edit Shopify SEO](https://sitebuilderstack.com/blogs/guides/bulk-edit-shopify-seo-claude-code) | <https://claude.ai/artifact/SZ9koPaqBPCxshyQ98vTmg> |
| `product-page` | [Shopify digital product page template](https://sitebuilderstack.com/blogs/guides/shopify-digital-product-page-template) | <https://claude.ai/artifact/G492gGa3dLDwBddzf9JQ3X> |
| `scope-builder` | [Website scope of work template](https://sitebuilderstack.com/blogs/guides/website-scope-of-work-template-claude-code) | <https://claude.ai/artifact/Vb6WURhumspfLWuHp4MueP> |
| `aeo-checker` | Answer engine readiness — no single article; pairs with the [technical SEO audit](https://sitebuilderstack.com/blogs/guides/claude-code-technical-seo-audit) | <https://claude.ai/artifact/WzATH5FnyueC52uoGDVLCc> |

**All four are shared with anyone who has the link**, confirmed by reading each
artifact's stored state on 25 September 2026. Sharing is done from the Share
control in each artifact's page header; nothing in this repository can change
it, so verify rather than assume before linking one from a published page — a
link to a private artifact 404s for every reader.

Each is linked from its own guide, and `docs/content/qa-guides-2026-09-24.py`
asserts that an article's off-domain links are sources, the store's own CDN, or
a named tool.

## Working on them

```
_tokens.css              the shared visual system (the storefront's own tokens)
<tool>/body.html         markup
<tool>/app.js            logic
<tool>/style.css         tool-specific layout (optional)
<tool>/index.html        GENERATED — the file that is published
<tool>/preview.html      GENERATED — index.html inside the runtime's shell, for tests
```

```bash
python3 build.py     # regenerate index.html and preview.html for every tool
```

Editing `index.html` directly is always wrong: the next build overwrites it.
Republish with the same file path to keep the URL.

## What they have in common

- **No network.** Verified: zero requests beyond the page itself. No analytics,
  no fonts, no CDN. Nothing a visitor types leaves the tab, and each page says
  so rather than implying it.
- **Nothing persisted.** State lives in memory for the life of the tab.
- **Each opens in a working state** — the worked example from its article is
  loaded, so the first frame shows what the tool does rather than empty boxes.
- **Copy always works; download is conditional.** `claude.use('downloads')`
  resolves only inside the claude.ai viewer, so the download button stays
  hidden elsewhere and the page explains why instead of failing silently.
- **One product each**, linked with fixed campaign parameters
  (`utm_source=claude_artifact`, `utm_medium=interactive_tool`, a campaign per
  tool) and no visitor data in any URL.

## Checks

```bash
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser node tests.js
```

**120/120** across four tools at 390, 768 and 1280px. Per tool: no
`html`/`head`/`body` wrapper; a title in the first 8 KB; no external script,
style, font or image; every *link* points at sitebuilderstack.com; fictional
example URLs appear as data and never as links; the correct product and
campaign tag; no credential-shaped strings; under the page-size limit; no
console errors; zero network requests; exactly one `h1`; opens in a working
state; the copy control works and reports success only after success; a refused
clipboard reports failure and offers selectable text; download hidden without
the capability, with the reason shown; the first control takes keyboard focus;
reset works; no horizontal overflow at any of the three widths.

The download **save** path can only run inside the claude.ai viewer and was not
exercised here; the absent-capability branch was.

## Why an artifact is not itself an AEO asset

Checked 25 September 2026, and it is the reason `aeo-checker` is a tool rather
than a piece of optimised content:

- `https://claude.ai/robots.txt` returns `Disallow: /` for `GPTBot`,
  `OAI-SearchBot`, `ChatGPT-User` and `Google-Extended`.
- An artifact URL returns **HTTP 403** behind a bot challenge to a plain client.

So an artifact cannot be crawled or cited by an answer engine. These tools earn
traffic by being **shared**, which is referral traffic, not organic search. Any
content meant to be cited has to live on sitebuilderstack.com, in HTML, on a
path AI crawlers are allowed to fetch.
