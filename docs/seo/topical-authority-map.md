# Topical authority map

Every published guide, its cluster, and how it is linked. Generated from the real
internal link graph by `scripts/topical-map.py`, which reads the article bodies rather
than a hand-kept list — so if this document and the site disagree, the script is right
and this file is stale.

Regenerate the table with:

```bash
python3 scripts/topical-map.py
```

Last regenerated: 1 September 2026, against 19 published guides.

## Clusters

Six clusters. Four of them are commercial — they map onto what the product is for, and
each has a pillar with supporting guides beneath it. Two are not, and are honestly
modelled as peer sets rather than being given an invented hierarchy.

| Cluster | Pillar | Supporting | Commercial |
| --- | --- | --- | --- |
| Website Development | `how-to-build-a-website-with-claude-code` | prompts, terminal setup, website audit | yes |
| SEO | `claude-code-seo-website-optimization` | technical SEO audit | yes |
| CLAUDE.md | `production-claude-md-web-development` | CLAUDE.md examples | yes |
| Shopify | `build-shopify-store-with-claude-code` | Shopify SEO | yes |
| Deployment & Workflow | `claude-code-github-actions` | enterprise | partly |
| Extensibility | *(peer set)* | subagents, skills, plugins, MCP, hooks | no |
| Standalone | *(none)* | certification, vibe coding tools | no |

**Why Extensibility has no pillar.** The five articles were written to cross-reference
each other, and none is the entry point — a reader arrives at hooks or at MCP directly
from search, not by descending from a hub. Declaring one of them the pillar would invent
a hierarchy the content does not have, and would produce permanent "missing link up"
warnings that mean nothing. The script models this explicitly (`PILLARS[...] = None`)
rather than by suppressing the warning.

## The link graph

```
handle                                         cluster                 in out flags
----------------------------------------------------------------------------------------------------
production-claude-md-web-development           CLAUDE.md               18   7 PILLAR
claude-md-examples-web-development             CLAUDE.md                4   5 

claude-code-github-actions                     Deployment & Workflow    7   7 PILLAR
claude-code-enterprise                         Deployment & Workflow    6   9 

claude-code-hooks                              Extensibility            6   9 peer
claude-code-mcp                                Extensibility            4   9 peer
claude-code-plugins                            Extensibility            9   7 peer
claude-code-skills                             Extensibility           13   6 peer
claude-code-subagents                          Extensibility           10   8 peer

claude-code-seo-website-optimization           SEO                      8   8 PILLAR
claude-code-technical-seo-audit                SEO                      3   5 

build-shopify-store-with-claude-code           Shopify                  7   7 PILLAR
shopify-seo-with-claude-code                   Shopify                  3   5 

claude-code-certification                      Standalone               2   7 peer
vibe-coding-tools                              Standalone               3   7 peer

how-to-build-a-website-with-claude-code        Website Development     15   9 PILLAR
best-claude-code-prompts-for-web-development   Website Development     14   5 
claude-code-terminal-setup                     Website Development      3  10 
claude-code-website-audit                      Website Development      3   8
```

`in` and `out` count distinct guide-to-guide links in the article bodies, excluding
links inside `<pre>` blocks and self-links. No article is an orphan; every supporting
guide links up to its pillar and is linked down from it.

## Per-article detail

| URL | Primary topic | Target intent | Cluster | Role |
| --- | --- | --- | --- | --- |
| `/blogs/guides/how-to-build-a-website-with-claude-code` | End-to-end build workflow | how to build a website with claude code | Website Development | Pillar |
| `/blogs/guides/best-claude-code-prompts-for-web-development` | Prompt patterns | claude code prompts | Website Development | Supporting |
| `/blogs/guides/claude-code-terminal-setup` | Install and first week | claude code getting started | Website Development | Supporting |
| `/blogs/guides/claude-code-website-audit` | Auditing a live site | claude code website audit | Website Development | Supporting (new) |
| `/blogs/guides/claude-code-seo-website-optimization` | What to check, and why | claude code seo | SEO | Pillar |
| `/blogs/guides/claude-code-technical-seo-audit` | Running the audit, and proving it ran | claude code technical seo audit | SEO | Supporting (new) |
| `/blogs/guides/production-claude-md-web-development` | Principles and structure | production claude.md | CLAUDE.md | Pillar |
| `/blogs/guides/claude-md-examples-web-development` | Four filled-in files | claude.md examples | CLAUDE.md | Supporting (new) |
| `/blogs/guides/build-shopify-store-with-claude-code` | Building the store | build shopify store with claude code | Shopify | Pillar |
| `/blogs/guides/shopify-seo-with-claude-code` | Storefront SEO layer | shopify claude code seo | Shopify | Supporting (new) |
| `/blogs/guides/claude-code-github-actions` | CI and PR review | claude code github actions | Deployment | Pillar |
| `/blogs/guides/claude-code-enterprise` | Team rollout and policy | claude code enterprise | Deployment | Supporting |
| `/blogs/guides/claude-code-subagents` | Isolated context and tools | claude code subagents | Extensibility | Peer |
| `/blogs/guides/claude-code-skills` | Reusable procedures | claude code skills | Extensibility | Peer |
| `/blogs/guides/claude-code-plugins` | Packaging and distribution | claude code plugins | Extensibility | Peer |
| `/blogs/guides/claude-code-mcp` | External tool connections | claude code mcp | Extensibility | Peer |
| `/blogs/guides/claude-code-hooks` | Lifecycle enforcement | claude code hooks | Extensibility | Peer |
| `/blogs/guides/claude-code-certification` | Whether one exists | claude code certification | Standalone | Peer |
| `/blogs/guides/vibe-coding-tools` | Tool landscape | vibe coding tools | Standalone | Peer |

