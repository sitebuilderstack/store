#!/usr/bin/env python3
"""Site-wide SEO audit against the live storefront.

Crawls from the homepage plus the sitemap, and reports per URL: status,
title, meta description, canonical, robots directives, h1 count, JSON-LD
validity and Open Graph completeness. Then reports duplicates.

Everything here reads the response body. Nothing is inferred from a template.

Exit codes: 0 clean, 1 findings, 2 the crawl itself was incomplete.

Usage: audit-seo-site.py [--json]
"""
import collections
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = os.environ.get("SBS_BASE", "https://sitebuilderstack.com")
UA = "sbs-seo-audit/1.0 (+https://sitebuilderstack.com)"
PAUSE = float(os.environ.get("SBS_CRAWL_PAUSE", "1.0"))

SKIP_PREFIX = ("/cart", "/checkout", "/account", "/orders", "/services",
               "/cdn/", "/apps/", "/tools/", "/search")


def fetch(url, tries=6):
    """GET with backoff. Raises after `tries`; a throttled run must not look clean."""
    last = None
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                   "Accept-Encoding": "gzip"})
        try:
            r = urllib.request.urlopen(req, timeout=45)
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return r.status, dict(r.headers), raw.decode("utf-8", "replace"), r.url
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = float(e.headers.get("Retry-After") or 0) or min(60, 4 * (2 ** attempt))
                last = e
                time.sleep(wait)
                continue
            raw = e.read()
            try:
                if e.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
            except Exception:
                pass
            return e.code, dict(e.headers), raw.decode("utf-8", "replace"), url
        except Exception as e:                       # noqa: BLE001
            last = e
            time.sleep(min(60, 4 * (2 ** attempt)))
    raise RuntimeError("giving up on %s: %s" % (url, last))


def sitemap_urls():
    out, queue, seen = [], [BASE + "/sitemap.xml"], set()
    while queue:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        _, _, body, _ = fetch(u)
        locs = [m.replace("&amp;", "&") for m in re.findall(r"<loc>([^<]+)</loc>", body)]
        if "<sitemapindex" in body:
            queue.extend(locs)
        else:
            out.extend(locs)
    return out


def internal_links(html, base_path):
    hrefs = re.findall(r'href="([^"#][^"]*)"', html)
    out = set()
    for h in hrefs:
        if h.startswith(BASE):
            h = h[len(BASE):] or "/"
        elif h.startswith(("http://", "https://", "mailto:", "tel:", "//")):
            continue
        if not h.startswith("/"):
            continue
        # Query strings are stripped so parameter variants do not multiply the
        # crawl — except pagination, which produces genuinely distinct indexable
        # URLs. Dropping those meant page two of a paginated list was never
        # checked, and it shipped a duplicate of page one's title tag unseen.
        frag = h.split("#")[0]
        if re.search(r"[?&]page=\d+$", frag):
            h = frag
        else:
            h = frag.split("?")[0]
        if any(h.startswith(p) for p in SKIP_PREFIX):
            continue
        out.add(h or "/")
    return out


def audit(url):
    status, headers, body, final = fetch(url)
    rec = {"url": url, "status": status, "final": final}
    if status != 200 or "text/html" not in headers.get("Content-Type", ""):
        return rec, set()

    def first(pat, flags=0):
        m = re.search(pat, body, flags)
        return m.group(1).strip() if m else None

    rec["title"] = first(r"<title>(.*?)</title>", re.S)
    rec["description"] = first(r'<meta name="description" content="([^"]*)"')
    rec["canonical"] = first(r'rel="canonical" href="([^"]*)"')
    rec["robots"] = first(r'<meta name="robots" content="([^"]*)"')
    rec["x_robots"] = headers.get("X-Robots-Tag")
    rec["h1"] = len(re.findall(r"<h1\b", body))
    rec["og"] = {k: bool(re.search(r'property="og:%s" content="[^"]+' % k, body))
                 for k in ("title", "description", "url", "image", "type")}
    rec["twitter_card"] = bool(re.search(r'name="twitter:card"', body))
    # Any DOUBLE-escaped entity in a meta tag, not just &amp;ndash;.
    #
    # This started as an ndash-only check and therefore missed &amp;amp;, which
    # is how the same bug shipped twice: og:title in one cycle, and the meta
    # description in the next, on every page whose description contained an
    # ampersand. The cause both times is escaping a value Shopify already
    # escaped; the fix both times is escape_once. Matching the whole family
    # means the third occurrence is caught by a test rather than by reading
    # the served markup.
    rec["entity_leak"] = bool(re.search(
        r'content="[^"]*&amp;(?:amp|lt|gt|quot|apos|nbsp|ndash|mdash|#\d+);', body))

    ld = []
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S):
        try:
            d = json.loads(m)
        except Exception as e:                        # noqa: BLE001
            ld.append({"error": str(e)[:80]})
            continue
        types = d.get("@type") or [x.get("@type") for x in d.get("@graph", [])]
        ld.append({"types": types})
    rec["ld"] = ld
    return rec, internal_links(body, url)


