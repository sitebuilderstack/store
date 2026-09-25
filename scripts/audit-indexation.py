#!/usr/bin/env python3
"""Indexation audit: what the live site tells a crawler it should index.

Reuses `audit-seo-site.py` for the crawl rather than re-implementing one, then
answers the indexation questions specifically:

  * Is every sitemap URL reachable, canonical to itself, and indexable?
  * Is anything indexable that should not be, or noindexed that should not be?
  * Are there duplicate titles or descriptions — the cheapest signal that two
    URLs are competing?
  * Do Shopify's parameterised and paginated variants behave?
  * Are canonicals absolute, self-referencing, and pointing at a live URL?

Where Search Console access exists, it also reports what Google has actually
done with each URL, which is the only source that settles "is it indexed".

Nothing here noindexes or redirects anything. It reports.

Usage:
  audit-indexation.py                    crawl live and write the report
  audit-indexation.py --crawl FILE.json  reuse a saved audit-seo-site.py --json
  audit-indexation.py --self-test        prove the rules fire and stay silent
"""
import argparse
import collections
import json
import os
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPORTS = os.path.join(ROOT, "reports")
BASE = os.environ.get("SBS_BASE", "https://sitebuilderstack.com")
UA = "sbs-indexation-audit/1.0 (+https://sitebuilderstack.com)"

# URL families that are deliberately kept out of the index, with the reason.
# Tag archives are noindex,follow by decision in landing.liquid: they are thin
# and would compete with the guide index while still passing link equity.
# Shopify's /policies/ pages are NOT here — indexing them is legitimate, and
# one of them already takes impressions.
NOINDEX_EXPECTED = {
    "/cart": "Shopify cart",
    "/checkout": "Shopify checkout",
    "/account": "customer account",
    "/search": "internal search results",
    "/blogs/guides/tagged/": "tag archive, noindex,follow by decision",
}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


# ── rules, separated from the crawl so --self-test can exercise them ─────────
def page_findings(rec):
    """Indexation findings for one crawled record. Empty list means clean."""
    out = []
    url, status = rec["url"], rec.get("status")
    if status != 200:
        # A redirect is only a finding when the sitemap pointed at it.
        if rec.get("in_sitemap") and status in (301, 302, 307, 308):
            out.append(("sitemap URL redirects", "%s -> %s" % (status, rec.get("final"))))
        elif status and status >= 400:
            out.append(("HTTP %s" % status, rec.get("final") or url))
        return out

    if "title" not in rec:
        return out                       # non-HTML (agents.md, llms.txt, feeds)

    robots = (rec.get("robots") or "") + " " + (rec.get("x_robots") or "")
    noindexed = "noindex" in robots.lower()
    matched = next((p for p in NOINDEX_EXPECTED if p in url), None)
    should_noindex = matched is not None

    if noindexed and not should_noindex:
        out.append(("noindex on a page that should be indexable", robots.strip()))
    if not noindexed and should_noindex:
        out.append(("indexable but is a %s URL (%s)"
                    % (matched, NOINDEX_EXPECTED[matched]), "no robots directive"))

    can = rec.get("canonical")
    if not can:
        out.append(("no canonical", url))
    else:
        if not can.startswith("http"):
            out.append(("canonical is not absolute", can))
        elif can.rstrip("/") != rec.get("final", url).rstrip("/"):
            out.append(("canonical points elsewhere", can))

    if not rec.get("title"):
        out.append(("no title", url))
    if not rec.get("description"):
        out.append(("no meta description", url))
    if rec.get("h1", 1) != 1:
        out.append(("h1 count is %s" % rec.get("h1"), url))
    return out


def duplicates(records):
    """Duplicate titles and descriptions among distinct indexable pages.

    Keyed on the FINAL url, and each final url counted once. An earlier version
    keyed on the requested url and reported /pages/privacy-policy as a duplicate
    of /policies/privacy-policy -- they are the same page, reached through a 301
    that is working exactly as intended. A redirect is not a duplicate.
    """
    out = {}
    for field in ("title", "description"):
        acc = collections.defaultdict(set)
        for r in records:
            v = (r.get(field) or "").strip()
            if v and r.get("status") == 200:
                acc[v].add(r.get("final") or r["url"])
        out[field] = {v: sorted(u) for v, u in acc.items() if len(u) > 1}
    return out


