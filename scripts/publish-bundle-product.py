#!/usr/bin/env python3
"""Create or update the Complete Site Builder Stack bundle in Shopify.

The bundle is one SKU that delivers the three existing product archives as
three attachments. It deliberately does NOT contain a fourth combined archive:
a combined ZIP would have to be rebuilt and its checksum republished every time
any of the three changed, and the version it contained would be a fourth number
that could disagree with the other three.

Two assertions matter more here than on a single product.

1. The description must not state a price, a total, or a saving. Every one of
   those is rendered live by `sections/sbs-bundle-value.liquid` from the actual
   product prices. A number typed into the description is a number that goes
   stale the first time any price changes, and a stale saving on a bundle page
   is a misleading price claim rather than a typo.

2. The description must not carry a struck-through "was" figure, a percentage
   off, or an urgency claim. The store has never charged $197 in one
   transaction, so presenting it as a former price would be a fabricated
   discount -- the exact pattern the conversion toolkit prohibits by name.

The file counts are read from the three product directories rather than typed,
so the listing cannot claim a size the products do not have.

Usage: publish-bundle-product.py [--dry-run]
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shopify_api import gql, check_user_errors  # noqa: E402

ROOT = os.path.dirname(HERE)
HANDLE = "complete-site-builder-stack"
TITLE = "Complete Site Builder Stack"
PRICE = os.environ.get("SBS_BUNDLE_PRICE", "39.99")
# The price is set on CREATE only. On an update run it is left exactly as the
# store has it, unless --set-price is passed. Without this, re-running the
# script to change a description silently reverted the price to whatever this
# constant said -- which is how a price change made in the admin on 2026-09-13
# would have been undone by the next routine publish.
SET_PRICE = "--set-price" in sys.argv

SKU = "SBS-CCSTACK-V1"
SEO_TITLE = "Complete Site Builder Stack — Build, Rank, Convert"
SEO_DESC = ("All three Claude Code systems in one purchase: the Website Launch System, "
            "the SEO & Website Audit Toolkit and the Conversion & Revenue Optimization "
            "Toolkit. Three downloads, 267 files.")

# The three products the bundle contains, by directory and storefront handle.
PARTS = (
    ("Claude-Code-Website-Launch-System", "claude-code-website-launch-system"),
    ("Claude-Code-SEO-Website-Audit-Toolkit", "claude-code-seo-website-audit-toolkit"),
    ("Claude-Code-Conversion-Revenue-Optimization-Toolkit",
     "claude-code-conversion-revenue-optimization-toolkit"),
)

FIELDS = """
  id handle title status vendor productType
  variants(first:1){ nodes{ id price sku inventoryItem{ id requiresShipping measurement{ weight{ value unit } } } } }