## Free resource pages

Not part of the blog cluster. These are reference artefacts rather than guides, and they
target list and template intent rather than how-to intent.

| URL | Intent | Paired guide |
| --- | --- | --- |
| `/pages/resources` | free claude code resources | — |
| `/pages/production-claude-md-starter` | claude.md template | `production-claude-md-web-development` |
| `/pages/claude-code-launch-checklist` | website launch checklist | `how-to-build-a-website-with-claude-code` |
| `/pages/claude-code-seo-checklist` | seo checklist | `claude-code-seo-website-optimization` |
| `/pages/claude-code-security-checklist` | website security checklist | `claude-code-enterprise` |
| `/pages/claude-code-website-audit-checklist` | website audit checklist | `claude-code-website-audit` |

## Cannibalisation review

Checked before publishing each of the four new guides. Two required a deliberate
decision and one required changing the plan.

### 1. Technical SEO audit vs. the SEO pillar — **plan changed**

The guide was specified as "Claude Code Technical SEO Audit: Complete Workflow" covering
crawling, indexing, canonicals, metadata, sitemap, robots, structured data, internal
links, redirects, Core Web Vitals, Search Console and Bing Webmaster Tools.

The SEO pillar already covers all of those, in exactly that dependency order, across
thirteen numbered sections. Publishing the guide as specified would have produced two
pages competing for one intent — the failure mode the whole review exists to prevent.

**Decision: re-angle rather than duplicate.** The pillar keeps *what to check and why*.
The new guide covers *execution and proof*: writing checks that are capable of failing,
the four false passes this build produced and what caused each, turning findings into a
diff, and what the three submission systems actually do. Roughly 80% of its content does
not appear in the pillar at all.

The two link to each other with anchor text that states the split explicitly ("This
guide covers what to check and why. For the execution … read …"), so the distinction is
visible to a reader and to a crawler.

### 2. Website audit guide vs. the website audit checklist page — **kept, differentiated**

Both were created in this sprint, which made the risk acute.

- `/pages/claude-code-website-audit-checklist` is the **artefact**: a list to work
  through, downloadable as Markdown, targeting "website audit checklist".
- `/blogs/guides/claude-code-website-audit` is the **method**: four passes in a
  deliberate order, prompts that produce evidence, a severity scale, and five real
  findings, targeting "claude code website audit".

They cross-link with explicit framing ("Read this for how to run an audit; open that for
what to check"). If Search Console later shows them trading positions for one query, the
correct fix is to merge them, not to add a third page.

### 3. CLAUDE.md examples vs. the CLAUDE.md pillar and the starter page — **kept**

The pillar contains one complete template and teaches the principles. The starter page
is a single generic blank file. The examples article is four **filled-in** files for
named project shapes, which is what "CLAUDE.md examples" as a query actually wants —
a template full of angle brackets does not satisfy it. The article says this in its
opening paragraph so the difference is explicit rather than implied.

### 4. Shopify SEO vs. both pillars — **kept, low risk**

The Shopify pillar has one section on SEO out of twenty-three; the SEO pillar is
platform-independent. The new guide is Shopify-specific throughout — measured canonical
behaviour for five URL forms, SEO metafields, the homepage title fallback, the thin pages
Shopify generates, and Merchant Center eligibility for a digital product. Little overlap
with either.

## Gaps not filled in this sprint

Deliberately left. Each would be one page, not a batch, and only when there is something
first-hand to say:

| Gap | Query shape | Why not yet |
| --- | --- | --- |
| Getting a new site indexed | "how long does google take to index" | Needs this site's own indexing timeline as evidence; that data is still accumulating |
| Claude Code vs. other assistants | comparison intent | Cannot be written honestly without sustained use of the alternatives |
| Accessibility with Claude Code | "claude code accessibility" | Real material exists (the invisible CTA, the target-size work) but it is currently spread across three guides |
| Cost and token management | "claude code cost" | Would need real usage figures, which are not published |
| Migrating an existing site | "migrate website with claude code" | No first-hand migration to draw on |

## Cannibalisation monitoring

Once Search Console has query data, the check is: for each target intent, run
`site:sitebuilderstack.com <query>` and confirm one clear winner, then compare against
the Performance report for two URLs alternating on the same query. Two pages swapping
positions is the signal to merge, not to optimise both.
