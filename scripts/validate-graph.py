#!/usr/bin/env python3
"""Validate content/content-graph.json against the article and resource manifests.

The graph drives pillar pages, learning paths, prev/next navigation, related
guides and the library filters. A handle that does not resolve produces a dead
internal link on a live page, so every reference is checked in both directions
rather than trusted.

Exit status is non-zero on any failure. Run with --self-test to prove the
checks fire: each one is applied to a deliberately broken graph and must be
reported, and the real graph must stay clean.
"""
import io
import json
import re
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEVELS = {"Beginner", "Intermediate", "Advanced"}
TYPES = {"Guide", "Workflow", "Tutorial", "Reference", "Example", "Checklist", "Comparison"}
# "Convert" added 2026-09-08 with the conversion cluster. The enum is closed
# on purpose — it is a filter facet in the guide library, and an unbounded
# set of one-article goals makes the filter useless. Adding one is a
# decision; this is that decision, made because the site now has a
# Build/Rank/Convert lifecycle and five guides that serve the last stage.
GOALS = {"Build", "Optimize", "Secure", "Deploy", "Audit", "Learn", "Convert"}


def load(path):
    with io.open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return json.load(fh)


def content_page_handles():
    """Handles declared by the page publishers, read rather than duplicated.

    Long-form pages and tool pages are equally valid targets — the hub renders
    them through the global `pages` object, which does not care which script
    created them.
    """
    handles = set()
    for name in ("publish-pages.py", "publish-tools.py"):
        src = io.open(os.path.join(ROOT, "scripts", name), encoding="utf-8").read()
        handles |= set(re.findall(r'"handle":\s*"([a-z0-9-]+)"', src))
    return handles


def check(graph, article_handles, resource_handles):
    """Return a list of human-readable failures. Empty means valid."""
    bad = []
    arts = graph["articles"]
    pillars = graph["pillars"]
    paths = graph["paths"]

    # Every published article must be classified, and every classified article
    # must be published. A guide missing from the graph silently loses its
    # pillar link, its related guides and its place in the library filters.
    missing = sorted(set(article_handles) - set(arts))
    extra = sorted(set(arts) - set(article_handles))
    for h in missing:
        bad.append("article not in graph: %s" % h)
    for h in extra:
        bad.append("graph references an article that is not published: %s" % h)

    for h, a in sorted(arts.items()):
        if a["pillar"] not in pillars:
            bad.append("%s: unknown pillar %r" % (h, a["pillar"]))
        elif h not in pillars[a["pillar"]]["cluster"]:
            # The 'up' link and the pillar's own list must agree, or the pillar
            # page omits an article that points at it.
            bad.append("%s: primary pillar %s does not list it in its cluster" % (h, a["pillar"]))
        if a["level"] not in LEVELS:
            bad.append("%s: unknown level %r" % (h, a["level"]))
        if a["type"] not in TYPES:
            bad.append("%s: unknown type %r" % (h, a["type"]))
        if a["goal"] not in GOALS:
            bad.append("%s: unknown goal %r" % (h, a["goal"]))
        if a.get("product") not in graph.get("products", {}):
            bad.append("%s: product %r is not defined" % (h, a.get("product")))
        if a.get("resource") and a["resource"] not in resource_handles:
            bad.append("%s: resource %r is not a published resource page" % (h, a["resource"]))
        rel = a.get("related", [])
        if h in rel:
            bad.append("%s: related list includes itself" % h)
        if len(rel) != len(set(rel)):
            bad.append("%s: related list has duplicates" % h)
        if not 2 <= len(rel) <= 5:
            bad.append("%s: %d related guides, want 2-5" % (h, len(rel)))
        for r in rel:
            if r not in arts:
                bad.append("%s: related handle does not exist: %s" % (h, r))

    for ph, p in sorted(pillars.items()):
        if not p["cluster"]:
            bad.append("pillar %s has an empty cluster" % ph)
        if len(p["cluster"]) != len(set(p["cluster"])):
            bad.append("pillar %s lists an article twice" % ph)
        for h in p["cluster"]:
            if h not in arts:
                bad.append("pillar %s: cluster handle does not exist: %s" % (ph, h))
        # The hub renders these through the global `pages` object, so a handle
        # that is not a published resource page renders nothing at all — a
        # silently missing section rather than a visible error.
        for h in p.get("resources", []):
            if h not in resource_handles:
                bad.append("pillar %s: resource %r is not a published resource page" % (ph, h))

    # prev/next is a single chain per article, so an article may appear in at
    # most one path. Two paths claiming the same article would give it two
    # different "next" guides.
    seen = {}
    for sh, s in sorted(paths.items()):
        if s["pillar"] not in pillars:
            bad.append("path %s: unknown pillar %r" % (sh, s["pillar"]))
        if len(s["steps"]) < 2:
            bad.append("path %s has fewer than 2 steps" % sh)
        for h in s["steps"]:
            if h not in arts:
                bad.append("path %s: step handle does not exist: %s" % (sh, h))
            if h in seen:
                bad.append("%s is in two paths: %s and %s" % (h, seen[h], sh))
            seen[h] = sh

    return bad