"""

# Anything that states money in the description. The live section owns prices.
PRICE_SHAPED = re.compile(r"\$\s?\d[\d,]*(?:\.\d{2})?")
FAKE_DISCOUNT = (
    (r"\bwas\s+\$?\d", "a struck-through 'was' price"),
    (r"\b\d+\s*%\s*(?:off|discount|saving)", "a percentage discount"),
    (r"\blimited time\b", "an urgency claim"),
    (r"\bonly\s+\d+\s+(?:left|remaining|available)\b", "a scarcity claim"),
    (r"\bprice\s+(?:goes\s+up|increases|rises)\b", "a threatened price rise"),
    (r"\bnormally\s+\$?\d", "a claimed normal price"),
    (r"\bvalued?\s+at\s+\$?\d", "a claimed value"),
    (r"\bsave\s+\$?\d", "a stated saving"),
)


def part_counts():
    """Files and words across the three product directories."""
    files = words = 0
    per = []
    for d, _ in PARTS:
        p = os.path.join(ROOT, "product", d)
        if not os.path.isdir(p):
            raise SystemExit("missing product directory: %s" % p)
        f = w = 0
        for r, _dirs, fs in os.walk(p):
            for name in fs:
                f += 1
                if name.endswith(".md"):
                    w += len(io.open(os.path.join(r, name), encoding="utf-8",
                                     errors="ignore").read().split())
        per.append((d, f, w))
        files += f
        words += w
    return files, words, per


def audit_description(body, files, words):
    problems = []

    for m in PRICE_SHAPED.finditer(body):
        problems.append("description states money (%r) — the live section owns "
                        "every price" % m.group(0))
    for pattern, label in FAKE_DISCOUNT:
        m = re.search(pattern, body, re.I)
        if m:
            problems.append("description contains %s: %r" % (label, m.group(0)))

    # The two quantities the description does state must match the products.
    m = re.search(r"(\d{2,4})\s+files", body)
    if not m:
        problems.append("description does not state a file count")
    elif int(m.group(1)) != files:
        problems.append("description says %s files, the products hold %d"
                        % (m.group(1), files))

    m = re.search(r"([\d,]+)\s*(?:words|000 words)", body)
    if not m:
        problems.append("description does not state a word count")
    else:
        claimed = int(m.group(1).replace(",", ""))
        # Stated to the nearest thousand, so allow that much slack and no more.
        if abs(claimed - words) > 1000:
            problems.append("description says %s words, the products hold %d"
                            % (m.group(1), words))

    # Each component must be linked, or the bundle page cannot be checked.
    for _d, handle in PARTS:
        if "/products/%s" % handle not in body:
            problems.append("description does not link to /products/%s" % handle)
    return problems


def find():
    d = gql("query($q:String!){ products(first:5, query:$q){ nodes{ %s } } }" % FIELDS,
            {"q": "handle:%s" % HANDLE})
    for p in d["products"]["nodes"]:
        if p["handle"] == HANDLE:
            return p
    return None


def live_part_prices():
    """The three component prices, from the store, so the total is never typed."""
    out = []
    for _d, handle in PARTS:
        d = gql("query($q:String!){ products(first:5, query:$q){ nodes{ handle status "
                "variants(first:1){ nodes{ price } } } } }", {"q": "handle:%s" % handle})
        hit = next((p for p in d["products"]["nodes"] if p["handle"] == handle), None)
        if not hit:
            raise SystemExit("component product not found on the store: %s" % handle)
        if hit["status"] != "ACTIVE":
            raise SystemExit("component product %s is %s, not ACTIVE — a bundle cannot "
                             "contain a product customers cannot buy" % (handle, hit["status"]))
        out.append((handle, float(hit["variants"]["nodes"][0]["price"])))
    return out


def main():
    dry = "--dry-run" in sys.argv
    files, words, per = part_counts()
    body = io.open(os.path.join(ROOT, "content", "products", "complete-stack.html"),
                   encoding="utf-8").read()

    print("counted from the three product directories:")
    for d, f, w in per:
        print("  %-52s %3d files  %6s words" % (d, f, format(w, ",")))
    print("  %-52s %3d files  %6s words" % ("TOTAL", files, format(words, ",")))

    problems = audit_description(body, files, words)
    if problems:
        for p in problems:
            print("  FAIL %s" % p)
        raise SystemExit("refusing to publish a bundle listing that misstates itself")
    print("  description states no price and matches the products")

    parts = live_part_prices()
    total = sum(p for _h, p in parts)
    price = float(PRICE)
    print("\nlive component prices:")
    for h, p in parts:
        print("  %-52s $%.2f" % (h, p))
    print("  %-52s $%.2f" % ("bought separately", total))
    print("  %-52s $%.2f" % ("bundle", price))
    if price >= total:
        raise SystemExit("bundle price $%.2f is not below the separate total $%.2f — "
                         "a bundle that saves nothing should not be sold as one"
                         % (price, total))
    print("  %-52s $%.2f" % ("saving", total - price))

    existing = find()
    if dry:
        print("\n%s %s at $%s" % ("would update" if existing else "would create",
                                  HANDLE, PRICE))
        return 0

    payload = {
        "handle": HANDLE,
        "title": TITLE,
        "descriptionHtml": body,
        "vendor": "Site Builder Stack",
        "productType": "Digital Product",
        "status": "ACTIVE",
        "tags": ["bundle", "claude-code", "digital", "build", "seo", "conversion"],
        "templateSuffix": "complete-stack",
        "seo": {"title": SEO_TITLE, "description": SEO_DESC},
    }
    if existing:
        payload["id"] = existing["id"]
        d = gql("mutation($p:ProductUpdateInput!){ productUpdate(product:$p){ product{ %s } "
                "userErrors{ field message } } }" % FIELDS, {"p": payload})
        check_user_errors(d["productUpdate"], "productUpdate")
        prod, verb = d["productUpdate"]["product"], "updated"
    else:
        d = gql("mutation($p:ProductCreateInput!){ productCreate(product:$p){ product{ %s } "
                "userErrors{ field message } } }" % FIELDS, {"p": payload})
        check_user_errors(d["productCreate"], "productCreate")
        prod, verb = d["productCreate"]["product"], "created"

    variant = prod["variants"]["nodes"][0]
    vd = gql("""mutation($pid:ID!,$vars:[ProductVariantsBulkInput!]!){
                  productVariantsBulkUpdate(productId:$pid, variants:$vars){
                    productVariants{ id price sku
                      inventoryItem{ requiresShipping measurement{ weight{ value unit } } } }
                    userErrors{ field message } } }""",
             {"pid": prod["id"], "vars": [{
                 "id": variant["id"],
                 **({"price": PRICE} if (not existing or SET_PRICE) else {}),
                 "inventoryItem": {
                     "sku": SKU,
                     "requiresShipping": False,
                     "tracked": False,
                     "measurement": {"weight": {"value": 0.0, "unit": "GRAMS"}},
                 },
             }]})
    check_user_errors(vd["productVariantsBulkUpdate"], "productVariantsBulkUpdate")
    v = vd["productVariantsBulkUpdate"]["productVariants"][0]

    print("\n%s %s" % (verb, prod["handle"]))
    print("  price            $%s" % v["price"])
    print("  sku              %s" % v["sku"])
    print("  requiresShipping %s" % v["inventoryItem"]["requiresShipping"])
    print("  template suffix  complete-stack")
    print("\nDelivery: attach all THREE archives to this product in the digital-delivery")
    print("app. The Admin API cannot see attachments; only a fulfilled paid order proves")
    print("delivery works.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
