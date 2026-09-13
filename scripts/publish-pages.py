#!/usr/bin/env python3
"""Publish the hand-authored content pages in content/pages/ to Shopify.

Separate from publish-resources.py: those pages are generated from Markdown,
these are authored as HTML because they are prose rather than reference
documents. Idempotent — updates by handle, never duplicates.

Usage: publish-pages.py [--dry-run] [handle ...]
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
SRC = os.path.join(ROOT, "content", "pages")

PAGES = [
    {
        "handle": "claude-code-failure-library",
        "file": "failure-library.md",
        "templateSuffix": "resource",
        "title": "Claude Code Web Development Failure Library",
        "seoTitle": "Claude Code Failure Library",
        "seoDescription": "Twenty ways a website built with an AI coding assistant breaks quietly, "
                          "with how to detect, fix and prove each one. Sixteen observed on this site.",
    },
    {
        "handle": "case-study",
        "file": "case-study.md",
        "templateSuffix": "case-study",
        "title": "How SiteBuilderStack.com Was Built With the Launch System",
        "seoTitle": "Case Study: Built With the Launch System",
        "seoDescription": "Building this store with the Claude Code Website Launch System: "
                          "the thirteen-stage workflow, and five production failures every "
                          "check called healthy.",
    },
    {
        "handle": "build-rank-convert",
        "file": "build-rank-convert.md",
        "templateSuffix": "build-rank-convert",
        "title": "Build → Rank → Convert → Operate With Claude Code",
        "seoTitle": "Build, Rank, Convert, Operate With Claude",
        "seoDescription": "The four problems every website meets, in order, and the "
                          "Claude Code system for each: build it, get it found, convert "
                          "the traffic, then keep it running.",
    },
    {
        "handle": "claude-code-website-development-benchmark-2026",
        "file": "benchmark.md",
        "templateSuffix": "resource",
        "title": "Claude Code Website Development Benchmark 2026",
        "seoTitle": "Claude Code Website Benchmark 2026",
        "seoDescription": "An open benchmark of Claude Code across Shopify, WordPress, "
                          "Astro, Next.js and static HTML. Methodology published first; "
                          "no trials run yet.",
    },
    {
        "handle": "my-learning",
        "file": "my-learning.md",
        "templateSuffix": "my-learning",
        "title": "My Learning",
        "seoTitle": "My Learning — Track Your Progress",
        "seoDescription": "Your progress through the Claude Code learning tracks on this "
                          "site, kept in your browser. No account, and nothing is "
                          "transmitted anywhere.",
    },
    {
        "handle": "about",
        "file": "about.html",
        "title": "About James Joyner IV",
        "seoTitle": "About James Joyner IV",
        "seoDescription": "James Joyner IV, senior software engineer with 25 years in "
                          "infrastructure engineering, on why Site Builder Stack exists "
                          "and how its guides are checked.",
    },
]
FIELDS = "id handle title templateSuffix isPublished"


def find(handle):
    d = gql("query($q:String!){ pages(first:10, query:$q){ nodes{ %s } } }" % FIELDS,
            {"q": "handle:%s" % handle})
    for p in d["pages"]["nodes"]:
        if p["handle"] == handle:
            return p
    return None


MAX_TITLE = 62
MAX_DESC = 158
TITLE_SUFFIX = len(" \u2013 Site Builder Stack")


def check_lengths(e):
    """Refuse to publish metadata that will truncate in a result.

    The layout appends the shop name to any title that does not already contain
    it, so the rendered length is what matters, not the stored string.
    """
    t = len(e["seoTitle"]) + (0 if "Site Builder Stack" in e["seoTitle"] else TITLE_SUFFIX)
    if t > MAX_TITLE:
        raise SystemExit("%s: rendered title is %d chars, max %d -> %r"
                         % (e["handle"], t, MAX_TITLE, e["seoTitle"]))
    if len(e["seoDescription"]) > MAX_DESC:
        raise SystemExit("%s: meta description is %d chars, max %d"
                         % (e["handle"], len(e["seoDescription"]), MAX_DESC))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    for e in PAGES:
        if args and e["handle"] not in args:
            continue
        check_lengths(e)
        path = os.path.join(SRC, e["file"])
        # Markdown sources go through the same converter as the resource pages,
        # so the markup conventions stay identical across the site.
        body = render(path) if path.endswith(".md") else io.open(path, encoding="utf-8").read()
        payload = {"title": e["title"], "handle": e["handle"],
                   "body": body, "isPublished": True}
        if e.get("templateSuffix"):
            payload["templateSuffix"] = e["templateSuffix"]
        existing = find(e["handle"])
        if dry:
            print("%-20s %s (%d bytes)" % (e["handle"],
                  "would update" if existing else "would create", len(body)))
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
             "type": "single_line_text_field", "value": e["seoTitle"]},
            {"ownerId": page["id"], "namespace": "global", "key": "description_tag",
             "type": "multi_line_text_field", "value": e["seoDescription"]},
        ]
        dm = gql(mq, {"mf": mfs})
        check_user_errors(dm["metafieldsSet"], "metafieldsSet")
        print("%-20s %-8s published=%s  %d bytes" %
              (e["handle"], verb, page["isPublished"], len(body)))


if __name__ == "__main__":
    main()
