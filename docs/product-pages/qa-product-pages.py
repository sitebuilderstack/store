#!/usr/bin/env python3
"""Product-page QA matrix — all eight products, against a chosen theme.

    python3 docs/product-pages/qa-product-pages.py                  # preview theme
    python3 docs/product-pages/qa-product-pages.py --live           # the published theme
    python3 docs/product-pages/qa-product-pages.py --save DIR       # keep the HTML

Every check reads the RENDERED page, not the template, because the defects this
suite exists to catch were all invisible in the templates: a sticky bar whose
product came from a theme setting, a header link that resolved to the homepage,
and a closing call to action for a different product.
"""
from __future__ import annotations

import argparse, collections, html, http.cookiejar, json, pathlib, re, sys, urllib.request

PREVIEW_THEME = "191797854500"
SITE = "https://sitebuilderstack.com"

PRODUCTS = [
    ("launch-system",    "claude-code-website-launch-system",                   "The Claude Code Website Launch System",                  1999),
    ("seo-toolkit",      "claude-code-seo-website-audit-toolkit",               "Claude Code SEO & Website Audit Toolkit",                1999),
    ("cro-toolkit",      "claude-code-conversion-revenue-optimization-toolkit", "Claude Code Conversion & Revenue Optimization Toolkit",  1999),
    ("ops-system",       "claude-code-website-operations-maintenance-system",   "Claude Code Website Operations & Maintenance System",    3999),
    ("shopify-toolkit",  "claude-code-shopify-automation-admin-api-toolkit",    "Claude Code Shopify Automation & Admin API Toolkit",     3999),
    ("migration-system", "claude-code-website-migration-replatforming-system",  "Claude Code Website Migration & Replatforming System",   2999),
    ("agency-system",    "claude-code-agency-client-delivery-system",           "Claude Code Agency & Client Delivery System",            3999),
    ("complete-stack",   "complete-site-builder-stack",                         "Complete Site Builder Stack",                            3999),
]
HANDLES = {h for _, h, _, _ in PRODUCTS}


# A preview theme is served against a session cookie, not the query string
# alone: without a cookie jar every request comes back as the PUBLISHED theme,
# and the suite silently audits the wrong thing.
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))
_OPENER.addheaders = [("User-Agent", "SBS-product-QA/1.0")]


def fetch(url: str) -> str:
    return _OPENER.open(url, timeout=40).read().decode("utf-8", "replace")


def text_of(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, bool, str]] = []

    def check(self, product: str, name: str, ok: bool, detail: str = "") -> None:
        self.rows.append((product, name, bool(ok), detail))

    @property
    def failed(self) -> list[tuple[str, str, bool, str]]:
        return [r for r in self.rows if not r[2]]


