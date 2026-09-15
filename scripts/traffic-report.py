#!/usr/bin/env python3
"""Shopify analytics traffic report, with a bot-vs-human read.

A new store's session numbers are mostly not audience. Automated checks that
execute JavaScript register as sessions, and referrer-spoofing crawlers show up
as "search". This prints the breakdowns and the signals that separate the two,
so the numbers are not read as traction they are not.

Usage: traffic-report.py [days]
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location("sq", os.path.join(HERE, "shopifyql.py"))
sq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sq)

D = int(sys.argv[1]) if len(sys.argv) > 1 else 30
W = "SINCE -%dd UNTIL today" % D

QUERIES = [
    ("FROM sessions SHOW sessions %s" % W,
     "Total sessions, last %d days" % D),
    ("FROM sessions SHOW sessions GROUP BY referrer_source %s ORDER BY sessions DESC LIMIT 25" % W,
     "By referrer source"),
    ("FROM sessions SHOW sessions GROUP BY referrer_name %s ORDER BY sessions DESC LIMIT 25" % W,
     "By referrer name"),
    ("FROM sessions SHOW sessions GROUP BY landing_page_path %s ORDER BY sessions DESC LIMIT 25" % W,
     "By landing page"),
    ("FROM sessions SHOW sessions GROUP BY utm_source, utm_medium, utm_campaign %s "
     "ORDER BY sessions DESC LIMIT 15" % W,
     "By UTM tagging (none means no campaign is attributed)"),
    ("FROM sessions SHOW sessions GROUP BY referrer_source, day %s ORDER BY day ASC LIMIT 90" % W,
     "By day and source"),
    ("FROM sessions SHOW sessions GROUP BY hour WHERE referrer_source = 'search' "
     "SINCE -7d UNTIL today ORDER BY hour ASC LIMIT 100",
     "Search sessions by hour -- a single-hour spike across every URL is a crawler, not people"),
]

for ql, title in QUERIES:
    sq.show(ql, title)
    print()

print("=" * 74)
print("HOW TO READ THIS")
print("=" * 74)
print("""  Sessions are not audience until proven otherwise. Three tells:

  * Landing pages that no human would choose -- /password, /products_preview,
    /checkouts/cn/..., /cart as an entry point. These are automated checks or
    your own admin previews.
  * A flat spread across every URL including tag archives, inside one hour.
    Real search traffic is lumpy and concentrated on a few pages.
  * "search" sessions arriving before Search Console shows the sitemap as
    fetched. Nobody can click a result for a page that is not indexed yet, so
    a Google referrer at that point is spoofed or a crawler.

  Cross-check any apparent organic traffic against the Search Console
  performance report, which counts impressions and clicks Google actually
  served. If Search Console shows no clicks, there were no clicks.""")
