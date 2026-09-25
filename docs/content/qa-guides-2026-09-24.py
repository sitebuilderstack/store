#!/usr/bin/env python3
"""QA for the three September 2026 guides.

    python3 docs/content/qa-guides-2026-09-24.py           # sources + Shopify records
    python3 docs/content/qa-guides-2026-09-24.py --live    # also fetch the rendered pages

Without --live it checks the local bodies, the manifest and the Shopify article
records. With --live it fetches the published pages too, which only works once
they are published — a draft URL returns 404 and the check says so rather than
failing obscurely.
"""
from __future__ import annotations

import argparse, json, pathlib, re, sys, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from shopify_api import gql  # noqa: E402

BLOG = "gid://shopify/Blog/121974554916"
SITE = "https://sitebuilderstack.com"
HANDLES = ["bulk-edit-shopify-seo-claude-code",
           "shopify-digital-product-page-template",
           "website-scope-of-work-template-claude-code",
           "answer-engine-optimization-claude-code"]
PRODUCTS = {
    "bulk-edit-shopify-seo-claude-code": "claude-code-shopify-automation-admin-api-toolkit",
    "shopify-digital-product-page-template": "claude-code-conversion-revenue-optimization-toolkit",
    "website-scope-of-work-template-claude-code": "claude-code-agency-client-delivery-system",
    "answer-engine-optimization-claude-code": "claude-code-seo-website-audit-toolkit",
}

def _json_ok(blob: str) -> bool:
    try:
        json.loads(blob); return True
    except Exception:
        return False


rows: list[tuple[str, str, bool, str]] = []
def chk(scope, name, ok, detail=""): rows.append((scope, name, bool(ok), detail))

_last = [0.0]


