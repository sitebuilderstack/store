#!/usr/bin/env python3
"""Build the internal link graph for the guides and report cluster structure.

Reads content/articles.json plus the HTML bodies, and prints per-article
inbound and outbound internal links, plus orphan and cannibalisation signals.
Used to keep docs/seo/topical-authority-map.md honest rather than guessed.

Usage: topical-map.py [--json]
"""
import io, json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(io.open(os.path.join(ROOT, "content", "articles.json"), encoding="utf-8"))
BODIES = os.path.join(ROOT, "content", "articles")

CLUSTERS = {
    "how-to-build-a-website-with-claude-code": "Website Development",
    "best-claude-code-prompts-for-web-development": "Website Development",
    "claude-code-terminal-setup": "Website Development",
    "claude-code-website-audit": "Website Development",
    "claude-code-website-security-audit": "Website Development",
    "claude-code-performance-core-web-vitals": "Website Development",
    "claude-code-accessibility-audit": "Website Development",

    "claude-code-seo-website-optimization": "SEO",
    "claude-code-technical-seo-audit": "SEO",
    "google-search-console-claude-code": "SEO",

    "production-claude-md-web-development": "CLAUDE.md",
    "claude-md-examples-web-development": "CLAUDE.md",

    "build-shopify-store-with-claude-code": "Shopify",
    "shopify-seo-with-claude-code": "Shopify",

    "claude-code-subagents": "Extensibility",
    "claude-code-skills": "Extensibility",
    "claude-code-plugins": "Extensibility",
    "claude-code-mcp": "Extensibility",
    "claude-code-hooks": "Extensibility",

    "claude-code-github-actions": "Deployment & Workflow",
    "claude-code-enterprise": "Deployment & Workflow",

    # Two articles that answer a question rather than support a commercial
    # cluster. They are peers of everything and children of nothing, so they
    # get no pillar and are not expected to link up to one.
    "claude-code-certification": "Standalone",
    "vibe-coding-tools": "Standalone",
}
PILLARS = {
    "Website Development": "how-to-build-a-website-with-claude-code",
    "SEO": "claude-code-seo-website-optimization",
    "CLAUDE.md": "production-claude-md-web-development",
    "Shopify": "build-shopify-store-with-claude-code",
    "Deployment & Workflow": "claude-code-github-actions",

    # Extensibility (subagents, skills, plugins, MCP, hooks) is a peer set,
    # not a hub and spoke. The five were written to cross-reference each
    # other and no one of them is the entry point, so declaring a pillar
    # here would invent a hierarchy the content does not have.
    "Extensibility": None,
    "Standalone": None,
}


def strip_pre(s):
    return re.sub(r"<pre\b.*?</pre>", " ", s, flags=re.S)


def main():
    out_links, titles = {}, {}
    for a in M["articles"]:
        src = io.open(os.path.join(BODIES, a["file"]), encoding="utf-8").read()
        body = strip_pre(src)
        hrefs = re.findall(r'href="(/[^"#]*)', body)
        guides = {h.split("/blogs/guides/")[-1]
                  for h in hrefs if h.startswith("/blogs/guides/") and h.count("/") > 2}
        guides.discard(a["handle"])
        out_links[a["handle"]] = sorted(guides)
        titles[a["handle"]] = a["title"]

    inbound = collections.defaultdict(set)
    for src, dests in out_links.items():
        for d in dests:
            inbound[d].add(src)

    known = set(out_links)
    rows = []
    for h in out_links:
        cluster = CLUSTERS.get(h, "UNMAPPED")
        pillar = PILLARS.get(cluster)
        broken = [d for d in out_links[h] if d not in known]
        rows.append({
            "handle": h, "cluster": cluster, "pillar": pillar or "(peer cluster)",
            "is_pillar": pillar is not None and pillar == h,
            "out": out_links[h], "in": sorted(inbound[h]),
            "links_to_pillar": pillar is None or pillar in out_links[h] or pillar == h,
            "linked_from_pillar": pillar is None or h in out_links.get(pillar, []),
            "broken": broken,
        })

    if "--json" in sys.argv:
        print(json.dumps(rows, indent=1))
        return

    by_cluster = collections.defaultdict(list)
    for r in rows:
        by_cluster[r["cluster"]].append(r)

    print("%-46s %-22s %3s %3s %s" % ("handle", "cluster", "in", "out", "flags"))
    print("-" * 100)
    for c in sorted(by_cluster):
        for r in sorted(by_cluster[c], key=lambda x: (not x["is_pillar"], x["handle"])):
            flags = []
            if r["is_pillar"]:
                flags.append("PILLAR")
            elif r["cluster"] in ("Extensibility", "Standalone"):
                flags.append("peer")
            else:
                if not r["links_to_pillar"]:
                    flags.append("NO-LINK-UP")
                if not r["linked_from_pillar"]:
                    flags.append("NO-LINK-DOWN")
            if not r["in"]:
                flags.append("ORPHAN")
            if r["broken"]:
                flags.append("BROKEN:" + ",".join(r["broken"]))
            print("%-46s %-22s %3d %3d %s" % (
                r["handle"], r["cluster"], len(r["in"]), len(r["out"]), " ".join(flags)))
        print()

    unmapped = [r["handle"] for r in rows if r["cluster"] == "UNMAPPED"]
    if unmapped:
        print("UNMAPPED (add to CLUSTERS):", unmapped)


if __name__ == "__main__":
    main()
