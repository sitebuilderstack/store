#!/usr/bin/env python3
"""Keyword research from MEASURED data, not invention.

Every number here comes from the Bing Webmaster Tools keyword API. Nothing is
estimated. Where a figure is unavailable -- notably keyword difficulty, which
no free API exposes -- it is reported as unavailable rather than guessed.

Two limits to keep in view when reading the output:
  * These are BING impressions. Bing is a minority of search volume in most
    markets, so treat the numbers as relative signal, not absolute demand.
  * Impressions measure how often a query is searched. They say nothing about
    how hard it is to rank for it.

Usage: keyword-research.py [--words N] [--min-impressions N]
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bing_webmaster as bing  # noqa: E402

SEEDS = [
    "claude code", "claude code website", "claude code tutorial",
    "claude code prompts", "claude md", "claude code shopify",
    "claude code seo", "ai website builder", "build website with ai",
    "ai web development", "claude code agent", "anthropic claude code",
    "claude code guide", "ai coding assistant", "claude code setup",
    "claude code workflow", "website launch checklist", "shopify store setup",
    "ai website development", "claude code templates", "vibe coding",
    "claude code best practices", "ai seo audit", "build shopify store",
    "claude code examples", "ai landing page", "claude code tips",
    "website build checklist", "claude code project", "ai developer tools",
]

# Queries whose intent is "find, install or log into the tool" -- enormous
# volume, no commercial value here, and unrankable for a new site against
# Anthropic's and OpenAI's own domains.
EXCLUDE = re.compile(
    r"\b(login|log in|sign in|signin|download|install|npm|cli|api key|"
    r"chatgpt|chat gpt|gpt|openai|free|is claude down|desktop|windows|mac|"
    r"extension|app store|pricing|subscription|refund|status|outage|"
    r"wix|squarespace|godaddy|wordpress\.com)\b", re.I)

# Words that signal someone intends to buy, hire, or acquire something --
# as opposed to browsing. This is editorial judgement, labelled as such, not
# data from any API.
BUYER = re.compile(r"\b(buy|price|pricing|cost|best|top|template|templates|kit|"
                   r"system|course|tool|tools|service|services|hire|agency|"
                   r"software|platform|alternative|alternatives|vs|review|"
                   r"reviews|checklist|pack|bundle|pro|premium)\b", re.I)
INFO = re.compile(r"\b(how|what|why|guide|tutorial|learn|example|examples|"
                  r"docs|documentation|explained|beginner)\b", re.I)


def related(seed):
    code, d = bing.call("GET", "GetRelatedKeywords", q=seed, country="us",
                        language="en-US", startDate="2026-05-01", endDate="2026-08-28")
    if code != 200 or not isinstance(d, dict):
        return []
    return d.get("d") or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", type=int, default=3)
    ap.add_argument("--min-impressions", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-filter", action="store_true",
                    help="keep navigational/tool-acquisition queries too")
    a = ap.parse_args()

    found, seen_seed_fail = {}, []
    for s in SEEDS:
        rows = related(s)
        if not rows:
            seen_seed_fail.append(s)
        for r in rows:
            q = (r.get("Query") or "").strip().lower()
            if not q:
                continue
            if len(q.split()) != a.words:
                continue
            if not a.no_filter and EXCLUDE.search(q):
                continue
            imp = r.get("Impressions") or 0
            if imp < a.min_impressions:
                continue
            # keep the highest reading if a phrase surfaces from several seeds
            prev = found.get(q)
            if not prev or imp > prev["impressions"]:
                found[q] = {"query": q, "impressions": imp,
                            "broad": r.get("BroadImpressions") or 0,
                            "seeds": set()}
            found[q]["seeds"].add(s)

    rows = sorted(found.values(), key=lambda x: -x["impressions"])
    for r in rows:
        r["seeds"] = sorted(r["seeds"])
        r["intent"] = ("buyer" if BUYER.search(r["query"])
                       else "informational" if INFO.search(r["query"])
                       else "navigational/other")

    if a.json:
        print(json.dumps(rows, indent=2))
        return

    print("Seeds queried: %d   phrases found at exactly %d words: %d"
          % (len(SEEDS), a.words, len(rows)))
    if seen_seed_fail:
        print("Seeds that returned nothing: %s" % ", ".join(seen_seed_fail))
    print("\n%-44s %12s %12s  %s" % ("PHRASE", "IMPRESSIONS", "BROAD", "INTENT"))
    print("-" * 92)
    for r in rows[:60]:
        print("%-44s %12s %12s  %s"
              % (r["query"][:44], r["impressions"], r["broad"], r["intent"]))
    print("\nImpressions are Bing's, for the US/en-US market, May-Aug 2026.")
    print("Keyword difficulty is NOT available from this API and is not shown.")


if __name__ == "__main__":
    main()
