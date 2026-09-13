#!/usr/bin/env python3
"""Publish the free resource pages to Shopify.

Reads resources/resources.json, converts each Markdown source through
md2html.py, injects a download block pointing at the raw file on the CDN, and
creates or updates the page by handle. Idempotent: an existing handle is
updated, never duplicated.

SEO title and description go on the global.title_tag / global.description_tag
metafields, which is what the theme's SEO tags and the resource section read.

Usage: publish-resources.py [--dry-run] [handle ...]
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shopify_api import gql, check_user_errors  # noqa: E402
from md2html import render  # noqa: E402

ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(ROOT, "resources", "resources.json")
SRC = os.path.join(ROOT, "resources")

PAGE_FIELDS = "id handle title templateSuffix isPublished publishedAt"


MAX_TITLE = 62
MAX_DESC = 158
TITLE_SUFFIX = len(" \u2013 Site Builder Stack")


def check_lengths(e):
    """Refuse to publish metadata that will truncate in a result."""
    t = len(e["seoTitle"]) + (0 if "Site Builder Stack" in e["seoTitle"] else TITLE_SUFFIX)
    if t > MAX_TITLE:
        raise SystemExit("%s: rendered title is %d chars, max %d -> %r"
                         % (e["handle"], t, MAX_TITLE, e["seoTitle"]))
    if len(e["seoDescription"]) > MAX_DESC:
        raise SystemExit("%s: meta description is %d chars, max %d"
                         % (e["handle"], len(e["seoDescription"]), MAX_DESC))


def find_page(handle):
    d = gql("""query($q:String!){ pages(first:10, query:$q){
                 nodes{ %s } } }""" % PAGE_FIELDS, {"q": "handle:%s" % handle})
    for p in d["pages"]["nodes"]:
        if p["handle"] == handle:
            return p
    return None


def download_block(cdn, entry):
    name = entry["download"]
    return (
        '<div class="sbs-resource-download">\n'
        '  <p>Plain Markdown, no sign-up. Drop it straight into a repository.</p>\n'
        '  <a class="sbs-btn sbs-btn--ghost" href="%s%s" download>%s</a>\n'
        "</div>\n\n" % (cdn, name, entry["downloadLabel"])
    )


def body_for(m, entry):
    path = os.path.join(SRC, entry["file"])
    if entry.get("raw"):
        return io.open(path, encoding="utf-8").read()
    html = render(path)
    if entry.get("download"):
        # After the table of contents, before the first paragraph of prose.
        marker = "</nav>\n\n"
        idx = html.find(marker)
        block = download_block(m["cdn"], entry)
        html = (html[:idx + len(marker)] + block + html[idx + len(marker):]
                if idx != -1 else block + html)
    return html


def metafields(entry):
    return [
        {"namespace": "global", "key": "title_tag",
         "type": "single_line_text_field", "value": entry["seoTitle"]},
        {"namespace": "global", "key": "description_tag",
         "type": "multi_line_text_field", "value": entry["seoDescription"]},
    ]


def publish(m, entry, dry):
    check_lengths(entry)
    handle = entry["handle"]
    body = body_for(m, entry)
    suffix = entry.get("templateSuffix", "resource")
    payload = {
        "title": entry["title"],
        "handle": handle,
        "body": body,
        "templateSuffix": suffix,
        "isPublished": True,
    }
    existing = find_page(handle)
    if dry:
        print("%-38s %-12s suffix=%-9s %6d bytes" % (
            handle, "would update" if existing else "would create", suffix, len(body)))
        return

    if existing:
        q = ("mutation($id:ID!,$page:PageUpdateInput!){ pageUpdate(id:$id, page:$page){"
             " page{ %s } userErrors{ field message } } }" % PAGE_FIELDS)
        d = gql(q, {"id": existing["id"], "page": payload})
        check_user_errors(d["pageUpdate"], "pageUpdate")
        page = d["pageUpdate"]["page"]
        verb = "updated"
    else:
        q = ("mutation($page:PageCreateInput!){ pageCreate(page:$page){"
             " page{ %s } userErrors{ field message } } }" % PAGE_FIELDS)
        d = gql(q, {"page": payload})
        check_user_errors(d["pageCreate"], "pageCreate")
        page = d["pageCreate"]["page"]
        verb = "created"

    mq = ("mutation($mf:[MetafieldsSetInput!]!){ metafieldsSet(metafields:$mf){"
          " userErrors{ field message } } }")
    dm = gql(mq, {"mf": [dict(f, ownerId=page["id"]) for f in metafields(entry)]})
    check_user_errors(dm["metafieldsSet"], "metafieldsSet")

    print("%-38s %-8s suffix=%-9s published=%s  %d bytes" % (
        handle, verb, page["templateSuffix"], page["isPublished"], len(body)))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    m = json.load(io.open(MANIFEST, encoding="utf-8"))
    for entry in [m["hub"]] + m["pages"]:
        if args and entry["handle"] not in args:
            continue
        publish(m, entry, dry)


if __name__ == "__main__":
    main()