def audit(handle: str, title: str, cents: int, body: str, rep: Report) -> None:
    p = handle

    # --- the page is the right page -------------------------------------
    rep.check(p, "renders the right product", f'data-sbs-product-handle="{handle}"' in body)
    price = f"${cents // 100}.{cents % 100:02d}"
    rep.check(p, "opening panel shows the live price",
              bool(re.search(r'data-sbs-product-price="' + re.escape(f"{cents/100:.2f}") + r'"', body)), price)

    # --- every purchase form is this product's ---------------------------
    forms = re.findall(r'<form[^>]*action="/cart/add"[^>]*id="([^"]+)"[^>]*>', body)
    variants = set(re.findall(r'<input type="hidden" name="id" value="(\d+)"', body))
    rep.check(p, "one variant id across every purchase form", len(variants) == 1, ",".join(sorted(variants)))
    rep.check(p, "opening purchase form present", "sbs-product-form" in forms, str(forms))
    rep.check(p, "closing purchase form present", "sbs-final-form" in forms, str(forms))
    rep.check(p, "sticky purchase form present", "sbs-sticky-form" in forms, str(forms))
    rep.check(p, "no duplicate form ids", len(forms) == len(set(forms)), str(forms))

    # --- the sticky bar follows this product -----------------------------
    m = re.search(r'<div class="sbs-sticky"[^>]*data-sbs-sticky-product="([^"]+)"', body)
    rep.check(p, "sticky bar carries this product", bool(m) and m.group(1) == handle,
              m.group(1) if m else "absent")
    st = re.search(r'class="sbs-sticky__title">([^<]*)', body)
    rep.check(p, "sticky bar shows this product's title", bool(st) and html.unescape(st.group(1)).strip() == title,
              st.group(1).strip() if st else "absent")
    sp = re.search(r'class="sbs-sticky__price">([^<]*)', body)
    rep.check(p, "sticky bar shows this product's price", bool(sp) and price in sp.group(1),
              sp.group(1).strip() if sp else "absent")

    # --- no primary purchase action for another product -------------------
    primaries = re.findall(r'<a class="sbs-btn sbs-btn--primary"[^>]*href="([^"]*)"', body)
    offsite = [h for h in primaries if h.startswith("/products/") and handle not in h]
    rep.check(p, "no primary button for a different product", not offsite, ", ".join(offsite))
    root_anchor = [h for h in primaries if h.startswith("/#")]
    rep.check(p, "no primary button to a homepage anchor", not root_anchor, ", ".join(root_anchor))

    # --- the cross-sell is secondary and labelled -------------------------
    cs = re.search(r'<section class="sbs-section sbs-center sbs-crosssell" data-sbs-crosssell="(\w+)"(.*?)</section>', body, re.S)
    if cs:
        rep.check(p, "cross-sell is secondary", cs.group(1) == "secondary", cs.group(1))
        rep.check(p, "cross-sell is labelled as another product", "sbs-eyebrow" in cs.group(2))
        rep.check(p, "cross-sell button is not primary", "sbs-btn--primary" not in cs.group(2))
    else:
        rep.check(p, "cross-sell section present", False, "absent")

    # --- header section links stay on this page ---------------------------
    hdr = re.search(r"<header.*?</header>", body, re.S)
    hdr = hdr.group(0) if hdr else ""
    for label, anchor in (("What&#39;s included", "included"), ("How it works", "walkthrough"), ("FAQ", "faq")):
        a = re.search(r'<a href="([^"]*)"[^>]*>\s*' + re.escape(label), hdr)
        rep.check(p, f"header “{text_of(label)}” stays on the page", bool(a) and a.group(1) == f"#{anchor}",
                  a.group(1) if a else "absent")
        rep.check(p, f"#{anchor} exists on the page", f'id="{anchor}"' in body)

    # --- the closing panel is real ----------------------------------------
    fin = re.search(r'<section class="sbs-section sbs-section--alt" id="get">(.*?)</section>', body, re.S)
    if fin:
        f = fin.group(1)
        rep.check(p, "closing panel states delivery", "Delivery" in f)
        rep.check(p, "closing panel states requirements", "You need" in f)
        rep.check(p, "closing panel states the licence", "Licence" in f)
        rep.check(p, "closing panel links the refund policy", "/policies/refund-policy" in f)
        rep.check(p, "closing panel shows this product's price", price in text_of(f))
    else:
        rep.check(p, "closing panel present", False, "absent")

    # --- catalogue consistency --------------------------------------------
    eco = re.search(r'<section class="sbs-section" id="also">(.*?)</section>', body, re.S)
    if eco:
        links = re.findall(r'href="/products/([a-z0-9-]+)"', eco.group(1))
        dup = [h for h, n in collections.Counter(links).items() if n > 1]
        rep.check(p, "no duplicate product card", not dup, ", ".join(dup))
        rep.check(p, "every other product is listed", set(links) == HANDLES - {handle},
                  "missing: " + ", ".join(sorted(HANDLES - {handle} - set(links))))

    # --- honesty ------------------------------------------------------------
    flat = text_of(re.sub(r"<script.*?</script>", "", body, flags=re.S))
    rep.check(p, "no “no video is published yet”", "No video is published yet" not in flat)
    rep.check(p, "no dead video player", "<video" not in body or "<source src=" in body)
    # The store's refund policy became final sale on 24 September 2026. The page
    # must say the same thing and must NOT offer the change-of-mind refund the
    # policy withdrew — the original defect was a page and a policy disagreeing,
    # and it disagrees just as badly in this direction.
    # The policy is final sale with no exceptions. A page that promises a refund
    # the policy does not give is the original defect pointing the other way, so
    # the rule is checked as "promises nothing the policy withholds".
    rep.check(p, "states final sale, as the policy does", "all sales are final" in flat.lower())
    rep.check(p, "links the refund policy", "/policies/refund-policy" in body)
    rep.check(p, "promises no remedy the policy withholds",
              not re.search(r"refund you|we will refund|refund is given|money back|"
                            r"satisfaction guarantee|decided it is not for you|"
                            r"supply a working|send a working|replacement (?:file|copy)|"
                            r"statutory rights", flat, re.I))
    # Scarcity has to be detected as a MECHANISM, not as a word. Two of these
    # products describe fake countdowns and untracked stock warnings at length
    # — in order to refuse them — so scanning for "countdown" or "hurry" flags
    # the honest copy and misses a real timer. Assertions are matched instead,
    # plus the markup a working countdown needs.
    rep.check(p, "no scarcity claim asserted",
              not re.search(r"only \d+ (?:left|remaining|in stock)|\d+ (?:people|others) (?:are )?viewing|"
                            r"offer expires|sale ends in|\d+ sold in the last", flat, re.I))
    rep.check(p, "no countdown mechanism in the markup",
              not re.search(r'data-countdown|class="[^"]*countdown|id="[^"]*countdown|<time[^>]*datetime="[^"]*"[^>]*>\s*\d+:\d\d', body, re.I))
    rep.check(p, "no “Complete purchase” mislabel", "complete purchase" not in flat.lower())
    rep.check(p, "no unresolved Liquid in the rendered page", "{{" not in flat and "{%" not in flat)
    rep.check(p, "no placeholder left public", not re.search(r"\bTODO\b|\bFIXME\b|Lorem ipsum", flat))

    # --- structured data ----------------------------------------------------
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S)
    products_ld = []
    for b in blocks:
        try:
            data = json.loads(b)
        except Exception:
            rep.check(p, "structured data parses", False, b[:60]); continue
        for node in (data if isinstance(data, list) else [data]):
            if isinstance(node, dict) and node.get("@type") == "Product":
                products_ld.append(node)
    rep.check(p, "exactly one Product schema", len(products_ld) == 1, str(len(products_ld)))
    if len(products_ld) == 1:
        offers = products_ld[0].get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        rep.check(p, "schema price matches the page", str(offers.get("price")) == f"{cents/100:.2f}",
                  str(offers.get("price")))
        rep.check(p, "no fabricated rating in schema",
                  "aggregateRating" not in products_ld[0] and "review" not in products_ld[0])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="audit the published theme instead of the preview")
    ap.add_argument("--save", metavar="DIR", help="write each rendered page here")
    args = ap.parse_args()

    suffix = "" if args.live else f"?preview_theme_id={PREVIEW_THEME}"
    rep = Report()
    out = pathlib.Path(args.save) if args.save else None
    if out:
        out.mkdir(parents=True, exist_ok=True)

    for _key, handle, title, cents in PRODUCTS:
        body = fetch(f"{SITE}/products/{handle}{suffix}")
        if out:
            (out / f"{handle}.html").write_text(body, encoding="utf-8")
        audit(handle, title, cents, body, rep)

    by_product: dict[str, list] = {}
    for prod, name, ok, detail in rep.rows:
        by_product.setdefault(prod, []).append((name, ok, detail))

    for prod, rows in by_product.items():
        bad = [r for r in rows if not r[1]]
        print(f"\n{prod}  —  {len(rows) - len(bad)}/{len(rows)}")
        for name, ok, detail in rows:
            if not ok:
                print(f"    ✗ {name}" + (f"  [{detail}]" if detail else ""))
        if not bad:
            print("    all checks passed")

    total, failed = len(rep.rows), len(rep.failed)
    print(f"\n{'PUBLISHED THEME' if args.live else 'PREVIEW THEME ' + PREVIEW_THEME}: {total - failed}/{total} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
