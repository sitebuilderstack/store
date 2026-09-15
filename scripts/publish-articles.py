#!/usr/bin/env python3
"""Publish the cornerstone guides to the Shopify blog.

Reads content/articles.json plus the HTML bodies in content/articles/,
then creates or updates each article in the order listed. Idempotent:
an existing handle is updated rather than duplicated.

SEO title and description are set through the global.title_tag and
global.description_tag metafields, which is what the theme's SEO tags
read.

Usage: publish-articles.py [--dry-run] [handle ...]
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import gql, check_user_errors  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "content", "articles.json")
BODIES = os.path.join(ROOT, "content", "articles")

ARTICLE_FIELDS = """
  id handle title summary isPublished publishedAt templateSuffix
  tags author{ name }
  image{ url altText }
  blog{ id handle }
"""


def blog_id(handle):
    d = gql("query($q:String!){ blogs(first:5, query:$q){ nodes{ id handle } } }",
            {"q": "handle:%s" % handle})
    for b in d["blogs"]["nodes"]:
        if b["handle"] == handle:
            return b["id"]
    raise SystemExit("blog not found: %s" % handle)


def find_article(bid, handle):
    """blog.articles has no query argument, so list and filter locally."""
    d = gql("""query($id:ID!){ blog(id:$id){
                 articles(first:100){ nodes{ %s } } } }""" % ARTICLE_FIELDS,
            {"id": bid})
    for a in d["blog"]["articles"]["nodes"]:
        if a["handle"] == handle:
            return a
    return None


def seo_metafields(a):
    return [
        {"namespace": "global", "key": "title_tag",
         "type": "single_line_text_field", "value": a["seoTitle"]},
        {"namespace": "global", "key": "description_tag",
         "type": "multi_line_text_field", "value": a["seoDescription"]},
    ]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv

    m = json.load(io.open(MANIFEST, encoding="utf-8"))
    tax = set(m["tagTaxonomy"])
    bid = blog_id(m["blogHandle"])
    print("blog %s -> %s\n" % (m["blogHandle"], bid))

    for a in m["articles"]:
        if args and a["handle"] not in args:
            continue

        bad = set(a["tags"]) - tax
        if bad:
            raise SystemExit("%s: tags outside the taxonomy: %s" % (a["handle"], bad))

        body = io.open(os.path.join(BODIES, a["file"]), encoding="utf-8").read()
        payload = {
            "title": a["title"],
            "handle": a["handle"],
            "body": body,
            "summary": "<p>%s</p>" % a["excerpt"],
            "tags": a["tags"],
            "author": {"name": m["author"]},
            "image": {"url": m["cdn"] + a["image"], "altText": a["imageAlt"]},
            "isPublished": True,
            "metafields": seo_metafields(a),
        }

        existing = find_article(bid, a["handle"])
        if dry:
            print("%-44s %s  (%d bytes body)" %
                  (a["handle"], "would update" if existing else "would create", len(body)))
            continue

        if existing:
            q = """mutation($id:ID!,$article:ArticleUpdateInput!){
                     articleUpdate(id:$id, article:$article){
                       article{ %s } userErrors{ field message } } }""" % ARTICLE_FIELDS
            payload.pop("metafields")           # set separately on update
            d = gql(q, {"id": existing["id"], "article": payload})
            check_user_errors(d["articleUpdate"], "articleUpdate")
            art = d["articleUpdate"]["article"]
            mq = """mutation($mf:[MetafieldsSetInput!]!){
                      metafieldsSet(metafields:$mf){ userErrors{ field message } } }"""
            mfs = [dict(f, ownerId=art["id"]) for f in seo_metafields(a)]
            dm = gql(mq, {"mf": mfs})
            check_user_errors(dm["metafieldsSet"], "metafieldsSet")
            verb = "updated"
        else:
            payload["blogId"] = bid
            q = """mutation($article:ArticleCreateInput!){
                     articleCreate(article:$article){
                       article{ %s } userErrors{ field message } } }""" % ARTICLE_FIELDS
            d = gql(q, {"article": payload})
            check_user_errors(d["articleCreate"], "articleCreate")
            art = d["articleCreate"]["article"]
            verb = "created"

        print("%-44s %s" % (a["handle"], verb))
        print("    title      %s" % art["title"])
        print("    author     %s" % art["author"]["name"])
        print("    tags       %s" % ", ".join(art["tags"]))
        print("    published  %s  %s" % (art["isPublished"], art["publishedAt"]))
        print("    image      %s" % (art["image"] or {}).get("url", "NONE"))
        print("    alt        %s" % ((art["image"] or {}).get("altText") or "NONE")[:70])
        print()


if __name__ == "__main__":
    main()
