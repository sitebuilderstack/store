#!/usr/bin/env python3
"""Publish the Weekly Website Fix challenges to the weekly-fix blog.

Reads content/content-graph.json → challenges and the bodies in
content/challenges/. Creates the blog if it does not exist. Each challenge is
created or updated with template suffix "challenge", the series metafields
(sbs.challenge, sbs.number, sbs.criteria, sbs.lab, sbs.guide, sbs.module)
and a publish date: a challenge whose date is today or earlier is published
now; a future one is scheduled by setting isPublished with a future
publishDate, which Shopify's ArticleCreateInput documents as "the date and
time when the article should become visible". The publish time is 09:00 in
the store's timezone; a challenge dated today is published immediately.

Idempotent: an existing handle is updated. The scheduled state is verified
after each write by reading publishedAt back and, for future dates, by
fetching the storefront URL (which must 404 until the date).

Usage: publish-challenges.py [--dry-run] [--verify] [handle-or-id ...]
"""
import datetime
import io
import json
import os
import sys
import urllib.error
import urllib.request
import zoneinfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import gql, check_user_errors  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_HANDLE = "weekly-fix"
BLOG_TITLE = "Weekly Website Fix"
AUTHOR = "James Joyner IV"
PUBLISH_HOUR = 9
SITE = "https://sitebuilderstack.com"
FIELDS = "id handle title isPublished publishedAt templateSuffix"


def shop_tz():
    d = gql("{ shop { ianaTimezone } }")
    return zoneinfo.ZoneInfo(d["shop"]["ianaTimezone"])


def blog_id():
    d = gql("query($q:String!){ blogs(first:5, query:$q){ nodes{ id handle } } }", {"q": "handle:%s" % BLOG_HANDLE})
    for b in d["blogs"]["nodes"]:
        if b["handle"] == BLOG_HANDLE:
            return b["id"], False
    q = """mutation($blog:BlogCreateInput!){ blogCreate(blog:$blog){ blog{ id handle } userErrors{ field message } } }"""
    d = gql(q, {"blog": {"title": BLOG_TITLE, "handle": BLOG_HANDLE, "templateSuffix": "weekly-fix",
                          "commentPolicy": "CLOSED"}})
    check_user_errors(d["blogCreate"], "blogCreate")
    return d["blogCreate"]["blog"]["id"], True


def find_article(bid, handle):
    d = gql("query($id:ID!){ blog(id:$id){ articles(first:50){ nodes{ %s } } } }" % FIELDS, {"id": bid})
    for a in d["blog"]["articles"]["nodes"]:
        if a["handle"] == handle:
            return a
    return None


def metafields(cid, c):
    return [
        {"namespace": "sbs", "key": "challenge", "type": "single_line_text_field", "value": cid},
        {"namespace": "sbs", "key": "number", "type": "number_integer", "value": str(c["number"])},
        {"namespace": "sbs", "key": "criteria", "type": "list.single_line_text_field", "value": json.dumps(c["criteria"])},
        {"namespace": "sbs", "key": "lab", "type": "single_line_text_field", "value": c["lab"]},
        {"namespace": "sbs", "key": "guide", "type": "single_line_text_field", "value": c["guide"]},
        {"namespace": "sbs", "key": "module", "type": "single_line_text_field", "value": c["module"]},
        {"namespace": "global", "key": "title_tag", "type": "single_line_text_field", "value": c["title"][:62]},
        {"namespace": "global", "key": "description_tag", "type": "multi_line_text_field", "value": c["seo"]},
    ]


def storefront_status(handle):
    try:
        with urllib.request.urlopen(urllib.request.Request("%s/blogs/%s/%s" % (SITE, BLOG_HANDLE, handle), headers={"User-Agent": "sbs-publish-check"}), timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    verify_only = "--verify" in sys.argv
    graph = json.load(io.open(os.path.join(ROOT, "content", "content-graph.json"), encoding="utf-8"))
    tz = shop_tz()
    now = datetime.datetime.now(tz)
    bid, created = (None, False) if dry else blog_id()
    print("blog %s -> %s%s (store tz %s, now %s)\n" % (BLOG_HANDLE, bid, " (created)" if created else "", tz.key, now.strftime("%Y-%m-%d %H:%M")))

    for cid, c in sorted(graph["challenges"].items(), key=lambda kv: kv[1]["number"]):
        if args and cid not in args and c["handle"] not in args:
            continue
        when = datetime.datetime.combine(datetime.date.fromisoformat(c["publish"]), datetime.time(PUBLISH_HOUR, 0), tzinfo=tz)
        future = when.date() > now.date()
        if not future:
            # Today's (or an overdue) challenge goes live now rather than at
            # 09:00 — a date in the past would otherwise backdate it.
            when = now.replace(microsecond=0)
        if verify_only:
            a = find_article(bid, c["handle"])
            st = storefront_status(c["handle"])
            print("#%d %-58s publishedAt=%s storefront=%s %s" % (c["number"], c["handle"], a and a["publishedAt"], st,
                  "OK scheduled (404 until %s)" % when.date() if future and st == 404 else "OK live" if not future and st == 200 else "CHECK"))
            continue
        body = io.open(os.path.join(ROOT, "content", "challenges", c["file"]), encoding="utf-8").read()
        payload = {"title": c["title"], "handle": c["handle"], "body": body, "author": {"name": AUTHOR},
                   "templateSuffix": "challenge", "tags": ["Weekly Website Fix"],
                   "summary": "<p>%s</p>" % c["summary"],
                   # Shopify refuses isPublished:true with a future publishDate
                   # ("Can't set isPublished to true and also set a future
                   # publish date"); a scheduled article is isPublished:false
                   # with the future date, and becomes visible at that time.
                   "isPublished": not future, "publishDate": when.isoformat()}
        if dry:
            print("#%d %-58s %s at %s (%d bytes)" % (c["number"], c["handle"], "SCHEDULE" if future else "PUBLISH", when.isoformat(), len(body)))
            continue
        existing = find_article(bid, c["handle"])
        if existing:
            q = "mutation($id:ID!,$a:ArticleUpdateInput!){ articleUpdate(id:$id, article:$a){ article{ %s } userErrors{ field message } } }" % FIELDS
            d = gql(q, {"id": existing["id"], "a": payload})
            check_user_errors(d["articleUpdate"], "articleUpdate")
            art, verb = d["articleUpdate"]["article"], "updated"
        else:
            payload["blogId"] = bid
            payload["metafields"] = metafields(cid, c)
            q = "mutation($a:ArticleCreateInput!){ articleCreate(article:$a){ article{ %s } userErrors{ field message } } }" % FIELDS
            d = gql(q, {"a": payload})
            check_user_errors(d["articleCreate"], "articleCreate")
            art, verb = d["articleCreate"]["article"], "created"
        mq = "mutation($mf:[MetafieldsSetInput!]!){ metafieldsSet(metafields:$mf){ userErrors{ field message } } }"
        dm = gql(mq, {"mf": [dict(m, ownerId=art["id"]) for m in metafields(cid, c)]})
        check_user_errors(dm["metafieldsSet"], "metafieldsSet")
        st = storefront_status(c["handle"])
        print("#%d %-58s %s  isPublished=%s publishedAt=%s storefront=%s -> %s"
              % (c["number"], c["handle"], verb, art["isPublished"], art["publishedAt"], st,
                 "scheduled" if future else "live"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
