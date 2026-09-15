#!/usr/bin/env python3
"""Publish the free tools hub and the four tool pages.

Each tool page carries three metafields the theme reads:
  sbs.tool          which tool to render
  sbs.related       what to read next, as bare handles
  sbs.product       the one product this tool's audience is likely to want

Only handles are stored. The theme resolves them against the live blog and
product catalogue, so a retitled guide cannot leave a stale label behind.

Idempotent: updates by handle, never duplicates.

Usage: publish-tools.py [--dry-run] [handle ...]
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
SRC = os.path.join(ROOT, "content", "tools")
FIELDS = "id handle title isPublished templateSuffix"
MAX_TITLE, MAX_DESC, SUFFIX = 62, 158, len(" – Site Builder Stack")

PAGES = [
    {
        "handle": "tools", "file": "_hub.md", "suffix": "tools",
        "title": "Free Claude Code Website Tools",
        "seoTitle": "Free Claude Code Website Tools",
        "seoDescription": "Four free browser-based tools: a CLAUDE.md generator, an SEO audit prompt "
                          "generator, a launch readiness score and a project prompt builder.",
    },
    {
        "handle": "claude-md-generator", "file": "claude-md-generator.md", "suffix": "tool",
        "tool": "claudemd",
        "title": "CLAUDE.md Starter Generator",
        "seoTitle": "CLAUDE.md Generator",
        "seoDescription": "Generate a starting CLAUDE.md for your project: real commands, conventions "
                          "worth stating, and prohibitions. Runs in your browser, nothing is sent.",
        "related": ["production-claude-md-web-development", "claude-md-examples-web-development",
                    "claude-code-hooks"],
        "product": "claude-code-website-launch-system",
        "productNote": "The Launch System ships a production CLAUDE.md per platform, already written "
                       "and tested, alongside the hooks and skills that enforce what a file can only request.",
    },
    {
        "handle": "seo-audit-prompt-generator", "file": "seo-audit-prompt-generator.md", "suffix": "tool",
        "tool": "seo-prompt",
        "title": "Claude Code SEO Audit Prompt Generator",
        "seoTitle": "SEO Audit Prompt Generator",
        "seoDescription": "Build a technical SEO audit prompt scoped to your platform and situation. "
                          "Demands evidence, forbids fixing in the same run, works in dependency order.",
        "related": ["claude-code-technical-seo-audit", "claude-code-seo-website-optimization",
                    "google-search-console-claude-code"],
        "product": "claude-code-seo-website-audit-toolkit",
        "productNote": "The SEO & Website Audit Toolkit is this prompt and nineteen more, plus the "
                       "checklists, templates and platform workflows behind them.",
    },
    {
        "handle": "launch-readiness-score", "file": "launch-readiness-score.md", "suffix": "tool",
        "tool": "readiness",
        "title": "Website Launch Readiness Score",
        "seoTitle": "Launch Readiness Score",
        "seoDescription": "Twenty questions across SEO, performance, accessibility, security, analytics "
                          "and deployment. A score out of 100 and a prioritised list of what to fix.",
        "related": ["claude-code-website-audit", "claude-code-github-actions-cloudflare",
                    "claude-code-launch-checklist"],
        "product": "claude-code-website-launch-system",
        "productNote": "The Launch System turns this questionnaire into work you can actually run: "
                       "audits, platform workflows and pre- and post-launch checklists.",
    },
    {
        "handle": "website-prompt-builder", "file": "website-prompt-builder.md", "suffix": "tool",
        "tool": "prompt-builder",
        "title": "Claude Code Website Prompt Builder",
        "seoTitle": "Website Prompt Builder",
        "seoDescription": "Turn a description of what you are building into a structured Claude Code "
                          "project prompt: role, discovery, requirements, constraints and validation.",
        "related": ["how-to-build-a-website-with-claude-code",
                    "best-claude-code-prompts-for-web-development", "claude-code-astro"],
        "product": "claude-code-website-launch-system",
        "productNote": "The Launch System's staged master build prompt is this, developed further and "
                       "tested: thirteen stages, each with its own validation gate.",
    },
]


def find(handle):
    d = gql("query($q:String!){ pages(first:10, query:$q){ nodes{ %s } } }" % FIELDS,
            {"q": "handle:%s" % handle})
    for p in d["pages"]["nodes"]:
        if p["handle"] == handle:
            return p
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv

    for e in PAGES:
        if args and e["handle"] not in args:
            continue
        t = len(e["seoTitle"]) + (0 if "Site Builder Stack" in e["seoTitle"] else SUFFIX)
        if t > MAX_TITLE:
            raise SystemExit("%s: rendered title %d chars, max %d" % (e["handle"], t, MAX_TITLE))
        if len(e["seoDescription"]) > MAX_DESC:
            raise SystemExit("%s: description %d chars, max %d"
                             % (e["handle"], len(e["seoDescription"]), MAX_DESC))

        body = render(os.path.join(SRC, e["file"]))
        payload = {"title": e["title"], "handle": e["handle"], "body": body,
                   "isPublished": True, "templateSuffix": e["suffix"]}
        existing = find(e["handle"])
        if dry:
            print("%-28s %s (%d bytes)" % (e["handle"],
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

        mfs = [
            {"ownerId": page["id"], "namespace": "global", "key": "title_tag",
             "type": "single_line_text_field", "value": e["seoTitle"]},
            {"ownerId": page["id"], "namespace": "global", "key": "description_tag",
             "type": "multi_line_text_field", "value": e["seoDescription"]},
        ]
        if e.get("tool"):
            mfs.append({"ownerId": page["id"], "namespace": "sbs", "key": "tool",
                        "type": "single_line_text_field", "value": e["tool"]})
        if e.get("related"):
            mfs.append({"ownerId": page["id"], "namespace": "sbs", "key": "related",
                        "type": "list.single_line_text_field", "value": json.dumps(e["related"])})
        if e.get("product"):
            mfs.append({"ownerId": page["id"], "namespace": "sbs", "key": "product",
                        "type": "single_line_text_field", "value": e["product"]})
            mfs.append({"ownerId": page["id"], "namespace": "sbs", "key": "product_note",
                        "type": "multi_line_text_field", "value": e["productNote"]})
        mq = ("mutation($mf:[MetafieldsSetInput!]!){ metafieldsSet(metafields:$mf){"
              " userErrors{ field message } } }")
        check_user_errors(gql(mq, {"mf": mfs})["metafieldsSet"], "metafieldsSet")
        print("%-28s %-8s suffix=%s  %d bytes, %d metafield(s)"
              % (e["handle"], verb, page["templateSuffix"], len(body), len(mfs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
