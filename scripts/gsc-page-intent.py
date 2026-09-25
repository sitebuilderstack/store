#!/usr/bin/env python3
"""Compare the queries a page actually receives against what the page says.

For every page with impressions, this pulls its query set from Search Console
and checks whether the meaningful words in those queries appear in the page's
title tag, meta description, and h2 headings. A query the page ranks for but
never names is either an intent gap worth covering or a signal the page is
being matched for something it is not about.

It reports, it does not rewrite. Deciding whether a gap is worth filling is an
editorial judgement, and filling one by inserting keywords is the thing this is
meant to prevent.

Position bands are reported because they change what the right action is:
a page at 4-20 with a poor click-through rate has a snippet problem, and a page
at 40+ does not — no title rewrite moves it.

Usage: gsc-page-intent.py [--days 28] [--min-impressions 5]
"""
import argparse
import datetime
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import google_search_console as gsc  # noqa: E402

SITE = "sc-domain:sitebuilderstack.com"
ORIGIN = "https://sitebuilderstack.com"

# Words too common to signal intent. Deliberately short: over-filtering hides
# real gaps, and every term here is one nobody writes a section about.
STOP = set("""a an and are as at be by for from how in is it of on or that the to
with what when where which who why do does can i you your my me use using guide
tutorial best top vs versus 2024 2025 2026""".split())


def words(s):
    return [w for w in re.findall(r"[a-z0-9.#+_-]{2,}", s.lower()) if w not in STOP]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "sbs-intent-audit"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def page_text(html):
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', html)
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    h2 = re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.S)
    strip = lambda xs: " ".join(re.sub(r"<[^>]+>", " ", x) for x in xs)
    return {
        "title": re.sub(r"<[^>]+>", " ", title.group(1)) if title else "",
        "desc": desc.group(1) if desc else "",
        "headings": strip(h1 + h2),
    }


def band(pos):
    if pos <= 3:
        return "1-3"
    if pos <= 10:
        return "4-10"
    if pos <= 20:
        return "11-20"
    if pos <= 40:
        return "21-40"
    return "41+"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--min-impressions", type=int, default=5)
    a = ap.parse_args()

    end = datetime.date.today()
    start = end - datetime.timedelta(days=a.days)
    res = gsc.search_analytics(SITE, str(start), str(end),
                               dimensions=["page", "query"], row_limit=1000)
    data = next((x for x in res if isinstance(x, dict)), {}) if isinstance(res, tuple) else res

    pages = {}
    for r in data.get("rows", []):
        url, q = r["keys"]
        p = pages.setdefault(url, {"queries": [], "impr": 0, "clicks": 0})
        p["queries"].append((q, r["impressions"], r["position"], r["clicks"]))
        p["impr"] += r["impressions"]
        p["clicks"] += r["clicks"]

    print("Search Console %s to %s\n" % (start, end))
    for url, p in sorted(pages.items(), key=lambda kv: -kv[1]["impr"]):
        if p["impr"] < a.min_impressions:
            continue
        try:
            t = page_text(fetch(url))
        except Exception as e:
            print("  %s -> could not fetch: %s" % (url, e))
            continue

        have = set(words(t["title"] + " " + t["desc"] + " " + t["headings"]))
        in_snippet = set(words(t["title"] + " " + t["desc"]))
        avg_pos = sum(q[2] * q[1] for q in p["queries"]) / max(p["impr"], 1)
        ctr = (p["clicks"] / p["impr"] * 100) if p["impr"] else 0

        print("%s" % url.replace(ORIGIN, ""))
        print("   %d impressions, %d clicks, %.1f%% CTR, avg position %.1f (band %s), %d queries"
              % (p["impr"], p["clicks"], ctr, avg_pos, band(avg_pos), len(p["queries"])))

        gaps = []
        for q, impr, pos, clicks in sorted(p["queries"], key=lambda x: -x[1]):
            missing = [w for w in words(q) if w not in have]
            snippet_missing = [w for w in words(q) if w not in in_snippet]
            if missing:
                gaps.append((q, impr, pos, missing, "title/desc/headings"))
            elif snippet_missing:
                gaps.append((q, impr, pos, snippet_missing, "snippet"))

        if not gaps:
            print("   every query term already appears on the page")
        for q, impr, pos, missing, where in gaps[:8]:
            print("   %-52s %3.0fi pos%5.1f  not in %s: %s"
                  % (q[:52], impr, pos, where, ",".join(missing[:5])))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
