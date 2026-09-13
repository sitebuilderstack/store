#!/usr/bin/env python3
"""Push content/content-graph.json into Shopify metafields.

The theme reads the information architecture from metafields rather than from
a copy of the graph baked into Liquid, so the admin shows the same values the
templates render and there is nothing to regenerate when the theme changes.

Only handles are stored — never titles or URLs. The theme resolves a handle
against the live blog, so a retitled article cannot leave a stale label behind
in a metafield.

Namespace: sbs
  On each article:  pillar, topic, level, content_type, goal,
                    path, step, prev, next, related, resource
  On each pillar page: pillar (its own handle), cluster, path, steps

Usage: publish-graph.py [--dry-run] [--articles-only|--pages-only]
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shopify_api import gql, check_user_errors  # noqa: E402

ROOT = os.path.dirname(HERE)
NS = "sbs"
TEXT = "single_line_text_field"
LIST = "list.single_line_text_field"
INT = "number_integer"


def load(p):
    with io.open(os.path.join(ROOT, p), encoding="utf-8") as fh:
        return json.load(fh)


def blog_articles(handle):
    """handle -> {gid, title} for every article in the blog."""
    out, cursor = {}, None
    while True:
        d = gql("""query($q:String!,$after:String){
                     blogs(first:5, query:$q){ nodes{ id handle
                       articles(first:100, after:$after){
                         nodes{ id handle title }
                         pageInfo{ hasNextPage endCursor } } } } }""",
                {"q": "handle:%s" % handle, "after": cursor})
        blogs = [b for b in d["blogs"]["nodes"] if b["handle"] == handle]
        if not blogs:
            raise SystemExit("blog not found: %s" % handle)
        arts = blogs[0]["articles"]
        for n in arts["nodes"]:
            out[n["handle"]] = {"gid": n["id"], "title": n["title"]}
        if not arts["pageInfo"]["hasNextPage"]:
            return out
        cursor = arts["pageInfo"]["endCursor"]


def pages_by_handle(handles):
    out = {}
    for h in handles:
        d = gql("query($q:String!){ pages(first:5, query:$q){ nodes{ id handle } } }",
                {"q": "handle:%s" % h})
        for n in d["pages"]["nodes"]:
            if n["handle"] == h:
                out[h] = n["id"]
    return out


def set_metafields(entries, dry):
    """metafieldsSet in batches of 25, the API's per-call maximum."""
    if dry:
        for e in entries:
            print("    would set %s.%s = %s" % (e["namespace"], e["key"], e["value"][:60]))
        return len(entries)
    done = 0
    for i in range(0, len(entries), 25):
        chunk = entries[i:i + 25]
        d = gql("""mutation($m:[MetafieldsSetInput!]!){
                     metafieldsSet(metafields:$m){
                       metafields{ key }
                       userErrors{ field message } } }""", {"m": chunk})
        check_user_errors(d["metafieldsSet"], "metafieldsSet")
        done += len(d["metafieldsSet"]["metafields"])
    return done


def article_entries(graph, arts):
    """Build the metafield list for every article, including path position."""
    # Reverse index: handle -> (path handle, 1-based step, total steps)
    pos = {}
    for ph, p in graph["paths"].items():
        for i, h in enumerate(p["steps"]):
            pos[h] = (ph, i + 1, len(p["steps"]))

    entries = []
    for h, a in graph["articles"].items():
        if h not in arts:
            raise SystemExit("article not published, cannot set metafields: %s" % h)
        oid = arts[h]["gid"]

        def add(key, value, mtype=TEXT):
            entries.append({"ownerId": oid, "namespace": NS, "key": key,
                            "type": mtype, "value": value})

        add("pillar", a["pillar"])
        add("topic", a["topic"])
        add("level", a["level"])
        add("content_type", a["type"])
        add("goal", a["goal"])
        add("related", json.dumps(a["related"]), LIST)
        if a.get("resource"):
            add("resource", a["resource"])
        # The one product this guide's reader is likely to want. Stored as a
        # handle so the theme reads the live title and price, and so a page can
        # never show two competing offers.
        # The free tool this guide's reader can use immediately. Rendered above
        # the product CTA on purpose: someone who has just read ten minutes has
        # earned a useful next action before an offer, and the tool is free,
        # ungated and produces something.
        tool = graph.get("tools", {}).get(a.get("tool"))
        if tool:
            add("tool", tool["handle"])
            add("tool_heading", tool["heading"])
            add("tool_note", tool["note"])
            add("tool_label", tool["label"])

        prod = graph.get("products", {}).get(a.get("product"))
        if prod:
            add("product", prod["handle"])
            add("product_heading", prod["heading"])
            add("product_note", prod["note"])
            add("product_label", prod["label"])

        if h in pos:
            path_handle, step, total = pos[h]
            steps = graph["paths"][path_handle]["steps"]
            add("path", path_handle)
            add("step", str(step), INT)
            add("steps_total", str(total), INT)
            # Omitted rather than set empty: Shopify rejects a blank metafield
            # value outright, and Liquid reads an absent metafield as nil, which
            # `!= blank` already handles. So the first and last step of a path
            # simply carry no prev / no next.
            if step > 1:
                add("prev", steps[step - 2])
            if step < total:
                add("next", steps[step])
    return entries


def page_entries(graph, pages):
    entries = []
    for ph, p in graph["pillars"].items():
        handle = p["url"].rsplit("/", 1)[-1]
        if handle not in pages:
            print("    skip (page not published yet): %s" % handle)
            continue
        oid = pages[handle]

        def add(key, value, mtype=TEXT):
            entries.append({"ownerId": oid, "namespace": NS, "key": key,
                            "type": mtype, "value": value})

        add("pillar", ph)
        add("cluster", json.dumps(p["cluster"]), LIST)
        paths = [k for k, v in graph["paths"].items() if v["pillar"] == ph]
        if paths:
            add("path", paths[0])
            add("steps", json.dumps(graph["paths"][paths[0]]["steps"]), LIST)
        if p.get("resources"):
            add("resources", json.dumps(p["resources"]), LIST)
        # Every hub except this one, in the graph's own order. Derived rather
        # than stored, so adding a fifth hub cross-links the other four without
        # anyone remembering to edit them.
        others = [q["url"].rsplit("/", 1)[-1]
                  for k, q in graph["pillars"].items() if k != ph]
        if others:
            add("other_hubs", json.dumps(others), LIST)
    return entries


def main():
    dry = "--dry-run" in sys.argv
    only_a = "--articles-only" in sys.argv
    only_p = "--pages-only" in sys.argv

    graph = load("content/content-graph.json")
    manifest = load("content/articles.json")

    total = 0
    if not only_p:
        arts = blog_articles(manifest["blogHandle"])
        e = article_entries(graph, arts)
        print("articles: %d metafield(s) across %d guide(s)" % (len(e), len(graph["articles"])))
        total += set_metafields(e, dry)

    if not only_a:
        handles = [p["url"].rsplit("/", 1)[-1] for p in graph["pillars"].values()]
        pages = pages_by_handle(handles)
        e = page_entries(graph, pages)
        print("pillar pages: %d metafield(s) across %d page(s)" % (len(e), len(pages)))
        total += set_metafields(e, dry)

    print("%s %d metafield(s)" % ("would set" if dry else "set", total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
