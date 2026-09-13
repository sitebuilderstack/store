#!/usr/bin/env python3
"""Validate Shopify's generated sitemap. Never replaces it -- reads it.

Fetches /sitemap.xml, walks the sitemap index, confirms the expected URLs
are present, then fetches a sample of the listed URLs and reports the real
status, canonical, and indexability of each.

Usage: validate-sitemap.py [baseUrl]
"""
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://sitebuilderstack.com").rstrip("/")
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

MUST_CONTAIN = [
    "/",
    "/products/claude-code-website-launch-system",
    "/blogs/guides/how-to-build-a-website-with-claude-code",
    "/blogs/guides/best-claude-code-prompts-for-web-development",
    "/blogs/guides/production-claude-md-web-development",
    "/blogs/guides/build-shopify-store-with-claude-code",
    "/blogs/guides/claude-code-seo-website-optimization",
    "/blogs/guides/claude-code-subagents",
    "/blogs/guides/claude-code-skills",
    "/blogs/guides/claude-code-plugins",
    "/blogs/guides/claude-code-certification",
    "/blogs/guides/claude-code-enterprise",
    "/blogs/guides/vibe-coding-tools",
    "/blogs/guides/claude-code-github-actions",
    "/blogs/guides/claude-code-terminal-setup",
    "/blogs/guides/claude-code-mcp",
    "/blogs/guides/claude-code-hooks",
    "/pages/about",
]

fail = []
note = []


# A noindexed URL has no business being in a sitemap: it costs a crawl to
# discover a directive that says not to index. There is currently no legitimate
# exception on this store — the one that existed (/collections/frontpage) was
# resolved by unpublishing the collection rather than by noindexing it. If an
# exception ever becomes genuinely necessary, add it here with the reason
# written out, rather than loosening the check.
EXPECTED_NOINDEX = {}


def get(url, decode=True):
    req = urllib.request.Request(url, headers={"User-Agent": "sbs-sitemap-check/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        raw = r.read()
        return r.getcode(), r.headers, (raw.decode("utf-8", "replace") if decode else raw)


def walk(url, depth=0, seen=None):
    """Return every <loc> under a sitemap or sitemap index."""
    seen = seen if seen is not None else set()
    if url in seen:
        return []
    seen.add(url)
    code, hdrs, body = get(url)
    ct = hdrs.get("Content-Type", "")
    print("%s%s  HTTP %s  %s  %d bytes" % ("  " * depth, url, code, ct.split(";")[0], len(body)))
    if code != 200:
        fail.append("%s: HTTP %s" % (url, code))
        return []
    if "xml" not in ct:
        fail.append("%s: content type is %r" % (url, ct))
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        fail.append("%s: not well-formed XML (%s)" % (url, e))
        return []

    if root.tag == NS + "sitemapindex":
        out = []
        for sm in root.findall(NS + "sitemap"):
            loc = sm.findtext(NS + "loc")
            out += walk(loc, depth + 1, seen)
        return out

    locs = [u.findtext(NS + "loc") for u in root.findall(NS + "url")]
    print("%s  -> %d URLs" % ("  " * depth, len(locs)))
    if len(locs) > 50000:
        fail.append("%s: %d URLs exceeds the 50,000 limit" % (url, len(locs)))
    if len(body.encode()) > 50 * 1024 * 1024:
        fail.append("%s: exceeds the 50MB uncompressed limit" % url)
    return locs


print("=" * 78)
print("SITEMAP")
print("=" * 78)
all_locs = walk(BASE + "/sitemap.xml")
paths = {re.sub(r"^https?://[^/]+", "", u) for u in all_locs}
print("\ntotal URLs across all sitemaps: %d" % len(all_locs))

print("\n" + "=" * 78)
print("REQUIRED URLS")
print("=" * 78)
for p in MUST_CONTAIN:
    ok = p in paths or (p == "/" and any(x in ("", "/") for x in paths))
    print("  %-62s %s" % (p, "present" if ok else "MISSING"))
    if not ok:
        fail.append("sitemap missing %s" % p)

print("\n" + "=" * 78)
print("SAMPLED URLS -- actual response, canonical, indexability")
print("=" * 78)
sample = sorted(all_locs)
for u in sample:
    try:
        code, hdrs, body = get(u)
    except Exception as e:
        print("  %-64s ERROR %s" % (u[:64], e))
        fail.append("%s: fetch failed" % u)
        continue
    ctype = hdrs.get("Content-Type", "").split(";")[0].strip()
    if ctype != "text/html":
        # /agents.md and friends are plain documents. A canonical link element
        # and a robots meta tag are HTML constructs and do not apply.
        print("  %-70s %s, %s (non-HTML, canonical check n/a)"
              % (u.replace(BASE, ""), code, ctype))
        if code != 200:
            fail.append("%s: HTTP %s" % (u, code))
        elif "noindex" in hdrs.get("X-Robots-Tag", "").lower():
            fail.append("%s: X-Robots-Tag noindex" % u)
        continue

    xr = hdrs.get("X-Robots-Tag", "")
    m = re.search(r'<link rel="canonical" href="(.*?)"', body)
    canon = m.group(1) if m else None
    mr = re.search(r'<meta name="robots" content="(.*?)"', body, re.S)
    robots = (mr.group(1) if mr else "") + " " + xr
    selfcanon = (canon == u)
    noindex = "noindex" in robots.lower()
    flags = []
    if code != 200:
        flags.append("HTTP %s" % code); fail.append("%s: HTTP %s" % (u, code))
    if not canon:
        flags.append("no canonical"); fail.append("%s: no canonical" % u)
    elif not selfcanon:
        flags.append("canonical -> %s" % canon); fail.append("%s: canonical is %s" % (u, canon))
    if noindex:
        flags.append("NOINDEX")
        if u.rstrip("/") in EXPECTED_NOINDEX:
            note.append("%s: noindex, and expected to be — %s"
                        % (u, EXPECTED_NOINDEX[u.rstrip("/")]))
        else:
            fail.append("%s: noindex" % u)
    print("  %-70s %s" % (u.replace(BASE, ""), ", ".join(flags) if flags else "200, self-canonical, indexable"))

print("\n" + "=" * 78)
for f in fail:
    print("FAIL:", f)
if note:
    print("\n%d documented exception(s):" % len(note))
    for n in note:
        print("  \u00b7", n)
print("\n%d failures" % len(fail))
sys.exit(1 if fail else 0)
