#!/usr/bin/env python3
"""Create or update the Website Migration & Replatforming System in Shopify.

Every quantity on the listing is read from the built bundle rather than typed:
scripts/validate-migration-system.py counts files, modules, commands and scripts, and
this refuses to publish a description that disagrees with any of them.

Two listing-specific assertions:

  * The price is exactly 29.99 and the description states no other price for
    this product. The launch specification names $29.99 and forbids every
    neighbour ($29, $29.00, $29.95, $39, $49, $59, $69); a typo here would be
    the most visible possible mistake. The comparison table may quote the
    other five products' current prices.
  * No predicted percentage improvement, no struck-through price, no urgency.

Digital product settings match the other five: no shipping, inventory not
tracked, zero weight. The file itself is attached privately in the store's
digital-delivery app, which is the one step this script cannot do.

The price is set on CREATE only; an update leaves the store's price alone
unless --set-price is passed (same guard as the other publishers).

Usage: publish-migration-system-product.py [--dry-run] [--check-only] [--set-price]

--check-only audits the description against the bundle and exits without
touching the network, so the test suite can run it on a clone with no
credentials.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util as _il
if "--check-only" not in sys.argv:
    from shopify_api import gql, check_user_errors  # noqa: E402

_spec = _il.spec_from_file_location("vo", os.path.join(HERE, "validate-migration-system.py"))
_vo = _il.module_from_spec(_spec)
_spec.loader.exec_module(_vo)

ROOT = os.path.dirname(HERE)
HANDLE = "claude-code-website-migration-replatforming-system"
TITLE = "Claude Code Website Migration & Replatforming System"
PRICE = "29.99"
FORBIDDEN_PRICES = ("$29.00", "$29.95", "$49", "$59", "$69")
SET_PRICE = "--set-price" in sys.argv

SKU = "SBS-CCWMRS-V1"
SEO_TITLE = "Claude Code Website Migration & Replatforming System | SiteBuilderStack"
SEO_DESC = ("Plan, execute, and validate website migrations with Claude Code. Preserve URLs, redirects, "
            "SEO, metadata, content, analytics, and critical functionality.")

FIELDS = """
  id handle title status vendor productType
  variants(first:1){ nodes{ id price sku inventoryItem{ id requiresShipping measurement{ weight{ value unit } } } } }
"""


def find():
    d = gql("query($q:String!){ products(first:5, query:$q){ nodes{ %s } } }" % FIELDS,
            {"q": "handle:%s" % HANDLE})
    for p in d["products"]["nodes"]:
        if p["handle"] == HANDLE:
            return p
    return None


def audit_description(body, counts):
    problems = []
    for name, n in (("files", counts["files"]), ("modules", counts["modules"]), ("commands", counts["commands"]),
                    ("scripts", counts["scripts"]), ("guides", counts["guides"]), ("checklists", counts["checklists"]), ("reports", counts["reports"])):
        if str(n) not in body:
            problems.append("description does not state the real %s count (%d)" % (name, n))
    # Every dollar figure in the description must be this product's price or
    # one of the three existing products' current prices (the comparison table).
    for m in re.finditer(r"\$(\d+(?:\.\d+)?)", body):
        if m.group(0) not in ("$%s" % PRICE, "$19.99", "$39.99"):  # the comparison table: the other five products' prices
            problems.append("description states a price that is not permitted: %s" % m.group(0))
    for bad in FORBIDDEN_PRICES:
        if bad in body:
            problems.append("description contains a forbidden price: %s" % bad)
    # "$29" and "$39" are forbidden as this product's price; they may only appear as the start of $29.99 / $39.99
    for m in re.finditer(r"\$(29|39)(?!\.99)\b", body):
        problems.append("description contains a forbidden price: %s" % m.group(0))
    if "$%s" % PRICE in body and body.count("$%s" % PRICE) != 1:
        problems.append("the price should appear exactly once in the description (the comparison table)")
    if "$%s" % PRICE not in body:
        problems.append("description does not state the price $%s" % PRICE)
    for m in _vo.PREDICTED_LIFT.finditer(body):
        if not _vo.negated(body, m.start()):
            problems.append("description predicts a percentage improvement: %r" % m.group(0))
    for pattern, label in ((r"\bwas\s+\$\d", "a struck-through 'was' price"),
                           (r"\b\d+%\s*off\b", "a percentage discount"),
                           (r"\blimited time\b", "an urgency claim"),
                           (r"\b(?:sqlmap|nikto|metasploit)\b", "an attack tool")):
        if re.search(pattern, body, re.IGNORECASE):
            problems.append("description contains %s" % label)
    return problems


def main():
    dry = "--dry-run" in sys.argv
    counts = _vo.counts(_vo.BUNDLE)
    body = io.open(os.path.join(ROOT, "content", "products", "migration-system.html"), encoding="utf-8").read()
    print("counted from the bundle: %d files, %d modules, %d commands, %d scripts, %d platform guides, "
          "%d checklists, %d report templates, %s words"
          % (counts["files"], counts["modules"], counts["commands"], counts["scripts"], counts["guides"],
             counts["checklists"], counts["reports"], format(counts["words"], ",")))
    problems = audit_description(body, counts)
    if problems:
        for p in problems:
            print("  FAIL %s" % p)
        raise SystemExit("refusing to publish a listing that does not match the bundle")
    print("  quantities, price and claims in the description check out")
    if "--check-only" in sys.argv:
        return 0

    existing = find()
    if dry:
        print("%s %s at $%s" % ("would update" if existing else "would create", HANDLE, PRICE))
        return 0

    payload = {
        "handle": HANDLE,
        "title": TITLE,
        "descriptionHtml": body,
        "vendor": "Site Builder Stack",
        "productType": "Digital Product",
        "status": "ACTIVE",
        "tags": ["migration", "replatforming", "redirects", "seo", "wordpress", "shopify", "astro", "claude-code", "digital"],
        "templateSuffix": "migration-system",
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
                     "sku": SKU, "requiresShipping": False, "tracked": False,
                     "measurement": {"weight": {"value": 0.0, "unit": "GRAMS"}},
                 },
             }]})
    check_user_errors(vd["productVariantsBulkUpdate"], "productVariantsBulkUpdate")
    v = vd["productVariantsBulkUpdate"]["productVariants"][0]
    if v["price"] != PRICE:
        raise SystemExit("price on the store is $%s, expected $%s — run with --set-price" % (v["price"], PRICE))

    print("%s %s" % (verb, prod["handle"]))
    print("  price            $%s" % v["price"])
    print("  sku              %s" % v["sku"])
    print("  requiresShipping %s" % v["inventoryItem"]["requiresShipping"])
    print("  weight           %s %s" % (v["inventoryItem"]["measurement"]["weight"]["value"],
                                        v["inventoryItem"]["measurement"]["weight"]["unit"]))
    print("  template suffix  migration-system")
    return 0


if __name__ == "__main__":
    sys.exit(main())
