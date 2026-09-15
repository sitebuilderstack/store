#!/usr/bin/env python3
"""Validate the cornerstone article set: anchors, cross-links, headings, hygiene."""
import io, json, os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = "content/articles"
# The five cornerstones cross-link as a complete cluster; the six gap
# articles link into the cornerstones and to their own neighbours, but are
# not required to link to all ten.
CORNERSTONES = {
    "01-build-website.html": "how-to-build-a-website-with-claude-code",
    "02-prompts.html": "best-claude-code-prompts-for-web-development",
    "03-claude-md.html": "production-claude-md-web-development",
    "04-shopify.html": "build-shopify-store-with-claude-code",
    "05-seo.html": "claude-code-seo-website-optimization",
}
GAP = {
    "28-shopify-admin-api.html": "shopify-admin-api-claude-code",
    "29-cro-workflow.html": "claude-code-conversion-rate-optimization",
    "30-conversion-audit.html": "ai-website-conversion-audit",
    "31-shopify-conversion-audit.html": "shopify-conversion-audit-claude-code",
    "32-landing-page-audit.html": "claude-code-landing-page-audit",
    "33-cro-prompts.html": "claude-code-cro-prompts",
    "06-subagents.html": "claude-code-subagents",
    "07-skills.html": "claude-code-skills",
    "08-plugins.html": "claude-code-plugins",
    "09-certification.html": "claude-code-certification",
    "10-enterprise.html": "claude-code-enterprise",
    "11-vibe-coding.html": "vibe-coding-tools",
    "12-github-actions.html": "claude-code-github-actions",
    "13-terminal-setup.html": "claude-code-terminal-setup",
    "14-mcp.html": "claude-code-mcp",
    "15-hooks.html": "claude-code-hooks",
    "16-website-audit.html": "claude-code-website-audit",
    "17-technical-seo-audit.html": "claude-code-technical-seo-audit",
    "18-claude-md-examples.html": "claude-md-examples-web-development",
    "19-shopify-seo.html": "shopify-seo-with-claude-code",
    "20-security-audit.html": "claude-code-website-security-audit",
    "21-search-console.html": "google-search-console-claude-code",
    "22-performance.html": "claude-code-performance-core-web-vitals",
    "23-accessibility-audit.html": "claude-code-accessibility-audit",
}
SLUGS = dict(CORNERSTONES)
SLUGS.update(GAP)
MIN_XLINKS = 3
TARGETS = {
    "01-build-website.html": (5000, 6000),
    "02-prompts.html": (4000, 5500),
    # Grew when four sections were added on measured Bing demand: how the file
    # loads, path-scoped rules, AGENTS.md interop, and auto memory.
    "03-claude-md.html": (4500, 6500),
    # Both grew when a direct-answer section was added on Search Console
    # evidence ("connect shopify to claude code", "claude code seo").
    # Raised from 6500 on 2026-09-08, deliberately and not to make a failing
    # check pass. Both engines rank this site best for Shopify + Claude Code
    # queries -- Bing puts it at positions 1-5 across ~27 of them -- and two
    # sections were added to answer queries the search data actually records:
    # Theme Check with machine-readable output, and the repository layout.
    # This is the deepest guide on the site by design. If it passes 7500,
    # split it rather than raising this again.
    "04-shopify.html": (5000, 7500),
    "05-seo.html": (5000, 6500),
    "06-subagents.html": (1400, 3000),
    "07-skills.html": (1400, 3000),
    "08-plugins.html": (1400, 3000),
    "09-certification.html": (1400, 3000),
    "10-enterprise.html": (1400, 3000),
    "11-vibe-coding.html": (1400, 3000),
    # Raised from 3000 on 2026-09-08. The guide gained a security section
    # (pull_request_target, least privilege, prompt injection, fork PRs) and
    # five more troubleshooting cases. It had neither, in a guide about
    # running a model over code strangers can write. Split it rather than
    # raising this again.
    "12-github-actions.html": (1400, 4200),
    "13-terminal-setup.html": (1400, 3000),
    "14-mcp.html": (1400, 3000),
    "15-hooks.html": (1400, 3000),
    # The four cluster-supporting guides: longer than the gap set because each
    # carries worked code or a measured findings table, shorter than a pillar.
    "16-website-audit.html": (1800, 3200),
    "17-technical-seo-audit.html": (1800, 3200),
    "18-claude-md-examples.html": (1800, 3400),
    "19-shopify-seo.html": (1800, 3200),
    "20-security-audit.html": (2000, 3600),
    "21-search-console.html": (2000, 3600),
    "22-performance.html": (2000, 3600),
    "23-accessibility-audit.html": (2000, 3600),
    "28-shopify-admin-api.html": (1800, 3200),
    # The conversion cluster. Shorter bands than the platform guides on
    # purpose: each answers one question and stops, and padding them to the
    # length of a platform walkthrough would be exactly the filler the brief
    # they were written against forbids.
    "29-cro-workflow.html": (1400, 2600),
    "30-conversion-audit.html": (1000, 2200),
    "31-shopify-conversion-audit.html": (1000, 2200),
    "32-landing-page-audit.html": (1000, 2200),
    "33-cro-prompts.html": (1000, 2200),
}
# Free resource pages are legitimate internal link targets; anything else
# under /pages/ is a typo until it is added here deliberately.
RESOURCE_PAGES = {
    "/pages/resources",
    "/pages/production-claude-md-starter",
    "/pages/claude-code-launch-checklist",
    "/pages/claude-code-seo-checklist",
    "/pages/claude-code-security-checklist",
    "/pages/claude-code-website-audit-checklist",
    "/pages/about",
    "/pages/contact",
    "/pages/case-study",
}
# Everything below is DERIVED rather than listed. The hand-maintained version
# of this set went stale three times in one sprint -- it did not know about the
# four tool pages, the two newer products, the bundle, or a guide that had been
# published for weeks -- and each time it reported a working link as a typo.
# A list that cries wolf gets bypassed, which is worse than no check.
def _derived_paths():
    import json as _json
    out = set()

    # Guides, from the manifest rather than from SLUGS, so a guide added to the
    # site is a valid target immediately.
    try:
        d = _json.load(io.open(os.path.join(ROOT, "content", "articles.json"), encoding="utf-8"))
        arts = d if isinstance(d, list) else d.get("articles", d)
        for a in (arts if isinstance(arts, list) else arts.values()):
            out.add("/blogs/guides/" + a["handle"])
    except Exception:                                          # noqa: BLE001
        pass

    # Free resources, tools, hubs and products, from the graph and registries.
    try:
        r = _json.load(io.open(os.path.join(ROOT, "resources", "resources.json"), encoding="utf-8"))
        out.add("/pages/" + r["hub"]["handle"])
        for x in r["pages"]:
            out.add("/pages/" + x["handle"])
    except Exception:                                          # noqa: BLE001
        pass
    try:
        g = _json.load(io.open(os.path.join(ROOT, "content", "content-graph.json"), encoding="utf-8"))
        for x in g.get("tools", {}).values():
            out.add("/pages/" + x["handle"])
        for x in g.get("products", {}).values():
            out.add("/products/" + x["handle"])
        for x in g.get("pillars", {}).values():
            out.add(x["url"].rstrip("/"))
    except Exception:                                          # noqa: BLE001
        pass

    # Pages published by publish-pages.py, read from its own registry.
    try:
        src = io.open(os.path.join(ROOT, "scripts", "publish-pages.py"), encoding="utf-8").read()
        for h in re.findall(r'"handle":\s*"([a-z0-9-]+)"', src):
            out.add("/pages/" + h)
    except Exception:                                          # noqa: BLE001
        pass
    return out


