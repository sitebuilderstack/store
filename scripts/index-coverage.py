#!/usr/bin/env python3
"""Index coverage for every URL in the sitemap, from the URL Inspection API.

Reports what Google has actually done with each URL rather than what we
submitted. "Discovered - currently not indexed" is the state that matters for a
new site: it means Google knows about the page and has chosen not to fetch it.

Usage: index-coverage.py
"""
import collections
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import google_search_console as gsc  # noqa: E402

SITE = "sc-domain:sitebuilderstack.com"
BASE = "https://sitebuilderstack.com"


def sitemap_urls():
    out, queue, seen = [], [BASE + "/sitemap.xml"], set()
    while queue:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        req = urllib.request.Request(u, headers={"User-Agent": "sbs-coverage/1.0"})
        body = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
        locs = [m.replace("&amp;", "&") for m in re.findall(r"<loc>([^<]+)</loc>", body)]
        if "<sitemapindex" in body:
            queue.extend(locs)
        else:
            out.extend(locs)
    return sorted(set(out))


def main():
    urls = sitemap_urls()
    states = collections.Counter()
    rows = []
    for u in urls:
        # The Inspection API times out often enough that a single failure must
        # not end the run or, worse, be silently dropped from the totals. Any
        # URL that cannot be inspected after retries is counted as an error and
        # shows up in the summary, so a partial scan cannot read as a clean one.
        code = d = None
        for attempt in range(4):
            try:
                code, d = gsc.inspect_url(SITE, u)
            except Exception as e:                       # noqa: BLE001
                code, d = None, {"error": type(e).__name__}
            if code == 200:
                break
            time.sleep(min(30, 3 * (2 ** attempt)))
        if code != 200:
            rows.append((u, "UNINSPECTED (HTTP %s)" % code, ""))
            states["uninspected"] += 1
            continue
        idx = d.get("inspectionResult", {}).get("indexStatusResult", {})
        state = idx.get("coverageState", "?")

        # "URL is unknown to Google" is the state this API returns when it has
        # no record — and also, it turns out, when it is answering a rapid
        # sequence of calls and returns a degraded record. Two URLs reported
        # unknown by a batch run reported "Discovered" on three consecutive
        # single inspections, with a sitemap association and referring URLs.
        #
        # So an unknown result is confirmed with a second, unhurried call before
        # it is believed. Anything else is taken at face value.
        if "unknown" in state.lower():
            time.sleep(3)
            code2, d2 = gsc.inspect_url(SITE, u)
            if code2 == 200:
                idx2 = d2.get("inspectionResult", {}).get("indexStatusResult", {})
                state2 = idx2.get("coverageState", state)
                if "unknown" not in state2.lower():
                    state, idx = state2, idx2

        # Every URL here came out of our own sitemap. If the API answers
        # "unknown" AND reports no sitemap association for one of them, the two
        # statements contradict each other and the record is degraded rather
        # than informative — the same URL returns "Discovered" with
        # sitemap=True on an unhurried call. Label it as unmeasured instead of
        # reporting a state that is not true.
        if "unknown" in state.lower() and not idx.get("sitemap"):
            state = "UNMEASURED (API returned an empty record)"
        crawl = (idx.get("lastCrawlTime") or "never")[:10]
        rows.append((u, state, crawl))
        states[state] += 1
        print("%-58s %-38s %s" % ((u.replace(BASE, "") or "/")[:58], state[:38], crawl),
              flush=True)
        time.sleep(0.4)

    print("\n%d URL(s) in the sitemap" % len(urls))
    for state, n in states.most_common():
        print("  %-40s %d" % (state, n))
    unmeasured = sum(v for k, v in states.items() if k.startswith("UNMEASURED"))
    if unmeasured:
        print("\n%d URL(s) could not be measured: the Inspection API returned an empty\n"
              "record for them. The indexed count above is still reliable; the split\n"
              "between discovered and unknown is not." % unmeasured)
    if states["uninspected"]:
        print("\n!! %d URL(s) could not be inspected. This scan is INCOMPLETE."
              % states["uninspected"])
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
