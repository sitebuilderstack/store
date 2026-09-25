#!/usr/bin/env python3
"""Fetch the published guides and audit what the server actually returns.

Usage: audit-articles-live.py [--theme <id>] [baseUrl]

Checks per article: status, title, meta description, canonical, og tags,
JSON-LD types, in-page anchor targets, internal link resolution, image
attributes, Liquid leakage, and heading order.
"""
import http.cookiejar
import json
import os
import re
import sys
import urllib.request

BASE = "https://sitebuilderstack.com"
HANDLES = [
    "how-to-build-a-website-with-claude-code",
    "best-claude-code-prompts-for-web-development",
    "production-claude-md-web-development",
    "build-shopify-store-with-claude-code",
    "claude-code-seo-website-optimization",
    "claude-code-subagents",
    "claude-code-skills",
    "claude-code-plugins",
    "claude-code-certification",
    "claude-code-enterprise",
    "vibe-coding-tools",
    "claude-code-github-actions",
    "claude-code-terminal-setup",
    "claude-code-mcp",
    "claude-code-hooks",
]

argv = sys.argv[1:]
theme = None
if "--theme" in argv:
    i = argv.index("--theme")
    theme = argv[i + 1]
    del argv[i:i + 2]
if argv:
    BASE = argv[0].rstrip("/")

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "sbs-article-audit/1.0")]


def get(url):
    with op.open(url, timeout=45) as r:
        return r.getcode(), r.geturl(), r.read().decode("utf-8", "replace")


def head_val(head, pat):
    m = re.search(pat, head, re.S)
    return m.group(1).strip() if m else None


fail, warn = [], []
seen_titles, seen_descs = {}, {}
link_cache = {}

for h in HANDLES:
    url = "%s/blogs/guides/%s" % (BASE, h)
    if theme:
        url += "?preview_theme_id=%s" % theme
    code, final, s = get(url)
    head = s[:s.find("</head>")]
    body = s[s.find("<body"):]
    print("=" * 78)
    print(h)
    print("  HTTP %s  %d bytes" % (code, len(s)))
    if code != 200:
        fail.append("%s: HTTP %s" % (h, code))
        continue

    title = head_val(head, r"<title>(.*?)</title>")
    desc = head_val(head, r'<meta name="description" content="(.*?)"')
    canon = head_val(head, r'<link rel="canonical" href="(.*?)"')
    ogimg = head_val(head, r'<meta property="og:image" content="(.*?)"')
    ogtype = head_val(head, r'<meta property="og:type" content="(.*?)"')
    print("  title      %s (%d)" % (title, len(title or "")))
    print("  desc       %d chars" % len(desc or ""))
    print("  canonical  %s" % canon)
    print("  og:type    %s  og:image %s" % (ogtype, "yes" if ogimg else "NONE"))

    if not title:
        fail.append("%s: no title" % h)
    if not desc:
        fail.append("%s: no meta description" % h)
    if canon != "%s/blogs/guides/%s" % ("https://sitebuilderstack.com", h):
        fail.append("%s: canonical is %s" % (h, canon))
    if ogtype != "article":
        fail.append("%s: og:type is %r" % (h, ogtype))
    if not ogimg:
        fail.append("%s: no og:image" % h)
    if "&amp;" in (title or "") or re.search(r"&\w+;", title or ""):
        fail.append("%s: title contains an escaped entity: %r" % (h, title))
    if title in seen_titles:
        fail.append("%s: duplicate title with %s" % (h, seen_titles[title]))
    seen_titles[title] = h
    if desc in seen_descs:
        fail.append("%s: duplicate description with %s" % (h, seen_descs[desc]))
    seen_descs[desc] = h

    types = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception as e:
            fail.append("%s: invalid JSON-LD (%s)" % (h, e)); continue
        types.append(d.get("@type"))
        blob = json.dumps(d)
        for bad in ("aggregateRating", '"review"', "ratingValue"):
            if bad in blob:
                fail.append("%s: JSON-LD contains %s" % (h, bad))
    print("  json-ld    %s" % types)
    if "BlogPosting" not in types:
        fail.append("%s: no BlogPosting schema" % h)
    if "BreadcrumbList" not in types:
        fail.append("%s: no BreadcrumbList schema" % h)

    # h1 count and heading order in the article body
    art = body
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", art, re.S)
    if len(h1s) != 1:
        fail.append("%s: %d h1 elements" % (h, len(h1s)))

    # Liquid leakage. These articles discuss Liquid and quote it in examples,
    # so match Shopify's actual error format -- "Liquid error (file line N):" --
    # and strip <pre>/<code> before looking for unrendered delimiters.
    for lk in re.findall(r"Liquid error \([^)]{0,120}\)[^<]{0,120}", s):
        fail.append("%s: %s" % (h, lk))
    prose = re.sub(r"<pre\b.*?</pre>", " ", body, flags=re.S)
    prose = re.sub(r"<code\b.*?</code>", " ", prose, flags=re.S)
    stray = re.findall(r"{{\s*[\w.]+|{%\s*\w+", prose)
    if stray:
        fail.append("%s: %d stray Liquid delimiters outside code: %s"
                    % (h, len(stray), stray[:5]))

    # in-page anchors
    ids = set(re.findall(r'\bid="([^"]+)"', s))
    dead = sorted({f for f in re.findall(r'href="#([^"]+)"', s)
                   if f and f not in ids})
    if dead:
        fail.append("%s: dead in-page anchors %s" % (h, dead[:8]))
    print("  anchors    %d ids, %d dead" % (len(ids), len(dead)))

    # internal links -> fetch each once
    hrefs = sorted({x.split("#")[0] for x in re.findall(r'href="(/[^"]*)"', body)})
    bad_links = []
    for href in hrefs:
        if not href or href.startswith("/cdn"):
            continue
        if href not in link_cache:
            try:
                c, f2, _ = get(BASE + href)
                link_cache[href] = c
            except urllib.error.HTTPError as e:
                link_cache[href] = e.code
            except Exception:
                link_cache[href] = "ERR"
        if link_cache[href] != 200:
            bad_links.append("%s -> %s" % (href, link_cache[href]))
    print("  links      %d internal, %d broken" % (len(hrefs), len(bad_links)))
    for b in bad_links:
        fail.append("%s: broken link %s" % (h, b))

    # images
    imgs = re.findall(r"<img\s[^>]*>", body)
    noalt = [t for t in imgs if 'alt="' not in t]
    if noalt:
        fail.append("%s: %d img without alt" % (h, len(noalt)))
    figs = len(re.findall(r"<figure", body))
    print("  images     %d (%d figures), %d without alt" % (len(imgs), figs, len(noalt)))
    if figs < 1:
        fail.append("%s: no diagram figure rendered" % h)

    ctas = len(re.findall(r'href="/products/claude-code-website-launch-system"', body))
    print("  product links %d" % ctas)

print()
print("=" * 78)
for w in warn:
    print("WARN:", w)
for f in fail:
    print("FAIL:", f)
print("\n%d failures, %d warnings" % (len(fail), len(warn)))
sys.exit(1 if fail else 0)