def sitemap_urls():
    """Every URL in every sitemap, following the index."""
    import re
    seen, out = set(), []
    todo = [BASE.rstrip("/") + "/sitemap.xml"]
    while todo:
        u = todo.pop(0)
        if u in seen:
            continue
        seen.add(u)
        try:
            _, body = get(u)
        except Exception:                                      # noqa: BLE001
            continue
        locs = re.findall(r"<loc>([^<]+)</loc>", body)
        locs = [l.replace("&amp;", "&") for l in locs]
        if "<sitemapindex" in body:
            todo += locs
        else:
            out += locs
    return out


def parameter_check():
    """Shopify parameter and pagination behaviour, tested rather than assumed."""
    import re
    tests = [
        ("tracking parameter", BASE + "/?utm_source=test&utm_medium=audit"),
        ("collection sort", BASE + "/collections/all?sort_by=price-ascending"),
        ("collection page 1 param", BASE + "/collections/all?page=1"),
    ]
    rows = []
    for label, u in tests:
        try:
            status, body = get(u)
            m = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', body)
            can = m.group(1) if m else None
            rows.append((label, u, status, can))
        except Exception as e:                                 # noqa: BLE001
            rows.append((label, u, "error: %s" % type(e).__name__, None))
    return rows


def crawl():
    """Run the existing site audit and take its JSON."""
    p = subprocess.run([sys.executable, os.path.join(HERE, "audit-seo-site.py"),
                        "--json"], capture_output=True, text=True, timeout=1800)
    if not p.stdout.strip():
        raise SystemExit("audit-seo-site.py produced no JSON:\n" + p.stderr[-2000:])
    return json.loads(p.stdout)


def report(records, sm, dups, params):
    findings = []
    for r in records:
        for kind, detail in page_findings(r):
            findings.append((kind, r["url"], detail))
    by_kind = collections.Counter(k for k, _, _ in findings)

    html_pages = [r for r in records if "title" in r]
    in_sm = {u.rstrip("/") for u in sm}
    crawled = {r["url"].rstrip("/") for r in records}
    missing = sorted(in_sm - crawled)
    # Feeds, oembed endpoints and deliberately-noindexed families are not
    # sitemap omissions; they are URL types a sitemap should never list.
    extra = sorted(u for u in crawled - in_sm
                   if not any(p in u for p in NOINDEX_EXPECTED)
                   and not u.endswith((".atom", ".oembed", ".json", ".xml")))

    t = ["# Indexation audit", "",
         "Generated by `scripts/audit-indexation.py` against the live site. "
         "Regenerate rather than editing by hand.", "",
         "| | |", "| --- | --- |",
         "| URLs crawled | %d |" % len(records),
         "| HTML pages | %d |" % len(html_pages),
         "| URLs in sitemaps | %d |" % len(sm),
         "| Findings | %d |" % len(findings), "",
         "Nothing in this report has been acted on automatically. Noindexing or "
         "redirecting a URL is a decision about intent, and this file only "
         "supplies the evidence for it.", "",
         "## Findings by kind", ""]
    if by_kind:
        t += ["| Finding | Count |", "| --- | ---: |"]
        for k, n in by_kind.most_common():
            t += ["| %s | %d |" % (k, n)]
        t += ["", "### Every finding", "", "| Finding | URL | Detail |",
              "| --- | --- | --- |"]
        for k, u, d in sorted(findings):
            t += ["| %s | `%s` | %s |" % (k, u.replace(BASE, "") or "/", d)]
    else:
        t += ["None. Every crawled page is indexable, self-canonical, has one "
              "h1, a title and a description.", ""]

    t += ["", "## Sitemap agreement", "",
          "| Check | Count |", "| --- | ---: |",
          "| In a sitemap but not reached by the crawl | %d |" % len(missing),
          "| Reached by the crawl but in no sitemap | %d |" % len(extra), ""]
    if missing:
        t += ["Sitemap URLs the crawl did not reach:", ""]
        t += ["- `%s`" % u.replace(BASE, "") for u in missing[:30]] + [""]
    if extra:
        t += ["Crawled but absent from every sitemap — check each is meant to be "
              "indexable:", ""]
        t += ["- `%s`" % u.replace(BASE, "") for u in extra[:30]] + [""]

    t += ["## Duplicate metadata", ""]
    any_dup = False
    for field in ("title", "description"):
        d = dups[field]
        if d:
            any_dup = True
            t += ["### Duplicate %ss — %d" % (field, len(d)), "",
                  "| Value | URLs |", "| --- | --- |"]
            for v, urls in sorted(d.items()):
                t += ["| %s | %s |" % (v[:80],
                                       ", ".join("`%s`" % u.replace(BASE, "")
                                                 for u in urls))]
            t += [""]
    if not any_dup:
        t += ["No two indexable pages share a title or a meta description.", ""]

    t += ["## Parameter and pagination behaviour", "",
          "Tested against the live store rather than assumed from Shopify's "
          "documentation.", "",
          "| Case | URL | Status | Canonical |", "| --- | --- | ---: | --- |"]
    for label, u, status, can in params:
        t += ["| %s | `%s` | %s | %s |" % (
            label, u.replace(BASE, ""), status,
            ("`%s`" % can.replace(BASE, "")) if can else "—")]
    t += ["", "A tracking parameter that canonicalises back to the clean URL is "
          "the behaviour you want; one that self-canonicalises would split "
          "signals across every campaign link.", ""]
    return "\n".join(t) + "\n"