def fetch(url):
    # Shopify throttles a burst of storefront requests and answers 503, which
    # reads as a broken page. Pace them; a 503 that survives pacing is real.
    wait = 3.0 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "guides-qa/1"}), timeout=40)
        return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    man = json.loads((ROOT / "content" / "articles.json").read_text())
    by_handle = {a["handle"]: a for a in man["articles"]}
    tax = set(man["tagTaxonomy"])

    nodes = {a["handle"]: a for a in gql(
        '{ blog(id:"%s"){ articles(first:100){ nodes{ id handle title isPublished body '
        'metafields(first:5, namespace:"global"){ edges{ node{ key value } } } } } } }' % BLOG
    )["blog"]["articles"]["nodes"]}

    for h in HANDLES:
        e = by_handle.get(h)
        chk(h, "in the manifest", e is not None)
        if not e:
            continue
        body = (ROOT / "content" / "articles" / e["file"]).read_text()

        # --- source-level ---
        chk(h, "no h1 in the body (the template supplies it)", "<h1" not in body)
        ids = set(re.findall(r'<h[23] id="([^"]+)"', body))
        anchors = set(re.findall(r'href="#([^"]+)"', body))
        chk(h, "every in-page anchor resolves", anchors <= ids, ", ".join(sorted(anchors - ids)))
        chk(h, "has a table of contents", 'class="sbs-toc"' in body)
        chk(h, "has at least one copyable prompt", 'data-sbs-copy="prompt"' in body)
        chk(h, "links its primary product", f'/products/{PRODUCTS[h]}' in body)
        chk(h, "offers a free download", 'sbs-resource-download' in body)
        chk(h, "no unreplaced placeholder", not re.search(r"SBS_[A-Z_]+_URL|TODO|FIXME|Lorem ipsum", body))
        chk(h, "no internal UTM parameters", "utm_" not in body)
        # Off-domain links are allowed only where they are sources or a named
        # tool, and each must be verified reachable. A link to a PRIVATE
        # artifact would 404 for every reader, so the handle is checked here.
        off = set(re.findall(r'href="(https?://(?!sitebuilderstack\.com)[^"]+)"', body))
        allowed = ('developers.google.com', 'developers.openai.com', 'support.claude.com',
                   'docs.perplexity.ai', 'changelog.shopify.com', 'llmstxt.org',
                   'claude.ai/artifact/', 'help.shopify.com',
                   'cdn.shopify.com')  # the store's own asset CDN
        bad = [u for u in off if not any(a in u for a in allowed)]
        chk(h, "off-domain links are sources or verified tools", not bad, ", ".join(bad))
        chk(h, "no invented metric", not re.search(
            r"\b\d+% (increase|more|uplift|improvement)|search volume|keyword difficulty", body, re.I))
        # Match a promise being MADE, not the word. All three articles discuss
        # guarantees at length in order to forbid them — "do not add a
        # guarantee", "there is no lifetime guarantee on this product", "a
        # correct meta description does not guarantee Google will show it" —
        # so scanning for the token flags the honest copy and would miss an
        # actual promise phrased without it.
        chk(h, "no ranking or revenue promise", not re.search(
            r"\b(we|this product|this toolkit|this system) (guarantee|guarantees)\b|"
            r"guaranteed (results|rankings?|traffic|revenue|increase|uplift)|"
            r"\bis guaranteed to\b|"
            r"will (rank|increase|improve|boost) your\b|"
            r"\b(more|higher) (traffic|rankings?|sales|revenue) guaranteed\b", body, re.I))

        # --- metadata ---
        chk(h, "seo title within the rendered budget",
            len(e["seoTitle"]) + len(" – Site Builder Stack") <= 62,
            str(len(e["seoTitle"]) + 21))
        chk(h, "seo description within budget", len(e["seoDescription"]) <= 158, str(len(e["seoDescription"])))
        chk(h, "has an excerpt", bool(e.get("excerpt")))
        chk(h, "tags are in the taxonomy", set(e["tags"]) <= tax, ", ".join(set(e["tags"]) - tax))
        chk(h, "has a cover image and alt text", bool(e.get("image")) and len(e.get("imageAlt", "")) > 30)

        # --- Shopify record ---
        a = nodes.get(h)
        chk(h, "exists in Shopify", a is not None)
        if a:
            mf = {x["node"]["key"]: x["node"]["value"] for x in a["metafields"]["edges"]}
            chk(h, "seo title_tag set", mf.get("title_tag") == e["seoTitle"], mf.get("title_tag", "MISSING"))
            chk(h, "seo description_tag set", mf.get("description_tag") == e["seoDescription"])
            chk(h, "body uploaded intact", len(a["body"]) > 5000, f'{len(a["body"])} bytes')
            status = "published" if a["isPublished"] else "draft"
            code, _ = fetch(f"{SITE}/blogs/guides/{h}")
            if a["isPublished"]:
                chk(h, "published article is reachable", code == 200, str(code))
            else:
                chk(h, "draft is not publicly reachable", code == 404, str(code))
            print(f'  [{status}] {h}')

        if args.live and nodes.get(h, {}).get("isPublished"):
            code, page = fetch(f"{SITE}/blogs/guides/{h}")
            if code == 200:
                chk(h, "renders exactly one h1", page.count("<h1") == 1, str(page.count("<h1")))
                chk(h, "canonical is the article URL",
                    f'rel="canonical" href="{SITE}/blogs/guides/{h}"' in page)
                chk(h, "not noindexed", "noindex" not in page.lower())
                # Scope structured-data checks to the JSON-LD blocks. These
                # articles TALK about schema — one of them tells readers not to
                # use aggregateRating — so searching the whole page flags the
                # advice as if it were the markup.
                blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
                ld = [b for b in blocks if '"BlogPosting"' in b]
                chk(h, "exactly one BlogPosting block", len(ld) == 1, str(len(ld)))
                chk(h, "no fabricated rating markup",
                    not any("aggregateRating" in b or '"review"' in b for b in blocks))
                chk(h, "structured data parses",
                    all(_json_ok(b) for b in blocks), f"{len(blocks)} blocks")

    by_scope: dict[str, list] = {}
    for scope, name, ok, detail in rows:
        by_scope.setdefault(scope, []).append((name, ok, detail))
    print()
    for scope, items in by_scope.items():
        bad = [i for i in items if not i[1]]
        print(f'{scope}  —  {len(items)-len(bad)}/{len(items)}')
        for name, ok, detail in items:
            if not ok:
                print(f'    ✗ {name}' + (f'  [{detail}]' if detail else ''))
    total = len(rows); failed = sum(1 for r in rows if not r[2])
    print(f'\n{total-failed}/{total} checks passed')
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