def evaluate(recs):
    """Rules, separated from the crawl so --self-test can exercise them."""
    findings, notes = [], []
    ok = [r for r in recs if r["status"] == 200 and "title" in r]

    # A platform routinely serves one page at more than one URL and resolves the
    # duplicate with a canonical: /pages/<h> alongside /policies/<h>, ?page=1
    # alongside the bare list URL. Where a crawled URL canonicalises onto
    # another crawled URL that returns 200, the shared title and description are
    # the platform working correctly, not a defect. Anything else still fails.
    by_url = {r["url"].rstrip("/"): r for r in ok}
    canonical_alias = {}
    for r in ok:
        c = (r.get("canonical") or "").rstrip("/")
        if c and c != r["url"].rstrip("/") and c in by_url:
            canonical_alias[r["url"].rstrip("/")] = c

    def alias_group(urls):
        """True if every URL here is either a canonical target or an alias of it."""
        keys = [u.rstrip("/") for u in urls]
        targets = {canonical_alias.get(k, k) for k in keys}
        return len(targets) == 1 and any(k in canonical_alias for k in keys)
    indexable = [r for r in ok if not (r.get("robots") or "").startswith("noindex")]

    for r in recs:
        if r["status"] >= 400:
            findings.append("HTTP %s  %s" % (r["status"], r["url"]))
        elif r["status"] in (301, 302) and r["final"] != r["url"]:
            findings.append("redirect %s -> %s" % (r["url"], r["final"]))

    for field in ("title", "description"):
        groups = collections.defaultdict(list)
        for r in indexable:
            if r.get(field):
                groups[r[field]].append(r["url"])
        for v, urls in groups.items():
            if len(urls) > 1:
                target = notes if alias_group(urls) else findings
                label = ("canonical alias shares its %s (expected)" % field
                         if target is notes else "duplicate %s (%d)" % (field, len(urls)))
                target.append("%s: %r\n      %s"
                              % (label, v[:60], "\n      ".join(urls)))

    for r in indexable:
        if not r.get("description"):
            findings.append("no meta description  %s" % r["url"])
        if r["h1"] != 1:
            findings.append("%d h1 elements  %s" % (r["h1"], r["url"]))
        if not r.get("canonical"):
            findings.append("no canonical  %s" % r["url"])
        elif r["canonical"].rstrip("/") != r["url"].rstrip("/"):
            if r["url"].rstrip("/") in canonical_alias:
                notes.append("alias, correctly canonicalised  %s -> %s"
                             % (r["url"].replace(BASE, ""), r["canonical"].replace(BASE, "")))
            else:
                findings.append("canonical mismatch  %s -> %s" % (r["url"], r["canonical"]))
        if r["entity_leak"]:
            findings.append("HTML entity leaking into a meta tag  %s" % r["url"])
        missing_og = [k for k, v in r["og"].items() if not v]
        if missing_og:
            findings.append("missing og:%s  %s" % (",".join(missing_og), r["url"]))
        if not r["twitter_card"]:
            findings.append("no twitter:card  %s" % r["url"])
        for block in r["ld"]:
            if "error" in block:
                findings.append("invalid JSON-LD (%s)  %s" % (block["error"], r["url"]))

    return findings, notes, ok, indexable



def _rec(url, **kw):
    r = {"url": BASE + url, "status": 200, "final": BASE + url,
         "title": "T " + url, "description": "D " + url,
         "canonical": BASE + url, "robots": None, "x_robots": None, "h1": 1,
         "og": {k: True for k in ("title", "description", "url", "image", "type")},
         "twitter_card": True, "entity_leak": False, "ld": [{"types": "WebPage"}]}
    r.update(kw)
    return r


