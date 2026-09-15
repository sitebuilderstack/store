# Content cluster map

Every published guide and free resource, its cluster, and how it is linked.
Generated from the real internal link graph by `scripts/topical-map.py` — if this file
and the site disagree, the script is right and this file is stale.

```bash
python3 scripts/topical-map.py
```

Last regenerated: 3 September 2026, against **23 published guides** and 5 free resources.

## Structure

```
                     CLAUDE CODE WEBSITE DEVELOPMENT
                                  │
                    How to Build a Website With Claude Code
                                  │
   ┌────────────┬─────────────────┼──────────────────┬─────────────┐
   │            │                 │                  │             │
Security     Performance     Accessibility        Website        Prompts /
 Audit      (Core Web Vitals)     Audit            Audit        Terminal setup
   │            │                 │                  │
   └────────────┴────────┬────────┴──────────────────┘
                         │
                   Technical SEO Audit ──── Claude Code SEO (pillar)
                         │                          │
                         └──── Google Search Console Workflow ────┘
```

The three specialist audits are siblings under the build pillar and all feed the general
website audit. The Search Console workflow sits at the end of the SEO chain because it is
the only one that operates on data the site produced rather than on the site itself.

## Clusters

| Cluster | Pillar | Supporting |
| --- | --- | --- |
| Website Development | `how-to-build-a-website-with-claude-code` | prompts, terminal setup, website audit, **security audit**, **performance**, **accessibility** |
| SEO | `claude-code-seo-website-optimization` | technical SEO audit, **Google Search Console** |
| CLAUDE.md | `production-claude-md-web-development` | CLAUDE.md examples |
| Shopify | `build-shopify-store-with-claude-code` | Shopify SEO |
| Deployment & Workflow | `claude-code-github-actions` | enterprise |
| Extensibility | *(peer set — no pillar)* | subagents, skills, plugins, MCP, hooks |
| Standalone | *(none)* | certification, vibe coding tools |

**Why Extensibility has no pillar.** Those five were written to cross-reference each
other and none is the entry point — readers arrive at hooks or MCP directly from search,
not by descending from a hub. Declaring one the pillar would invent a hierarchy the
content does not have, and would generate permanent "missing link up" warnings that mean
nothing. The script models this explicitly rather than suppressing the warning.

## The link graph

```
handle                                         cluster                 in out flags
----------------------------------------------------------------------------------------------------
production-claude-md-web-development           CLAUDE.md               20   7 PILLAR
claude-md-examples-web-development             CLAUDE.md                4   5 

claude-code-github-actions                     Deployment & Workflow    8   8 PILLAR
claude-code-enterprise                         Deployment & Workflow    7  10 

claude-code-hooks                              Extensibility            7   9 peer
claude-code-mcp                                Extensibility            4   9 peer
claude-code-plugins                            Extensibility            9   7 peer
claude-code-skills                             Extensibility           13   6 peer
claude-code-subagents                          Extensibility           10   8 peer

claude-code-seo-website-optimization           SEO                     10  11 PILLAR
claude-code-technical-seo-audit                SEO                      6   6 
google-search-console-claude-code              SEO                      4   5 

build-shopify-store-with-claude-code           Shopify                  8   7 PILLAR
shopify-seo-with-claude-code                   Shopify                  4   7 

claude-code-certification                      Standalone               2   7 peer
vibe-coding-tools                              Standalone               3   8 peer

how-to-build-a-website-with-claude-code        Website Development     18  13 PILLAR
best-claude-code-prompts-for-web-development   Website Development     14   7 
claude-code-accessibility-audit                Website Development      2   5 
claude-code-performance-core-web-vitals        Website Development      5   4 
claude-code-terminal-setup                     Website Development      3  10 
claude-code-website-audit                      Website Development     10  11 
claude-code-website-security-audit             Website Development      5   6
```

`in` and `out` count distinct guide-to-guide links in the article bodies, excluding links
inside `<pre>` blocks and self-links. No article is an orphan; every supporting guide
links up to its pillar and is linked down from it.

## Guide → free resource pairings

| Guide | Resource |
| --- | --- |
| Security audit | [`/pages/claude-code-security-checklist`](https://sitebuilderstack.com/pages/claude-code-security-checklist) |
| Google Search Console | SEO checklist, website audit checklist |
| Performance | Launch checklist, website audit checklist |
| Accessibility | Website audit checklist, launch checklist |
| Website audit | Website audit checklist |
| Technical SEO audit | SEO checklist |
| CLAUDE.md examples | Production CLAUDE.md starter |

## Where the next article should come from

**Not from this map.** The cluster structure is complete enough that the next content
decision should come from Search Console, not from a gap on a diagram:

```
New guides → crawled and indexed → Search Console data
  → queries Google already associates with the domain
  → improve the page that already ranks
  → earn links → authority → only then expand
```

Regenerate `docs/seo/GSC-CONTENT-OPPORTUNITIES.md` before proposing anything new.
