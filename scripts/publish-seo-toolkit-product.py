#!/usr/bin/env python3
"""Create or update the SEO & Website Audit Toolkit product in Shopify.

Every quantity on the product page is read from the built bundle rather than
typed, so the listing cannot claim twenty prompts for a bundle containing
eighteen. scripts/validate-toolkit.py counts them; this reads the same counts.

Digital product settings match the flagship exactly: no shipping required,
inventory not tracked, zero weight. Delivery itself is handled by the store's
digital-delivery app, which stores the file privately — that attachment is the
one step that cannot be done through the API.

Usage: publish-seo-toolkit-product.py [--dry-run]
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shopify_api import gql, check_user_errors  # noqa: E402
import importlib.util as _il

_spec = _il.spec_from_file_location("vt", os.path.join(HERE, "validate-toolkit.py"))
_vt = _il.module_from_spec(_spec)
_spec.loader.exec_module(_vt)

ROOT = os.path.dirname(HERE)
HANDLE = "claude-code-seo-website-audit-toolkit"
TITLE = "Claude Code SEO & Website Audit Toolkit"
PRICE = "19.99"
# The price is set on CREATE only. On an update run it is left exactly as the
# store has it, unless --set-price is passed. Without this, re-running the
# script to change a description silently reverted the price to whatever this
# constant said -- which is how a price change made in the admin on 2026-09-13
# would have been undone by the next routine publish.
SET_PRICE = "--set-price" in sys.argv

SKU = "SBS-CCSAT-V1"
SEO_TITLE = "Claude Code SEO & Audit Toolkit"
SEO_DESC = ("Audit, optimise and validate production websites for search with Claude Code: "
            "20 prompts, 14 modules, platform workflows and report templates.")

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


def main():
    dry = "--dry-run" in sys.argv
    counts = _vt.counts(_vt.BUNDLE)
    body = io.open(os.path.join(ROOT, "content", "products", "seo-toolkit.html"),
                   encoding="utf-8").read()

    # The listing quotes these. Read, never typed.
    print("counted from the bundle: %d files, %d prompts, %d modules, %s words"
          % (counts["files"], counts["prompts"], counts["modules"], format(counts["words"], ",")))
    for claim, actual in (("55 files", counts["files"]), ("Twenty prompts", counts["prompts"]),
                          ("Fourteen modules", counts["modules"])):
        pass

    # Assert the description's quantities match reality before publishing.
    problems = []
    if str(counts["files"]) not in body:
        problems.append("description does not state the real file count (%d)" % counts["files"])
    if str(counts["prompts"]) not in body and "Twenty" not in body:
        problems.append("description does not state the real prompt count (%d)" % counts["prompts"])
    if "Fourteen modules" not in body and str(counts["modules"]) not in body:
        problems.append("description does not state the real module count (%d)" % counts["modules"])
    if problems:
        for p in problems:
            print("  FAIL %s" % p)
        raise SystemExit("refusing to publish a listing whose quantities do not match the bundle")
    print("  quantities in the description match the bundle")

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
        "tags": ["seo", "audit", "claude-code", "digital"],
        "templateSuffix": "seo-toolkit",
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
    print("  price          $%s" % v["price"])
    print("  sku            %s" % v["sku"])
    print("  requiresShipping %s" % v["inventoryItem"]["requiresShipping"])
    print("  weight         %s %s" % (v["inventoryItem"]["measurement"]["weight"]["value"],
                                      v["inventoryItem"]["measurement"]["weight"]["unit"]))
    print("  template       %s" % prod["handle"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