def coverage_section(path):
    """Fold in what Google has actually done, from index-coverage.py.

    This is the only source that settles "is it indexed". A page can be
    perfectly crawlable, self-canonical and in the sitemap while Google has
    simply chosen not to fetch it, and no amount of on-page auditing shows that.
    """
    import re
    raw = open(path, encoding="utf-8").read()
    rows, summary = [], []
    for line in raw.splitlines():
        m = re.match(r"^(/\S+)\s{2,}(.+?)\s{2,}(\S+)\s*$", line)
        if m:
            rows.append((m.group(1), m.group(2).strip(), m.group(3)))
            continue
        m = re.match(r"^\s{2}(\D.+?)\s{2,}(\d+)\s*$", line)
        if m:
            summary.append((m.group(1).strip(), int(m.group(2))))
    t = ["", "## What Google has actually done", "",
         "From the URL Inspection API via `scripts/index-coverage.py`. Everything "
         "above describes what the site *tells* a crawler; this is the only "
         "section that says what Google decided.", ""]
    if summary:
        t += ["| State | URLs |", "| --- | ---: |"]
        t += ["| %s | %d |" % (k, v) for k, v in summary]
    total = sum(v for _, v in summary)
    if summary and len(rows) != total:
        t += ["", "> The saved output held %d of %d rows, so the per-URL list "
              "below is omitted rather than shown incomplete. The counts above "
              "are the script's own totals and are unaffected." % (len(rows), total),
              ""]
        return "\n".join(t) + "\n"
    notind = [r for r in rows if r[1].startswith("Discovered")]
    if notind:
        t += ["", "### Discovered but not indexed — %d" % len(notind), "",
              "Google knows the URL exists and has chosen not to fetch it. On a "
              "site this new this is the normal state and resolves with age and "
              "links rather than with on-page changes. It is also the reason not "
              "to publish more pages: unindexed pages cannot rank, and adding to "
              "them does not help the ones already waiting.", ""]
        t += ["- `%s`" % r[0] for r in notind]
    t += ["", "_Regenerate with `scripts/index-coverage.py`, then pass the saved "
          "output to `--coverage`._", ""]
    return "\n".join(t) + "\n"


