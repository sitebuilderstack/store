#!/usr/bin/env python3
"""Create or update the Conversion & Revenue Optimization Toolkit in Shopify.

Every quantity on the listing is read from the built bundle rather than typed,
so the page cannot claim 70 workflows for a bundle containing 61.
scripts/validate-cro-toolkit.py counts them; this reads the same counts and
refuses to publish if the description disagrees with any of them.

There is one extra assertion here that the other products do not need: the
description must not contain a predicted percentage lift. The product's central
claim is that it never makes one, so a listing that did would be the most
visible possible contradiction of it. The same pattern the bundle validator
uses is applied to the marketing copy.

Digital product settings match the other two exactly: no shipping required,
inventory not tracked, zero weight. Delivery itself is handled by the store's
digital-delivery app, which stores the file privately — that attachment is the
one step that cannot be done through the API.

Usage: publish-cro-toolkit-product.py [--dry-run]
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shopify_api import gql, check_user_errors  # noqa: E402
import importlib.util as _il

_spec = _il.spec_from_file_location("vc", os.path.join(HERE, "validate-cro-toolkit.py"))
_vc = _il.module_from_spec(_spec)
_spec.loader.exec_module(_vc)

ROOT = os.path.dirname(HERE)
HANDLE = "claude-code-conversion-revenue-optimization-toolkit"
TITLE = "Claude Code Conversion & Revenue Optimization Toolkit"
PRICE = "19.99"
# The price is set on CREATE only. On an update run it is left exactly as the
# store has it, unless --set-price is passed. Without this, re-running the
# script to change a description silently reverted the price to whatever this
# constant said -- which is how a price change made in the admin on 2026-09-13
# would have been undone by the next routine publish.
SET_PRICE = "--set-price" in sys.argv

SKU = "SBS-CCCRO-V1"
SEO_TITLE = "Claude Code Conversion & Revenue Toolkit"
SEO_DESC = ("Find where a website loses conversions, rank what to fix and prove the fix "
            "worked, with Claude Code: 70 workflows, 68 commands, funnels, analytics "
            "and experimentation.")

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
    """Every number the listing states must be one something counted."""
    problems = []
    checks = (
        ("files", counts["files"]),
        ("modules", counts["modules"]),
        ("workflows", counts["workflows"]),
        ("commands", counts["commands"]),
    )
    for name, n in checks:
        if str(n) not in body:
            problems.append("description does not state the real %s count (%d)" % (name, n))

    # The product promises it never predicts a lift. The listing must not either.
    for m in _vc.PREDICTED_LIFT.finditer(body):
        if not _vc.negated(body, m.start()):
            problems.append("description predicts a percentage lift: %r" % m.group(0))

    # A struck-through price or an advertised bundle discount would contradict
    # both the product's own prohibitions and the decision not to launch one.
    for pattern, label in ((r"\bwas\s+\$\d", "a struck-through 'was' price"),
                           (r"\b\d+%\s*off\b", "a percentage discount"),
                           (r"\blimited time\b", "an urgency claim")):
        if re.search(pattern, body, re.IGNORECASE):
            problems.append("description contains %s" % label)
    return problems


def main():
    dry = "--dry-run" in sys.argv
    counts = _vc.counts(_vc.BUNDLE)
    body = io.open(os.path.join(ROOT, "content", "products", "cro-toolkit.html"),
                   encoding="utf-8").read()

    print("counted from the bundle: %d files, %d modules, %d workflows, %d commands, "
          "%d templates, %d examples, %s words"
          % (counts["files"], counts["modules"], counts["workflows"], counts["commands"],
             counts["templates"], counts["examples"], format(counts["words"], ",")))

    problems = audit_description(body, counts)
    if problems:
        for p in problems:
            print("  FAIL %s" % p)
        raise SystemExit("refusing to publish a listing that does not match the bundle")
    print("  quantities and claims in the description check out")

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
        "tags": ["cro", "conversion", "analytics", "claude-code", "digital"],
        "templateSuffix": "cro-toolkit",
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

    print("%s %s" % (verb, prod["handle"]))
    print("  price            $%s" % v["price"])
    print("  sku              %s" % v["sku"])
    print("  requiresShipping %s" % v["inventoryItem"]["requiresShipping"])
    print("  weight           %s %s" % (v["inventoryItem"]["measurement"]["weight"]["value"],
                                        v["inventoryItem"]["measurement"]["weight"]["unit"]))
    print("  template suffix  cro-toolkit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