def main():
    graph = load("content/content-graph.json")
    manifest = load("content/articles.json")
    resources = load("resources/resources.json")
    article_handles = [a["handle"] for a in manifest["articles"]]
    resource_handles = {p["handle"] for p in resources["pages"]}
    # Long-form pages published from content/pages/ by publish-pages.py are
    # equally valid targets — the hub renders them through the global `pages`
    # object, which does not care which script created them. Read the handles
    # from that script so the two cannot drift.
    resource_handles |= content_page_handles()

    if "--self-test" in sys.argv:
        return self_test(graph, article_handles, resource_handles)

    bad = check(graph, article_handles, resource_handles)
    for b in bad:
        print("  FAIL %s" % b)
    print("%d article(s), %d pillar(s), %d path(s), %d failure(s)"
          % (len(graph["articles"]), len(graph["pillars"]), len(graph["paths"]), len(bad)))
    return 1 if bad else 0


def self_test(graph, article_handles, resource_handles):
    """Each mutation must be caught; the unmutated graph must be clean."""
    import copy

    def broken(fn):
        g = copy.deepcopy(graph)
        fn(g)
        return g

    first = sorted(graph["articles"])[0]
    second = sorted(graph["articles"])[1]
    cases = [
        ("unknown pillar",
         lambda g: g["articles"][first].__setitem__("pillar", "nope")),
        ("article missing from its own pillar cluster",
         lambda g: g["pillars"][graph["articles"][first]["pillar"]]["cluster"].remove(first)),
        ("unknown level",
         lambda g: g["articles"][first].__setitem__("level", "Wizard")),
        ("unknown type",
         lambda g: g["articles"][first].__setitem__("type", "Blogpost")),
        ("unknown goal",
         lambda g: g["articles"][first].__setitem__("goal", "Vibe")),
        ("an article pointing at an undefined product",
         lambda g: g["articles"][first].__setitem__("product", "not-a-product")),
        ("resource that is not published",
         lambda g: g["articles"][first].__setitem__("resource", "not-a-resource")),
        ("related handle that does not exist",
         lambda g: g["articles"][first]["related"].append("ghost-guide")),
        ("related list includes itself",
         lambda g: g["articles"][first]["related"].append(first)),
        ("too few related guides",
         lambda g: g["articles"][first].__setitem__("related", [second])),
        ("pillar resource that is not published",
         lambda g: g["pillars"]["claude-code-seo"]["resources"].append("not-a-resource")),
        ("dangling pillar cluster handle",
         lambda g: g["pillars"]["claude-code-seo"]["cluster"].append("ghost-guide")),
        ("dangling path step",
         lambda g: g["paths"]["seo"]["steps"].append("ghost-guide")),
        ("article claimed by two paths",
         lambda g: g["paths"]["seo"]["steps"].append(g["paths"]["production"]["steps"][0])),
        ("article dropped from the graph",
         lambda g: g["articles"].pop(first)),
        ("graph article that is not published",
         lambda g: g["articles"].__setitem__("invented-guide", copy.deepcopy(g["articles"][second]))),
    ]

    fails = 0
    for name, mut in cases:
        found = check(broken(mut), article_handles, resource_handles)
        ok = bool(found)
        print("  %s  detects: %s" % ("PASS" if ok else "FAIL", name))
        if not ok:
            fails += 1

    clean = check(graph, article_handles, resource_handles)
    print("  %s  stays silent on the real graph%s"
          % ("PASS" if not clean else "FAIL", "" if not clean else " -> %s" % clean))
    if clean:
        fails += 1

    print("\n%d self-test failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
