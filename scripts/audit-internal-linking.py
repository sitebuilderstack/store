#!/usr/bin/env python3
"""Internal linking audit: hub-and-spoke coverage, orphans, and CTA distribution.

Answers four questions that decide whether a topical cluster actually behaves
like one:

  1. Do the templates guarantee the structural links — guide up to its hub,
     hub down to its whole cluster? These are checked once against the theme
     rather than per page, because a template link is either on every page of
     that type or on none of them.
  2. On top of that skeleton, does the body copy carry contextual links? A
     template link tells a crawler that a page type exists; a link inside a
     paragraph tells it which specific pages relate to which.
  3. Is any guide reachable only through templates, with no contextual inbound
     link from any other page's body?
  4. Which commercial product does each cluster point at, and is any product
     unreachable from the content library?

An earlier version of this script reported all 27 guides as failing to link to
their hub. They all do — five times each — from `sbs-article.liquid`. A check
that fires on every single row is almost always the check being wrong, so the
template guarantees are now verified once, by reading the theme.

Usage:
  audit-internal-linking.py                write reports/internal-linking-audit.md
  audit-internal-linking.py --self-test    prove the extractors work
"""
import argparse
import collections
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPORTS = os.path.join(ROOT, "reports")
GRAPH = os.path.join(ROOT, "content", "content-graph.json")

BODY_LINK = re.compile(r'<a\s[^>]*href="(/[^"#?]*)', re.I)


def body_links(text):
    """Internal paths linked from a content file, deduplicated, order kept."""
    seen, out = set(), []
    for m in BODY_LINK.finditer(text or ""):
        u = m.group(1).rstrip("/") or "/"
        if u not in seen:
            seen.add(u)
            out.append(u)
    # markdown links, for the .md sources
    for m in re.finditer(r"\]\((/[^)#?]*)", text or ""):
        u = m.group(1).rstrip("/") or "/"
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def load():
    g = json.load(open(GRAPH, encoding="utf-8"))
    arts = json.load(open(os.path.join(ROOT, "content", "articles.json"),
                          encoding="utf-8"))
    arts = arts if isinstance(arts, list) else arts.get("articles", arts)
    files = {}
    for a in (arts if isinstance(arts, list) else arts.values()):
        p = os.path.join(ROOT, "content", "articles", a["file"])
        files[a["handle"]] = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    pillars = {}
    for k, v in g["pillars"].items():
        p = os.path.join(ROOT, "content", "pillars", v.get("file", k + ".html"))
        pillars[k] = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    return g, files, pillars


TEMPLATES = {
    "guide links up to its hub":
        ("theme/dev/sections/sbs-article.liquid", "pillar_up_click"),
    "guide shows related guides":
        ("theme/dev/sections/sbs-article.liquid", "related_guide_clicked"),
    "hub links down to its cluster":
        ("theme/dev/sections/sbs-pillar.liquid", "cluster"),
    "hub offers a learning path":
        ("theme/dev/sections/sbs-pillar.liquid", "learning_path_step"),
}


def template_guarantees():
    """Structural links the theme renders on every page of a type."""
    out = []
    for label, (path, needle) in sorted(TEMPLATES.items()):
        f = os.path.join(ROOT, path)
        body = open(f, encoding="utf-8").read() if os.path.exists(f) else ""
        out.append((label, path, needle in body))
    return out


def analyse(g, files, pillars):
    art_url = lambda h: "/blogs/guides/" + h
    pil_url = lambda k: g["pillars"][k]["url"].rstrip("/")
    all_guides = {art_url(h) for h in files}
    all_hubs = {pil_url(k) for k in g["pillars"]}

    rows, issues = [], []
    inbound = collections.Counter()

    for h, body in files.items():
        links = body_links(body)
        for u in links:
            if u != art_url(h):
                inbound[u] += 1
        meta = g["articles"].get(h, {})
        pillar = meta.get("pillar")
        prod = meta.get("product")
        x_guides = [u for u in links if u in all_guides and u != art_url(h)]
        x_hubs = [u for u in links if u in all_hubs]
        x_prod = [u for u in links if u.startswith("/products/")]
        rows.append({"handle": h, "pillar": pillar,
                     "x_guides": len(x_guides), "x_hubs": len(x_hubs),
                     "product": prod, "product_linked": len(x_prod),
                     "resource": meta.get("resource"), "body_links": len(links)})
        if not pillar:
            issues.append(("guide is in no hub cluster", art_url(h)))
        if not prod:
            issues.append(("guide has no product CTA declared", art_url(h)))
        # Contextual cross-links are the thing templates cannot supply.
        if len(x_guides) < 2:
            issues.append(("body copy links to fewer than 2 sibling guides",
                           art_url(h)))

    for k, body in pillars.items():
        links = body_links(body)
        for u in links:
            inbound[u] += 1

    orphans = [art_url(h) for h in files if inbound[art_url(h)] == 0]
    for u in sorted(orphans):
        issues.append(("no contextual inbound link from any other page's body", u))

    prod_use = collections.Counter(r["product"] for r in rows if r["product"])
    declared = set(g.get("products", {}))

    # The bundle is reached from every guide by the template's upsell line
    # rather than by a per-guide CTA, so it is structurally linked even though
    # no guide names it in the graph. Verified against the theme rather than
    # assumed, so removing that line turns the finding back on.
    art = os.path.join(ROOT, "theme", "dev", "sections", "sbs-article.liquid")
    tpl = os.path.join(ROOT, "theme", "dev", "templates", "article.json")
    structural = set()
    if os.path.exists(art) and os.path.exists(tpl):
        art_src = open(art, encoding="utf-8").read()
        tpl_src = open(tpl, encoding="utf-8").read()
        if "bundle_cta_clicked" in art_src:
            # ONLY the handle in the template's `bundle` setting. An earlier
            # version matched any product handle appearing anywhere in the
            # template, which also matched `bundle_parts` -- that lists all
            # three components, so every product looked structurally linked and
            # the genuine "no guide points at the conversion toolkit" finding
            # disappeared. An exemption that silences the finding it was not
            # written for is worse than no exemption.
            try:
                tpl_json = json.loads(tpl_src)
                bundle_handle = ""
                for sec in tpl_json.get("sections", {}).values():
                    if sec.get("type") == "sbs-article":
                        bundle_handle = sec.get("settings", {}).get("bundle", "")
            except ValueError:
                bundle_handle = ""
            for key, prod in g.get("products", {}).items():
                if bundle_handle and prod.get("handle") == bundle_handle:
                    structural.add(key)

    for p in sorted(declared - set(prod_use) - structural):
        issues.append(("product declared in the graph but no guide points at it", p))

    return rows, issues, inbound, prod_use, declared


