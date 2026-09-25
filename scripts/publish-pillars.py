#!/usr/bin/env python3
"""Publish the four topic hub pages from content/pillars/ and content-graph.json.

Title, SEO metadata, URL and body all come from the graph, so the pages and the
metafields that drive their guide lists cannot describe different things.

Idempotent: updates by handle, never duplicates. Run publish-graph.py --pages-only
afterwards (or just run this with --with-graph) to set the metafields the
sbs-pillar section reads.

Usage: publish-pillars.py [--dry-run] [--with-graph] [handle ...]
"""
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shopify_api import gql, check_user_errors  # noqa: E402

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "content", "pillars")
FIELDS = "id handle title isPublished templateSuffix"

MAX_TITLE = 62
MAX_DESC = 158
TITLE_SUFFIX = len(" – Site Builder Stack")


def find(handle):
    d = gql("query($q:String!){ pages(first:10, query:$q){ nodes{ %s } } }" % FIELDS,
            {"q": "handle:%s" % handle})
    for p in d["pages"]["nodes"]:
        if p["handle"] == handle:
            return p
    return None


def check_lengths(handle, title, desc):
    """The layout appends the shop name unless the title already contains it,
    so the rendered length is what has to fit, not the stored string."""
    t = len(title) + (0 if "Site Builder Stack" in title else TITLE_SUFFIX)
    if t > MAX_TITLE:
        raise SystemExit("%s: rendered title is %d chars, max %d" % (handle, t, MAX_TITLE))
    if len(desc) > MAX_DESC:
        raise SystemExit("%s: description is %d chars, max %d" % (handle, len(desc), MAX_DESC))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv

    with io.open(os.path.join(ROOT, "content", "content-graph.json"), encoding="utf-8") as fh:
        graph = json.load(fh)

    for key, p in graph["pillars"].items():
        handle = p["url"].rsplit("/", 1)[-1]
        if args and handle not in args:
            continue
        check_lengths(handle, p["seoTitle"], p["seoDescription"])

        body = io.open(os.path.join(SRC, p["file"]), encoding="utf-8").read()
        payload = {"title": p["title"], "handle": handle, "body": body,
                   "isPublished": True, "templateSuffix": "pillar"}

        existing = find(handle)
        if dry:
            print("%-32s %s (%d bytes, %d cluster)"
                  % (handle, "would update" if existing else "would create",
                     len(body), len(p["cluster"])))
            continue

        if existing:
            q = ("mutation($id:ID!,$page:PageUpdateInput!){ pageUpdate(id:$id,page:$page){"
                 " page{ %s } userErrors{ field message } } }" % FIELDS)
            d = gql(q, {"id": existing["id"], "page": payload})
            check_user_errors(d["pageUpdate"], "pageUpdate")
            page, verb = d["pageUpdate"]["page"], "updated"
        else:
            q = ("mutation($page:PageCreateInput!){ pageCreate(page:$page){"
                 " page{ %s } userErrors{ field message } } }" % FIELDS)
            d = gql(q, {"page": payload})
            check_user_errors(d["pageCreate"], "pageCreate")
            page, verb = d["pageCreate"]["page"], "created"

        mq = ("mutation($mf:[MetafieldsSetInput!]!){ metafieldsSet(metafields:$mf){"
              " userErrors{ field message } } }")
        mfs = [
            {"ownerId": page["id"], "namespace": "global", "key": "title_tag",
             "type": "single_line_text_field", "value": p["seoTitle"]},
            {"ownerId": page["id"], "namespace": "global", "key": "description_tag",
             "type": "multi_line_text_field", "value": p["seoDescription"]},
        ]
        check_user_errors(gql(mq, {"mf": mfs})["metafieldsSet"], "metafieldsSet")
        print("%-32s %-8s suffix=%s published=%s  %d bytes"
              % (handle, verb, page["templateSuffix"], page["isPublished"], len(body)))

    if "--with-graph" in sys.argv and not dry:
        print()
        subprocess.check_call([sys.executable,
                               os.path.join(HERE, "publish-graph.py"), "--pages-only"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
