#!/usr/bin/env python3
"""Crawl the live storefront and report every broken or suspect link.

Usage: audit-live-links.py [baseUrl]

Checks internal links resolve, flags placeholder hrefs, theme-vendor links,
redirect chains, and reports the status of every distinct URL found.
"""
import os
import re
import time
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://sitebuilderstack.com").rstrip("/")
UA = {"User-Agent": "Mozilla/5.0 (compatible; sbs-link-audit/1.0)"}

SEEDS = ["/", "/products/claude-code-website-launch-system", "/cart",
         "/pages/contact", "/pages/licence", "/pages/disclaimer",
         "/policies/privacy-policy", "/policies/terms-of-service",
         "/policies/refund-policy", "/policies/shipping-policy",
         "/policies/contact-information",
         "/blogs/guides",
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
         "/pages/about"]


# Shopify rate-limits a fast crawl. Without pacing and a 429 retry this script
# reports rate limiting as broken links, which is a false alarm that looks
# exactly like a real outage.
PAUSE = float(os.environ.get("SBS_CRAWL_PAUSE", "1.0"))


def fetch(url, method="GET", _tries=6):
    """Fetch with pacing and a patient 429 retry.

    Shopify's rate-limit window outlasts a short exponential backoff, so a
    4-try/14-second retry still returned 429 and left seeds uncrawled -- which
    reports as "0 broken links" over a crawl that never happened. Back off up
    to ~2 minutes instead, and treat a final 429 as an explicit INCOMPLETE
    rather than folding it in with real findings.
    """
    for attempt in range(_tries):
        time.sleep(PAUSE)
        req = urllib.request.Request(url, method=method, headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status, r.read().decode("utf8", "replace"), r.url
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < _tries - 1:
                retry_after = e.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else min(60, 4 * (2 ** attempt))
                time.sleep(wait)
                continue
            return e.code, "", url
        except Exception as e:
            return None, f"{type(e).__name__}", url
    return 429, "", url


def hops(url):
    """Count redirect hops without following blindly."""
    n, cur = 0, url
    while n < 6:
        req = urllib.request.Request(cur, method="GET", headers=UA)
        opener = urllib.request.build_opener(NoRedirect)
        try:
            r = opener.open(req, timeout=20)
            return n, r.status, cur
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308):
                loc = e.headers.get("Location")
                if not loc:
                    return n, e.code, cur
                cur = urllib.parse.urljoin(cur, loc)
                n += 1
                continue
            return n, e.code, cur
        except Exception:
            return n, None, cur
    return n, None, cur


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


found = defaultdict(set)      # url -> set of pages linking to it
issues = []

for path in SEEDS:
    url = BASE + path
    status, body, _ = fetch(url)
    if status != 200:
        issues.append(f"SEED {path} returned {status}")
        continue
    # Editorial pages quote markup inside <code>/<pre> as examples. Scan only
    # the markup outside those, or an article about href="#" placeholders
    # reports itself.
    scannable = re.sub(r"<pre\b.*?</pre>", " ", body, flags=re.S)
    scannable = re.sub(r"<code\b.*?</code>", " ", scannable, flags=re.S)
    for href in re.findall(r'href="([^"]*)"', scannable):
        h = href.strip()
        if h in ("#", ""):
            issues.append(f"placeholder href on {path}: {href!r}")
            continue
        if h.startswith(("mailto:", "tel:", "javascript:", "data:")):
            continue
        if h.startswith("#"):
            if f'id="{h[1:]}"' not in body:
                issues.append(f"dead anchor on {path}: {h}")
            continue
        if h.startswith("/#"):
            continue                      # resolved on the homepage
        absu = urllib.parse.urljoin(url, h)
        if urllib.parse.urlparse(absu).netloc.endswith("sitebuilderstack.com"):
            found[absu.split("?")[0]].add(path)
        if re.search(r"novathemes|vinovathemes|themeforest|localhost|127\.0\.0\.1", absu, re.I):
            issues.append(f"suspect link on {path}: {absu}")

print(f"Crawled {len(SEEDS)} pages, found {len(found)} distinct internal URLs\n")
bad = 0
for url in sorted(found):
    n, status, final = hops(url)
    tag = "ok"
    if status is None:
        tag = "UNREACHABLE"; bad += 1
    elif status >= 400:
        tag = f"HTTP {status}"; bad += 1
    elif n > 1:
        tag = f"{n} REDIRECT HOPS"; bad += 1
    elif n == 1:
        tag = "301 (1 hop)"
    print(f"  {tag:<18} {url.replace(BASE,'') or '/'}")
    if tag not in ("ok", "301 (1 hop)"):
        print(f"                     linked from: {sorted(found[url])}")

# A run that was rate-limited did not crawl those pages at all. Reporting that
# alongside real findings lets an INCOMPLETE crawl read as a clean one, so it
# gets its own banner and its own exit code.
throttled = [i for i in issues if "429" in i]
real = [i for i in issues if "429" not in i]

print(f"\nIssues ({len(real)}):")
for i in real:
    print("  ✗", i)
print(f"\nBroken or multi-hop URLs: {bad}")

if throttled:
    print("\n" + "=" * 70)
    print(f"INCOMPLETE: {len(throttled)} URL(s) returned 429 after retries and were "
          "never crawled.")
    print("This result does NOT mean the site is clean -- those pages were not "
          "checked at all.")
    print("Re-run with a longer pause, e.g. SBS_CRAWL_PAUSE=3 "
          "scripts/audit-live-links.py")
    for i in throttled:
        print("  ·", i)
    print("=" * 70)

sys.exit(2 if throttled else (1 if (bad or real) else 0))
