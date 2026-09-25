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
        "handle": "my-projects",
        "file": "my-projects.md",
        "templateSuffix": "my-projects",
        "title": "My Projects",
        "seoTitle": "My Projects — Your Website Workspace",
        "seoDescription": "Keep generated checklists, prompts and plans for your own "
                          "website next to the guides, labs and tasks you are working "
                          "through. Browser-local, no account.",
    },
    {
        "handle": "labs",
        "file": "labs.md",
        "templateSuffix": "labs",
        "title": "Practical Labs",
        "seoTitle": "Practical Labs — Find the Fault",
        "seoDescription": "Four fifteen-minute labs on a fictional clinic's site: a wrong "
                          "canonical, a launch to hold, a form that only looks like it "
                          "works, a health report to triage.",
    },
    {
        "handle": "lab-launch-readiness",
        "file": "lab-launch-readiness.md",
        "templateSuffix": "lab",
        "title": "Launch Readiness Lab",
        "seoTitle": "Launch Readiness Lab — Go or Hold?",
        "seoDescription": "Read a demonstration site's release evidence and decide whether "
                          "it launches. See which capture decides it and why a backup log "
                          "saying SUCCESS proved nothing.",
    },
    {
        "handle": "lab-technical-seo",
        "file": "lab-technical-seo.md",
        "templateSuffix": "lab",
        "title": "Technical SEO Lab",
        "seoTitle": "Technical SEO Lab — A Canonical That Lies",
        "seoDescription": "A fixture with a canonical pointing at staging and a redirect "
                          "landing on the homepage. Find both from rendered responses, "
                          "pick the first safe fix, verify it.",
    },
    {
        "handle": "lab-conversion-functionality",
        "file": "lab-conversion-functionality.md",
        "templateSuffix": "lab",
        "title": "Conversion Functionality Lab",
        "seoTitle": "Conversion Lab — The Form That Looks Fine",
        "seoDescription": "A landing page that says Thanks without an email address and a "
                          "button that breaks its own promise. Find both, read the failing "
                          "check, then the passing one.",
    },
    {
        "handle": "lab-website-operations",
        "file": "lab-website-operations.md",
        "templateSuffix": "lab",
        "title": "Website Operations Lab",
        "seoTitle": "Operations Lab — Triage a Health Report",
        "seoDescription": "Six findings, one hour. Order them, pick a read-only diagnostic "
                          "before any change, and learn what a backup log saying SUCCESS "
                          "seven nights running proves.",
    },
    {
        "handle": "weekly-fix",
        "file": "weekly-fix.md",
        "templateSuffix": "weekly-fix",
        "title": "Weekly Website Fix",
        "seoTitle": "Weekly Website Fix — 15 Minutes a Week",
        "seoDescription": "A new challenge every Thursday: one thing commonly broken on a "
                          "website, a safe way to check yours in fifteen minutes, and the "
                          "record you keep. No account.",
    },
    {
        "handle": "team-licenses",
        "file": "team-licenses.md",
        "templateSuffix": "team-licenses",
        "title": "Team and Agency Licences",
        "seoTitle": "Team and Agency Licences",
        "seoDescription": "Multi-seat licences for Site Builder Stack products: what a seat "
                          "covers, how it differs from the client-work rights you have, and "
                          "how to request a quote.",
    },
    {
        "handle": "membership",
        "file": "membership.md",
        "templateSuffix": "membership",
        "title": "Workflow Club",
        "seoTitle": "Workflow Club — One New Workflow a Month",
        "seoDescription": "A proposed monthly workflow release for people who keep websites "
                          "running with Claude Code. Read the pilot; no payment is taken and "
                          "nothing is for sale yet.",
    },
    {
        "handle": "website-review",
        "file": "website-review.md",
        "templateSuffix": "website-review",
        "title": "Website Launch & Conversion Review",
        "seoTitle": "Website Launch & Conversion Review",
        "seoDescription": "A fixed-scope written review of up to five public pages: messaging, "
                          "navigation, technical issues and the path to purchase, with "
                          "evidence per finding.",
    },
    {
        "handle": "recommended-tools",
        "file": "recommended-tools.md",
        "templateSuffix": "recommended-tools",
        "title": "Recommended Tools",
        "seoTitle": "Recommended Tools for Website Work",
        "seoDescription": "Five tools for hosting, monitoring, analytics, email and deployment, "
                          "chosen because the guides lead you to need them. No commission is "
                          "earned from any link.",
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
