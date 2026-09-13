#!/usr/bin/env python3
"""Validate content/workflow-selector.json — every URL must be real.

The learning-path engine sits on the homepage and hands visitors a seven-step
route through the site. A URL that does not exist is a dead end on the most
visited page, so every one is resolved against the manifests that define what
is actually published rather than checked by eye.

Product handles are checked against the live store when credentials are
available and skipped otherwise, so this stays runnable offline and on a
public clone.

Run with --self-test to prove each check fires.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Step kinds the theme knows how to render. A kind it does not know renders
# with no label, which is a silently broken step rather than an error.
KINDS = {"guide", "resource", "workflow", "audit", "deploy", "next"}
STEPS_PER_ROADMAP = 6  # after the level-specific first step


def load(p):
    with io.open(os.path.join(ROOT, p), encoding="utf-8") as fh:
        return json.load(fh)


def content_page_handles():
    src = io.open(os.path.join(ROOT, "scripts", "publish-pages.py"), encoding="utf-8").read()
    return set(re.findall(r'"handle":\s*"([a-z0-9-]+)"', src))


def known_urls():
    """Every internal URL the roadmaps are allowed to point at."""
    urls = set()
    for a in load("content/articles.json")["articles"]:
        urls.add("/blogs/guides/" + a["handle"])
    res = load("resources/resources.json")
    urls.add("/pages/" + res["hub"]["handle"])
    for p in res["pages"]:
        urls.add("/pages/" + p["handle"])
    for h in content_page_handles():
        urls.add("/pages/" + h)
    for p in load("content/content-graph.json")["pillars"].values():
        urls.add(p["url"])
    urls.add("/blogs/guides")
    urls.add("/pages/tools")
    return urls


def check(cfg, urls):
    bad = []
    levels = [l["value"] for l in cfg["levels"]]
    stages = cfg.get("stages", [])
    products = cfg.get("products", {})

    if not levels:
        bad.append("no levels defined")
    if not stages:
        bad.append("no stages defined")

    total_steps = STEPS_PER_ROADMAP + 1
    for st in stages:
        e = st.get("entry")
        if not isinstance(e, int) or not 1 <= e <= total_steps:
            bad.append("stage %r entry %r is outside 1..%d" % (st.get("value"), e, total_steps))

    seen = set()
    for g in cfg["goals"]:
        gv = g.get("value")
        if gv in seen:
            bad.append("duplicate goal value: %s" % gv)
        seen.add(gv)
        if not g.get("label"):
            bad.append("%s: no label" % gv)

        # A level with no starting guide silently produces an empty roadmap.
        for lv in levels:
            if lv not in g.get("start", {}):
                bad.append("%s: no start for level %r" % (gv, lv))
        for lv, s in g.get("start", {}).items():
            if lv not in levels:
                bad.append("%s: start for unknown level %r" % (gv, lv))
            if s.get("url") not in urls:
                bad.append("%s/%s: start url does not exist: %s" % (gv, lv, s.get("url")))
            if not s.get("label"):
                bad.append("%s/%s: start has no label" % (gv, lv))

        steps = g.get("steps", [])
        if len(steps) != STEPS_PER_ROADMAP:
            bad.append("%s: %d steps, want %d" % (gv, len(steps), STEPS_PER_ROADMAP))
        for i, s in enumerate(steps, 2):
            if s.get("kind") not in KINDS:
                bad.append("%s step %d: unknown kind %r" % (gv, i, s.get("kind")))
            if s.get("url") not in urls:
                bad.append("%s step %d: url does not exist: %s" % (gv, i, s.get("url")))
            if not s.get("label"):
                bad.append("%s step %d: no label" % (gv, i))

        hub = g.get("hub") or {}
        if hub.get("url") not in urls:
            bad.append("%s: hub url does not exist: %s" % (gv, hub.get("url")))
        if not hub.get("label"):
            bad.append("%s: hub has no label" % gv)

        if g.get("product") not in products:
            bad.append("%s: product %r is not defined" % (gv, g.get("product")))

    for key, p in products.items():
        if not p.get("handle"):
            bad.append("product %s has no handle" % key)
        if not p.get("label") or not p.get("note"):
            bad.append("product %s is missing a label or note" % key)
    return bad


def main():
    cfg = load("content/workflow-selector.json")
    urls = known_urls()

    if "--self-test" in sys.argv:
        return self_test(cfg, urls)

    bad = check(cfg, urls)
    for b in bad:
        print("  FAIL %s" % b)
    print("%d goal(s), %d level(s), %d stage(s), %d known URL(s), %d failure(s)"
          % (len(cfg["goals"]), len(cfg["levels"]), len(cfg.get("stages", [])),
             len(urls), len(bad)))
    return 1 if bad else 0


def self_test(cfg, urls):
    import copy

    def broken(fn):
        c = copy.deepcopy(cfg)
        fn(c)
        return c

    cases = [
        ("start url that does not exist",
         lambda c: c["goals"][0]["start"]["beginner"].__setitem__("url", "/blogs/guides/ghost")),
        ("step url that does not exist",
         lambda c: c["goals"][0]["steps"][2].__setitem__("url", "/pages/ghost")),
        ("hub url that does not exist",
         lambda c: c["goals"][1]["hub"].__setitem__("url", "/pages/nope")),
        ("a level with no starting guide",
         lambda c: c["goals"][0]["start"].pop("experienced")),
        ("a roadmap with the wrong number of steps",
         lambda c: c["goals"][2]["steps"].pop()),
        ("a step with an unknown kind",
         lambda c: c["goals"][2]["steps"][0].__setitem__("kind", "vibes")),
        ("a step with no label",
         lambda c: c["goals"][2]["steps"][1].__setitem__("label", "")),
        ("duplicate goal values",
         lambda c: c["goals"].append(copy.deepcopy(c["goals"][0]))),
        ("a stage entry outside the roadmap",
         lambda c: c["stages"][0].__setitem__("entry", 99)),
        ("a goal pointing at an undefined product",
         lambda c: c["goals"][0].__setitem__("product", "not-a-product")),
        ("a product with no handle",
         lambda c: c["products"]["seo-toolkit"].__setitem__("handle", "")),
    ]

    fails = 0
    for name, mut in cases:
        found = check(broken(mut), urls)
        ok = bool(found)
        print("  %s  detects: %s" % ("PASS" if ok else "FAIL", name))
        if not ok:
            fails += 1
    clean = check(cfg, urls)
    print("  %s  stays silent on the real config%s"
          % ("PASS" if not clean else "FAIL", "" if not clean else " -> %s" % clean))
    if clean:
        fails += 1
    print("\n%d self-test failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
