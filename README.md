# Site Builder Stack

The source of [sitebuilderstack.com](https://sitebuilderstack.com) — a Shopify store
selling four digital products, published as a worked example of building and running
a site with Claude Code.

The products are **The Claude Code Website Launch System** ($19.99), the **SEO & Website
Audit Toolkit** ($19.99), the **Conversion & Revenue Optimization Toolkit** ($19.99) and
the **Website Operations & Maintenance System** ($39.99) — build the site, get it found,
turn the traffic into revenue, then keep it running. The first three are also sold
together as the **Complete Site Builder Stack** ($39.99), which is the same three
downloads on one order rather than a separate product; the Operations System is sold
on its own.

The methodology they sell is [published in full and free to
read](https://sitebuilderstack.com/blogs/guides): 27 guides, plus two complete
workflows lifted whole out of the paid toolkits. This repository is the machinery
underneath.

## What is worth looking at

If you are here from a guide, these are the parts that carry their weight:

| | |
| --- | --- |
| [`github/claude-code-website-starter-kit/`](github/claude-code-website-starter-kit) | A `CLAUDE.md` starter, four production checklists, and five installable Claude Code skills. MIT, free for client work |
| [`scripts/`](scripts) | The audit tooling: site-wide SEO, index coverage, rendered accessibility, Core Web Vitals, link crawling, Search Console analysis |
| [`resources/`](resources) | The free checklists in Markdown, the source for the pages on the site |
| [`content/articles/`](content/articles) | The 23 guides, as authored |
| [`docs/seo/`](docs/seo) | What was measured and decided, including the things that went wrong |

### The scripts are the interesting part

Most of them exist because something was reported as working when it was not. Four
separate checks on this project passed on exactly the condition they existed to catch —
a link crawler that reported "0 broken links" across a run where nine of twenty-eight
pages returned 429, a checkout check that read `innerText` for wording that only appears
in a `placeholder`. The
[case study](https://sitebuilderstack.com/pages/case-study) tells that story.

So every check here is control-tested in both directions, and several carry a
`--self-test` that proves each rule can still go red:

```bash
python3 scripts/audit-seo-site.py --self-test   # 11 rules, each on a crafted failure
./tests/run-all.sh                              # the whole suite
```

## Layout

```text
theme/dev/          the storefront source of truth — layouts, sections, snippets, templates
content/            the 23 guides and the hand-authored pages, as published
resources/          the five free checklists, in Markdown
github/             the starter kit, published standalone at github.com/sitebuilderstack/sitebuilderstack_store
scripts/            build, validation, audit and Shopify Admin API tooling
docs/               architecture, release process, and the SEO record
brand/              generated article images and diagrams
tests/              the suite
```

## Working on it

```bash
./tests/run-all.sh                                  # everything
python3 scripts/validate-articles.py                # anchors, links, metadata, hygiene
python3 scripts/audit-seo-site.py                   # crawl the live site
python3 scripts/gsc-opportunities.py --days 28      # Search Console, tiered
python3 scripts/index-coverage.py                   # every sitemap URL and its state

# push theme changes — never to the live theme without SBS_ALLOW_LIVE=1
python3 scripts/theme_push.py <themeId> theme/dev <path> [...]
```

Credentials are read at runtime from paths outside this repository and are never
printed, logged, or committed. `scripts/shopify_api.py` documents the contract, and the
suite fails if a secret ever enters the tree.

## What is not here

**The product source.** `product/Claude-Code-Website-Launch-System/` — 113 files, 17
modules, 100 prompts — is the thing customers pay for and is excluded from this public
mirror. So is the email-gated `freebie/` and the built `dist/`.

Everything else is here, including the parts that are unflattering.

## Independence notice

Site Builder Stack is an independent project and is not affiliated with, sponsored by,
or endorsed by Anthropic. "Claude" and "Claude Code" are product names and trademarks of
Anthropic, PBC, referenced here only to describe compatibility.

The purchased ONE Shopify theme is not redistributed here; only the custom layer built
on top of it is.

## Licence

The starter kit in `github/` is MIT — see its own `LICENSE`.

The rest of this repository is published to be read, not reused wholesale: the guides,
brand assets and storefront copy are © James Joyner IV. The scripts are free to adapt.