def self_test():
    """Every rule must fire on a crafted failure. A rule that cannot go red is
    not a rule, and this is the only thing that proves the audit above means
    anything when it prints "No findings"."""
    cases = [
        ("404", [_rec("/gone", status=404)], "HTTP 404"),
        ("duplicate title",
         [_rec("/a", title="Same"), _rec("/b", title="Same")], "duplicate title"),
        ("duplicate description",
         [_rec("/a", description="Same"), _rec("/b", description="Same")],
         "duplicate description"),
        ("missing description", [_rec("/a", description=None)], "no meta description"),
        ("two h1", [_rec("/a", h1=2)], "2 h1 elements"),
        ("no canonical", [_rec("/a", canonical=None)], "no canonical"),
        ("canonical mismatch",
         [_rec("/a", canonical=BASE + "/b")], "canonical mismatch"),
        ("entity leak", [_rec("/a", entity_leak=True)], "HTML entity leaking"),
        ("missing og",
         [_rec("/a", og={"title": True, "description": False, "url": True,
                         "image": False, "type": True})], "missing og:"),
        ("no twitter card", [_rec("/a", twitter_card=False)], "no twitter:card"),
        ("invalid JSON-LD",
         [_rec("/a", ld=[{"error": "Expecting value"}])], "invalid JSON-LD"),
    ]
    bad = 0
    for name, recs, expect in cases:
        findings, notes, _, _ = evaluate(recs)
        hit = any(expect in f for f in findings)
        print("  %-22s %s" % (name, "fires" if hit else "DID NOT FIRE"))
        if not hit:
            bad += 1

    # And the inverse: a clean record must produce nothing.
    findings, notes, _, _ = evaluate([_rec("/a")])
    print("  %-22s %s" % ("clean record",
                          "silent" if not findings else "FALSE POSITIVE: %s" % findings))
    if findings:
        bad += 1

    # Noindex pages are excluded from the duplicate and completeness rules.
    findings, _, _, _ = evaluate([_rec("/a", robots="noindex, follow",
                                       description=None, twitter_card=False)])
    print("  %-22s %s" % ("noindex exempt",
                          "silent" if not findings else "WRONGLY FLAGGED: %s" % findings))
    if findings:
        bad += 1

    # A crawled URL canonicalising onto another crawled URL is the platform
    # resolving its own duplicate: a note, never a finding.
    for label, pair in [
        ("policy alias -> note",
         [_rec("/policies/privacy-policy", title="P", description="P"),
          _rec("/pages/privacy-policy", title="P", description="P",
               canonical=BASE + "/policies/privacy-policy")]),
        ("?page=1 alias -> note",
         [_rec("/blogs/guides", title="G", description="G"),
          _rec("/blogs/guides?page=1", title="G", description="G",
               canonical=BASE + "/blogs/guides")]),
    ]:
        findings, notes, _, _ = evaluate(pair)
        okay = not findings and len(notes) >= 2
        print("  %-22s %s" % (label, "correct" if okay else
                              "WRONG findings=%s" % findings))
        if not okay:
            bad += 1

    # And the case the exemption must NOT swallow: two genuinely different pages
    # sharing a title, neither canonicalising onto the other.
    dupe = [_rec("/a", title="Same", description="Same"),
            _rec("/b", title="Same", description="Same")]
    findings, notes, _, _ = evaluate(dupe)
    hit = any("duplicate title" in f for f in findings)
    print("  %-22s %s" % ("real duplicate still", "fires" if hit else "SWALLOWED <-- BAD"))
    if not hit:
        bad += 1

    # A canonical pointing somewhere we never crawled is still a finding.
    off = [_rec("/a", canonical=BASE + "/never-crawled")]
    findings, _, _, _ = evaluate(off)
    hit = any("canonical mismatch" in f for f in findings)
    print("  %-22s %s" % ("offsite canonical", "fires" if hit else "SWALLOWED <-- BAD"))
    if not hit:
        bad += 1

    print("\n%s" % ("self-test passed" if not bad else "%d RULE(S) BROKEN" % bad))
    return 1 if bad else 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    seeds = sitemap_urls()
    seen, queue, recs, incomplete = set(), list(seeds) + [BASE + "/"], [], []
    while queue:
        u = queue.pop(0)
        u = u if u.startswith("http") else BASE + u
        key = u.rstrip("/") or BASE
        if key in seen:
            continue
        seen.add(key)
        try:
            rec, links = audit(u)
        except RuntimeError as e:
            incomplete.append(str(e))
            continue
        recs.append(rec)
        for l in links:
            if (BASE + l).rstrip("/") not in seen:
                queue.append(BASE + l)
        time.sleep(PAUSE)

    if "--json" in sys.argv:
        json.dump(recs, sys.stdout, indent=1)
        return 2 if incomplete else 0

    findings, notes, ok, indexable = evaluate(recs)

    print("crawled %d URLs, %d returned 200 HTML, %d indexable\n"
          % (len(recs), len(ok), len(indexable)))
    for r in sorted(ok, key=lambda x: x["url"]):
        noidx = " [noindex]" if (r.get("robots") or "").startswith("noindex") else ""
        flat = []
        for b in r["ld"]:
            t = b.get("types")
            if t is None:
                flat.append("INVALID")
            elif isinstance(t, list):
                flat.extend(str(x) for x in t)
            else:
                flat.append(str(t))
        print("%-62s h1=%d ld=%-44s%s"
              % (r["url"].replace(BASE, "") or "/", r["h1"], ",".join(flat) or "-", noidx))

    print()
    if incomplete:
        print("!! CRAWL INCOMPLETE — %d URL(s) could not be fetched:" % len(incomplete))
        for i in incomplete:
            print("   ", i)
        print("   Findings below are based on a partial crawl.\n")
    if notes:
        print("%d note(s) — expected platform behaviour, not defects:" % len(notes))
        for n in notes:
            print("  ·", n)
        print()
    if findings:
        print("%d finding(s):" % len(findings))
        for f in findings:
            print("  -", f)
    else:
        print("No findings.")
    return 2 if incomplete else (1 if findings else 0)


if __name__ == "__main__":
    sys.exit(main())