def self_test():
    ok, bad = [], []

    def check(name, got, want):
        (ok if got == want else bad).append("%s: got %r want %r" % (name, got, want))

    clean = {"url": BASE + "/pages/x", "final": BASE + "/pages/x", "status": 200,
             "title": "T", "description": "D", "canonical": BASE + "/pages/x",
             "robots": None, "x_robots": None, "h1": 1}
    check("clean page is silent", page_findings(clean), [])
    check("noindex on a content page fires",
          [k for k, _ in page_findings(dict(clean, robots="noindex, nofollow"))],
          ["noindex on a page that should be indexable"])
    check("tag archive noindex is expected",
          page_findings(dict(clean, url=BASE + "/blogs/guides/tagged/seo",
                             final=BASE + "/blogs/guides/tagged/seo",
                             canonical=BASE + "/blogs/guides/tagged/seo",
                             robots="noindex, follow")), [])
    check("policy page indexable is NOT a finding",
          page_findings(dict(clean, url=BASE + "/policies/refund-policy",
                             final=BASE + "/policies/refund-policy",
                             canonical=BASE + "/policies/refund-policy")), [])
    check("redirect is not a duplicate",
          duplicates([{"url": BASE + "/pages/p", "final": BASE + "/policies/p",
                       "status": 200, "title": "T"},
                      {"url": BASE + "/policies/p", "final": BASE + "/policies/p",
                       "status": 200, "title": "T"}])["title"], {})
    check("cart URL is expected to be noindexed",
          page_findings(dict(clean, url=BASE + "/cart", final=BASE + "/cart",
                             canonical=BASE + "/cart", robots="noindex")), [])
    check("indexable cart URL fires",
          [k for k, _ in page_findings(dict(clean, url=BASE + "/cart",
                                            final=BASE + "/cart",
                                            canonical=BASE + "/cart"))],
          ["indexable but is a /cart URL (Shopify cart)"])
    check("cross-canonical fires",
          [k for k, _ in page_findings(dict(clean, canonical=BASE + "/pages/y"))],
          ["canonical points elsewhere"])
    check("relative canonical fires",
          [k for k, _ in page_findings(dict(clean, canonical="/pages/x"))],
          ["canonical is not absolute"])
    check("missing canonical fires",
          [k for k, _ in page_findings(dict(clean, canonical=None))],
          ["no canonical"])
    check("two h1s fire",
          [k for k, _ in page_findings(dict(clean, h1=2))], ["h1 count is 2"])
    check("no description fires",
          [k for k, _ in page_findings(dict(clean, description=""))],
          ["no meta description"])
    check("404 fires",
          [k for k, _ in page_findings({"url": BASE + "/x", "status": 404,
                                        "final": BASE + "/x"})], ["HTTP 404"])
    check("non-HTML asset is silent",
          page_findings({"url": BASE + "/agents.md", "status": 200,
                         "final": BASE + "/agents.md"}), [])
    check("sitemap redirect fires",
          [k for k, _ in page_findings({"url": BASE + "/a", "status": 301,
                                        "final": BASE + "/b", "in_sitemap": True})],
          ["sitemap URL redirects"])
    check("duplicate titles found",
          sorted(duplicates([{"url": "u1", "status": 200, "title": "T"},
                             {"url": "u2", "status": 200, "title": "T"}])["title"]),
          ["T"])
    check("distinct titles are silent",
          duplicates([{"url": "u1", "status": 200, "title": "A"},
                      {"url": "u2", "status": 200, "title": "B"}])["title"], {})

    for l in ok:
        print("  ok   %s" % l)
    for l in bad:
        print("  FAIL %s" % l)
    print("\n%d passed, %d failed" % (len(ok), len(bad)))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crawl", help="reuse a saved audit-seo-site.py --json file")
    ap.add_argument("--coverage", help="saved index-coverage.py output, folded "
                                       "into the report as real Google state")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        raise SystemExit(self_test())

    records = json.load(open(a.crawl, encoding="utf-8")) if a.crawl else crawl()
    sm = sitemap_urls()
    in_sm = {u.rstrip("/") for u in sm}
    for r in records:
        r["in_sitemap"] = r["url"].rstrip("/") in in_sm
    dups = duplicates([r for r in records if "title" in r])
    params = parameter_check()

    os.makedirs(REPORTS, exist_ok=True)
    out = os.path.join(REPORTS, "indexation-audit.md")
    text = report(records, sm, dups, params)
    if a.coverage:
        text += coverage_section(a.coverage)
    open(out, "w", encoding="utf-8").write(text)
    n = sum(len(page_findings(r)) for r in records)
    print("crawled %d   sitemap %d   findings %d" % (len(records), len(sm), n))
    print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
