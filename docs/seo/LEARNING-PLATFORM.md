# The learning platform architecture

What changed, why, and where each piece lives. This is the reference for anyone
adding a guide, a hub, or a learning path later.

## The shape

```
Homepage
  └─ workflow selector ──> guide ──> hub ──> next guide ──> resource ──> product
/blogs/guides (library: search + 4 filters)
  └─ hub ──> learning path ──> guide (prev/next) ──> related ──> resource
```

Before this, the blog was chronological and its "related articles" block listed
the three newest posts regardless of subject. Every relationship on the site is
now editorial and stored as data.

## Where the architecture lives

| File | Holds |
| --- | --- |
| `content/content-graph.json` | Pillars, learning paths, and per-guide topic / level / type / goal / related / resource |
| `content/workflow-selector.json` | The homepage selector's 18 recommendations |
| `content/pillars/*.html` | The four hubs' original editorial content |
| Shopify metafields, namespace `sbs` | What the theme actually reads at render time |

Nothing is duplicated between them. `scripts/publish-graph.py` writes the graph
into metafields as **bare handles only** — never titles or URLs — and the theme
resolves each handle against the live blog. A retitled guide therefore updates
everywhere at once and no metafield can hold a stale label.

## The four hubs

| Hub | URL | Guides | Path |
| --- | --- | --- | --- |
| Claude Code for Web Development | `/pages/claude-code-web-development` | 12 | 9 steps |
| Claude Code SEO | `/pages/claude-code-seo` | 6 | 4 steps |
| Claude Code Shopify Development | `/pages/claude-code-shopify` | 6 | 2 steps |
| Claude Code Production Engineering | `/pages/claude-code-production` | 8 | 5 steps |

A guide has exactly one **primary pillar** (its up-link) and appears in at most
one **learning path** (so prev/next is a single chain). It may be listed as a
cluster member on other hubs — that is a reading recommendation, not a second
parent. Three guides are in no path at all: plugins, certification and the vibe
coding comparison are reference pieces, and forcing them into a sequence would
be dishonest about what they are.

## Adding a guide

1. Publish it as usual (`content/articles.json`, `publish-articles.py`).
2. Add an entry to `content/content-graph.json`: pillar, topic, level, type,
   goal, 2–5 related handles, one resource.
3. Add its handle to that pillar's `cluster`, and to a path's `steps` if it
   belongs in a sequence.
4. `python3 scripts/validate-graph.py` — it will refuse anything that does not
   resolve, in either direction.
5. `python3 scripts/publish-graph.py --articles-only`.

The library's filter options are derived from what exists, so a new topic
appears in the dropdown automatically and a retired one disappears.

## Adding a hub

1. Add it to `pillars` in the graph, with `title`, `url`, `intent`, `cluster`,
   `resources`, `seoTitle`, `seoDescription`, `file`.
2. Write the editorial body into `content/pillars/<handle>.html`.
3. `python3 scripts/publish-pillars.py --with-graph`.
4. Add it to the footer's Learn column and to `blog.json`'s hub blocks.

Cross-links between hubs are derived, not stored — a fifth hub links itself to
the other four and them to it without anyone editing four files.

## What is validated, and how

Every check below is control-tested: it has been shown to fire on a deliberately
broken input and to stay silent on a clean one. A check that has never failed is
not evidence.

| Check | What it prevents |
| --- | --- |
| `validate-graph.py` (16 cases) | A handle that does not resolve — a dead link on a live page |
| `validate-selector.py` (10 cases) | An invented URL in the homepage router |
| `test-library-filter.js` (15) | Filters that do not filter; a filter form visible with JS off |
| `test-workflow-selector.js` (21) | A half-answered form guessing; hidden steps still focusable |
| `test-checklist.js` (16) | Progress that does not persist; a checklist that needs JS to tick |
| `test-copy-buttons.js` (14) | The button's own label ending up in the clipboard |
| `test-analytics-events.js` (13) | Events that do not fire; analytics breaking a page |

The browser tests sit behind `./tests/run-all.sh --with-render` because they
need Chrome and the network. A suite that fails when the machine is offline
stops being trusted.

## Deliberate constraints

**No faceted URLs.** Filtered views are client-side, the querystring is written
with `replaceState` for sharing, and `canonical_url` still points at the clean
`/blogs/guides`. Nothing new became indexable.

**No FAQ schema.** Several hubs answer questions in prose. Marking prose up as
an FAQ to chase a rich result describes the page as something it is not.

**Everything works without JavaScript.** The library shows all 23 guides and
hides its filter form; the selector hides its questions and shows a real hub
list; checklists tick and reset natively. That is also exactly what a crawler
receives.

**Two in-article cards, never three.** Guides already carry two authored product
asides. The navigation cards are capped at two, only appear in guides with six
or more sections, and can never point at the same guide twice — the first
related guide is very often also the next lesson, and showing it twice is the
repetition worth avoiding.