VALID_PATHS = ({"/blogs/guides/" + s for s in SLUGS.values()} | RESOURCE_PAGES
               | _derived_paths() | {
    "/blogs/guides", "/", "/#buy", "/pages/tools", "/collections/all",
    "/policies/privacy-policy", "/policies/refund-policy",
    "/policies/terms-of-service",
})

def _product_handles():
    import json as _json
    try:
        g = _json.load(io.open(os.path.join(ROOT, "content", "content-graph.json"),
                               encoding="utf-8"))
        out = {p["handle"] for p in g.get("products", {}).values() if p.get("handle")}
        if out:
            return sorted(out)
    except Exception:                                          # noqa: BLE001
        pass
    return ["claude-code-website-launch-system"]


PRODUCT_HANDLES = _product_handles()


def strip_pre(s):
    return re.sub(r"<pre\b.*?</pre>", " ", s, flags=re.S)

# The layout appends " – Site Builder Stack" (21 characters) to every title
# that does not already contain the shop name, so the manifest's seoTitle has a
# budget of 62 - 21. Google truncates a result title around 580 CSS pixels,
# which is roughly 60 characters; a description past ~158 truncates mid-sentence
# rather than ending on a reason to click. Both are checked here because both
# regressed silently once already.
TITLE_SUFFIX = len(" – Site Builder Stack")
MAX_TITLE = 62
MAX_DESC = 158

