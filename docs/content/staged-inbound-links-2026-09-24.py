#!/usr/bin/env python3
"""Inbound links to the three September 2026 guides — STAGED, not applied.

    python3 docs/content/staged-inbound-links-2026-09-24.py            # show the diff
    python3 docs/content/staged-inbound-links-2026-09-24.py --apply    # write them

The three target articles are DRAFTS. Their /blogs/guides/ URLs return 404
until someone publishes them, so these links must not go into live articles
before that happens. The script refuses to apply while any target is still
unpublished — that check is the reason it exists rather than a note in a
document.

Each edit appends one sentence to an existing published article, as an exact
string insertion against a re-read of the live body. If the anchor text is not
found the edit is skipped, not forced, so a later revision of that article is
never clobbered.
"""
from __future__ import annotations

import argparse, difflib, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
from shopify_api import gql, check_user_errors  # noqa: E402

BLOG = "gid://shopify/Blog/121974554916"

TARGETS = {
    "bulk-edit-shopify-seo-claude-code": "/blogs/guides/bulk-edit-shopify-seo-claude-code",
    "shopify-digital-product-page-template": "/blogs/guides/shopify-digital-product-page-template",
    "website-scope-of-work-template-claude-code": "/blogs/guides/website-scope-of-work-template-claude-code",
}

# host article -> (anchor already in the body, sentence to append after it)
LINKS = [
    dict(host="shopify-seo-with-claude-code",
         target="bulk-edit-shopify-seo-claude-code",
         why="This guide explains what the SEO fields are; the new one is the narrow task of changing them across many products at once.",
         after="</p>",
         sentence='<p>For the narrower job of changing these fields across many products at once, see <a href="/blogs/guides/bulk-edit-shopify-seo-claude-code">how to bulk edit Shopify SEO titles and meta descriptions with Claude Code</a> — export, review, apply only what was approved, and verify what renders.</p>'),
    dict(host="shopify-admin-api-claude-code",
         target="bulk-edit-shopify-seo-claude-code",
         why="This guide is the API mechanics; the new one is a complete worked job using them.",
         after="</p>",
         sentence='<p>For a complete worked job on top of these mechanics, see <a href="/blogs/guides/bulk-edit-shopify-seo-claude-code">bulk editing Shopify SEO titles and meta descriptions</a>, which adds the review step, the staleness check and the read-back.</p>'),
    dict(host="shopify-conversion-audit-claude-code",
         target="shopify-digital-product-page-template",
         why="The audit finds the problems; the new article is the page structure that avoids several of them.",
         after="</p>",
         sentence='<p>If the audit points at a product page that does not answer enough, the <a href="/blogs/guides/shopify-digital-product-page-template">Shopify digital product page template</a> is the structure to rebuild it against.</p>'),
    dict(host="claude-code-website-audit",
         target="website-scope-of-work-template-claude-code",
         why="Pre-launch checks are exactly what acceptance criteria should be drawn from.",
         after="</p>",
         sentence='<p>On a client project, these checks are where acceptance criteria come from — see the <a href="/blogs/guides/website-scope-of-work-template-claude-code">website scope of work template</a> for turning them into something the client signs off against.</p>'),
]

READ = """
query($id: ID!) { blog(id: $id) { articles(first: 100) { nodes { id handle isPublished body } } } }
"""
WRITE = """
mutation($id: ID!, $article: ArticleUpdateInput!) {
  articleUpdate(id: $id, article: $article) {
    article { id handle }
    userErrors { field message }
  }
}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    nodes = {a["handle"]: a for a in gql(READ, {"id": BLOG})["blog"]["articles"]["nodes"]}

    unpublished = [h for h in TARGETS if not nodes.get(h, {}).get("isPublished")]
    if unpublished:
        print("Targets still unpublished:")
        for h in unpublished:
            print(f"  - {h}  ({TARGETS[h]} returns 404)")
        print("\nThese links would be broken in live articles. Publish the targets first.")
        if args.apply:
            print("REFUSING to apply."); return 1

    applied = skipped = already = 0
    for link in LINKS:
        host = nodes.get(link["host"])
        print(f'\n=== {link["host"]}  ->  {link["target"]}')
        print(f'    Why: {link["why"]}')
        if host is None:
            print("    SKIPPED: host article not found"); skipped += 1; continue
        body = host["body"]
        if link["sentence"] in body:
            print("    already applied"); already += 1; continue
        if link["after"] not in body:
            print(f'    SKIPPED: anchor {link["after"]!r} not present'); skipped += 1; continue

        idx = body.rindex(link["after"]) + len(link["after"])
        updated = body[:idx] + "\n" + link["sentence"] + body[idx:]
        print("    + " + link["sentence"][:150] + "…")
        if not args.apply:
            continue
        res = gql(WRITE, {"id": host["id"], "article": {"body": updated}})
        check_user_errors(res["articleUpdate"], "articleUpdate")
        print("    applied"); applied += 1

    print(f"\napplied {applied}, already {already}, skipped {skipped}")
    if not args.apply:
        print("dry run — nothing was written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