def report(g, rows, issues, inbound, prod_use, declared):
    by_kind = collections.Counter(k for k, _ in issues)
    t = ["# Internal linking audit", "",
         "Generated by `scripts/audit-internal-linking.py`. Regenerate rather "
         "than editing by hand.", "",
         "Counts **body links only**. A link that appears in the header, the "
         "footer or a nav template is on every page and says nothing about which "
         "pages relate to which.", "",
         "| | |", "| --- | --- |",
         "| Guides | %d |" % len(rows),
         "| Hubs | %d |" % len(g["pillars"]),
         "| Findings | %d |" % len(issues), "",
         "## Findings by kind", ""]
    if by_kind:
        t += ["| Finding | Count |", "| --- | ---: |"]
        for k, n in by_kind.most_common():
            t += ["| %s | %d |" % (k, n)]
    else:
        t += ["None.", ""]
    t += ["", "## Every finding", ""]
    if issues:
        t += ["| Finding | Page |", "| --- | --- |"]
        for k, u in sorted(issues):
            t += ["| %s | `%s` |" % (k, u)]
    else:
        t += ["None.", ""]

    t += ["", "## Commercial coverage", "",
          "Which product each hub's guides point at. A cluster with no product "
          "CTA is a cluster that cannot pay for itself; a product no cluster "
          "points at is a product the content library cannot sell.", "",
          "| Product | Guides pointing at it |", "| --- | ---: |"]
    for p in sorted(declared | set(prod_use)):
        t += ["| `%s` | %d |" % (p, prod_use.get(p, 0))]

    t += ["", "## Structural links guaranteed by the theme", "",
          "Checked once against the theme source. These render on every page of "
          "the type, so they are not per-page findings.", "",
          "| Structural link | Template | Present |", "| --- | --- | :-: |"]
    for label, path, present in template_guarantees():
        t += ["| %s | `%s` | %s |" % (label, path, "yes" if present else "**NO**")]

    t += ["", "## Contextual links, per guide", "",
          "What the body copy adds on top of the template skeleton.", "",
          "| Guide | Hub | Sibling guides | Hubs | Product | Body links |",
          "| --- | --- | ---: | ---: | ---: | ---: |"]
    for r in sorted(rows, key=lambda r: (r["pillar"] or "", r["handle"])):
        t += ["| `%s` | %s | %s | %d | %d | %d |" %
              (r["handle"], r["pillar"] or "—",
               ("**%d**" % r["x_guides"]) if r["x_guides"] < 2 else r["x_guides"],
               r["x_hubs"], r["product_linked"], r["body_links"])]
    return "\n".join(t) + "\n"


def self_test():
    ok, bad = [], []

    def check(name, got, want):
        (ok if got == want else bad).append("%s: got %r want %r" % (name, got, want))

    check("html link found", body_links('<a href="/pages/x">x</a>'), ["/pages/x"])
    check("markdown link found", body_links("see [x](/pages/x)"), ["/pages/x"])
    check("external link ignored",
          body_links('<a href="https://example.com/x">x</a>'), [])
    check("anchor stripped", body_links('<a href="/pages/x#top">x</a>'), ["/pages/x"])
    check("trailing slash normalised",
          body_links('<a href="/pages/x/">x</a>'), ["/pages/x"])
    check("duplicate collapsed",
          body_links('<a href="/a">1</a><a href="/a">2</a>'), ["/a"])
    check("two links kept in order",
          body_links('<a href="/b">1</a><a href="/a">2</a>'), ["/b", "/a"])
    check("no links is empty", body_links("<p>nothing</p>"), [])
    for l in ok:
        print("  ok   %s" % l)
    for l in bad:
        print("  FAIL %s" % l)
    print("\n%d passed, %d failed" % (len(ok), len(bad)))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        raise SystemExit(self_test())
    g, files, pillars = load()
    rows, issues, inbound, prod_use, declared = analyse(g, files, pillars)
    os.makedirs(REPORTS, exist_ok=True)
    out = os.path.join(REPORTS, "internal-linking-audit.md")
    open(out, "w", encoding="utf-8").write(
        report(g, rows, issues, inbound, prod_use, declared))
    print("guides %d   findings %d" % (len(rows), len(issues)))
    for k, n in collections.Counter(k for k, _ in issues).most_common():
        print("  %-58s %d" % (k, n))
    print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