fail = []
warn = []

for fn, slug in SLUGS.items():
    p = os.path.join(DIR, fn)
    src = io.open(p, encoding="utf-8").read()
    body = strip_pre(src)

    # --- ids and anchors ---
    ids = set(re.findall(r'\bid="([^"]+)"', src))
    frags = [m for m in re.findall(r'href="#([^"]+)"', src)]
    for f in frags:
        if f not in ids:
            fail.append(f"{fn}: TOC/in-page link #{f} has no matching id")

    dup = [i for i in ids if list(re.findall(r'\bid="([^"]+)"', src)).count(i) > 1]
    for d in set(dup):
        fail.append(f"{fn}: duplicate id {d!r}")

    # --- internal links ---
    internal = re.findall(r'href="(/[^"]*)"', src)
    for href in internal:
        base = href.split("#")[0] or "/"
        if href not in VALID_PATHS and base not in VALID_PATHS:
            fail.append(f"{fn}: unknown internal link {href}")
        if href.rstrip("/") == "/blogs/guides/" + slug:
            fail.append(f"{fn}: links to itself")

    # --- cross-link coverage ---
    linked = {h.split("/blogs/guides/")[-1].split("#")[0]
              for h in internal if "/blogs/guides/" in h and h.count("/") > 2}
    if fn in CORNERSTONES:
        # the five cornerstones must form a complete cluster
        missing = set(CORNERSTONES.values()) - {slug} - linked
        if missing:
            fail.append(f"{fn}: cornerstone missing cross-links to {sorted(missing)}")
    else:
        if len(linked) < MIN_XLINKS:
            fail.append(f"{fn}: only {len(linked)} cross-links, want >= {MIN_XLINKS}")
        if not (set(CORNERSTONES.values()) & linked):
            fail.append(f"{fn}: links to no cornerstone article")

    # --- product CTA count (2-3 expected across article) ---
    # Any product, not just the flagship. This counted only
    # /products/claude-code-website-launch-system, which was correct when the
    # store sold one product and silently wrong afterwards: a conversion guide
    # correctly pointing at the conversion toolkit scored zero CTAs and warned.
    # Derived from the graph so a fifth product needs no edit here.
    ctas = sum(internal.count("/products/" + h) for h in PRODUCT_HANDLES)

    # --- heading hierarchy (no skipped levels) ---
    heads = [(int(m.group(1)), re.sub(r"<[^>]+>", "", m.group(2)).strip())
             for m in re.finditer(r"<h([2-4])[^>]*>(.*?)</h\1>", body, flags=re.S)]
    prev = 2
    for lvl, txt in heads:
        if lvl > prev + 1:
            fail.append(f"{fn}: heading skip h{prev}->h{lvl} at {txt[:50]!r}")
        prev = lvl
    if not heads:
        fail.append(f"{fn}: no headings")

    # --- no h1 (theme renders it) ---
    if re.search(r"<h1\b", src):
        fail.append(f"{fn}: contains an h1; the section template renders it")

    # --- external links must be https + rel=noopener ---
    for m in re.finditer(r'<a\s+href="(https?://[^"]+)"([^>]*)>', src):
        url, attrs = m.group(1), m.group(2)
        if url.startswith("http://"):
            fail.append(f"{fn}: non-https external link {url}")
        if "noopener" not in attrs:
            fail.append(f"{fn}: external link without rel=noopener: {url}")

    # --- unclosed / stray tags sanity ---
    for tag in ("pre", "table", "nav", "ol", "ul", "li", "p", "code", "aside",
                "span", "figure", "figcaption"):
        o = len(re.findall(r"<%s\b" % tag, src))
        c = len(re.findall(r"</%s>" % tag, src))
        if o != c:
            fail.append(f"{fn}: <{tag}> open={o} close={c}")

    # --- hygiene: no fabricated-looking metrics, no placeholders ---
    for pat, msg in [
        (r"\blorem ipsum\b", "lorem ipsum"),
        (r"\bTODO\b|\bTKTK\b|\bXXX\b", "placeholder marker"),
        (r"\b\d[\d,]*\s+(?:monthly )?searches?\s+per month\b", "invented search volume"),
        (r"\bkeyword difficulty\s*[:=]\s*\d", "invented difficulty score"),
        (r"\bshopify-client-id\b|\bshopify-secret\b", "credential path reference"),
        (r"shpat_|shpca_|shppa_", "Shopify token prefix"),
    ]:
        for m in re.finditer(pat, src, flags=re.I):
            fail.append(f"{fn}: {msg} -> {src[max(0,m.start()-30):m.end()+30]!r}")

    # --- figures: informative images need alt, dimensions, lazy loading ---
    figs = re.findall(r"<figure>.*?</figure>", src, flags=re.S)
    if not figs:
        fail.append(f"{fn}: no diagram figure")
    for fg in figs:
        im = re.search(r"<img\s[^>]*>", fg)
        if not im:
            fail.append(f"{fn}: figure without img")
            continue
        tag = im.group(0)
        alt = re.search(r'alt="([^"]*)"', tag)
        if not alt or len(alt.group(1)) < 40:
            fail.append(f"{fn}: figure img alt missing or too short to be informative")
        for attr in ("width=", "height=", "loading=", "decoding=", "src="):
            if attr not in tag:
                fail.append(f"{fn}: figure img missing {attr}")
        if not re.search(r"<figcaption>.+?</figcaption>", fg, flags=re.S):
            fail.append(f"{fn}: figure without figcaption")
        srcm = re.search(r'src="([^"]+)"', tag)
        if srcm and not srcm.group(1).startswith("https://cdn.shopify.com/"):
            fail.append(f"{fn}: figure img not on the Shopify CDN")

    # --- word count ---
    text = re.sub(r"<[^>]+>", " ", src)
    words = len(html.unescape(text).split())
    lo, hi = TARGETS[fn]
    status = "ok" if lo <= words <= hi else "OUT OF RANGE"
    if status != "ok":
        fail.append(f"{fn}: {words} words, target {lo}-{hi}")

    print(f"{fn:26s} words={words:5d} [{lo}-{hi}] {status:12s} "
          f"h2={sum(1 for l,_ in heads if l==2):2d} ids={len(ids):2d} "
          f"xlink={len(linked)} cta={ctas}+1")
    # the sbs-article section renders one further CTA at the end of every article
    total_ctas = ctas + 1
    if not 2 <= total_ctas <= 3:
        warn.append(f"{fn}: {total_ctas} product CTAs incl. section CTA (want 2-3)")

# --- SEO metadata length, read from the manifest that publishes it ---
_m = json.load(io.open("content/articles.json", encoding="utf-8"))
for _a in _m["articles"]:
    _t = len(_a["seoTitle"]) + (0 if "Site Builder Stack" in _a["seoTitle"] else TITLE_SUFFIX)
    if _t > MAX_TITLE:
        fail.append("%s: rendered title is %d chars, max %d -> %r"
                    % (_a["handle"], _t, MAX_TITLE, _a["seoTitle"]))
    if len(_a["seoDescription"]) > MAX_DESC:
        fail.append("%s: meta description is %d chars, max %d"
                    % (_a["handle"], len(_a["seoDescription"]), MAX_DESC))
    if not _a["seoDescription"].strip():
        fail.append("%s: empty meta description" % _a["handle"])

print()
for w in warn:
    print("WARN:", w)
for f in fail:
    print("FAIL:", f)
print()
print(f"{len(fail)} failures, {len(warn)} warnings")
sys.exit(1 if fail else 0)
