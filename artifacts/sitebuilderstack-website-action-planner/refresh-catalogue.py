#!/usr/bin/env python3
"""Re-verify products.json against the live storefront.

    python3 artifacts/sitebuilderstack-website-action-planner/refresh-catalogue.py            # report only
    python3 artifacts/sitebuilderstack-website-action-planner/refresh-catalogue.py --write    # update the snapshot

What it does
------------
For each product in products.json it reads the live product by handle and
compares status, availability, price, currency and title. With --write it
updates only the *verified* fields — price, currency, status, availability,
title and the verification dates. Descriptive content (use case, benefits,
exclusions, prerequisites) is never rewritten from here: those were read from
each product's published description by a person and are not machine-derivable
without guessing.

If a product cannot be verified it is marked `availableOnDate: false`, which
makes the artifact print "See current price" for it instead of a number.
Nothing is ever invented.

After a --write run: `python3 build.py`, `node tests/test-rules.js`,
`node tests/test-links.js`, then republish index.html to the same artifact URL.
"""
from __future__ import annotations

import datetime as _dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from shopify_api import gql  # noqa: E402

QUERY = """
query($handle: String!) {
  productByHandle(handle: $handle) {
    id handle title status onlineStoreUrl
    priceRangeV2 { minVariantPrice { amount currencyCode } }
    variants(first: 1) { edges { node { sku availableForSale } } }
  }
}
"""

def main() -> int:
    write = "--write" in sys.argv
    path = HERE / "products.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    today = _dt.date.today().isoformat()

    changes: list[str] = []
    problems: list[str] = []

    for p in data["products"]:
        try:
            node = gql(QUERY, {"handle": p["handle"]}).get("productByHandle")
        except SystemExit:
            raise
        except Exception as exc:                      # noqa: BLE001
            problems.append(f'{p["handle"]}: lookup failed ({exc.__class__.__name__})')
            if write:
                p["availableOnDate"] = False
            continue

        if node is None:
            problems.append(f'{p["handle"]}: no such product on the storefront')
            if write:
                p["availableOnDate"] = False
                p["status"] = "UNKNOWN"
            continue

        price = float(node["priceRangeV2"]["minVariantPrice"]["amount"])
        currency = node["priceRangeV2"]["minVariantPrice"]["currencyCode"]
        variants = node["variants"]["edges"]
        available = bool(variants and variants[0]["node"]["availableForSale"]) and node["status"] == "ACTIVE"
        expected_url = f'https://sitebuilderstack.com/products/{node["handle"]}'

        for field, live, stored in (
            ("price", price, p["price"]),
            ("currency", currency, p["currency"]),
            ("status", node["status"], p["status"]),
            ("title", node["title"], p["title"]),
            ("availableOnDate", available, p["availableOnDate"]),
            ("url", expected_url, p["url"]),
        ):
            if live != stored:
                changes.append(f'{p["handle"]}.{field}: {stored!r} -> {live!r}')

        if write:
            p["price"] = price
            p["currency"] = currency
            p["status"] = node["status"]
            p["title"] = node["title"]
            p["availableOnDate"] = available
            p["url"] = expected_url
            p["verifiedOn"] = today

    if write:
        data["snapshot"]["verifiedOn"] = today
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Checked {len(data['products'])} products against the live storefront.")
    if changes:
        print("\nDifferences:")
        for c in changes:
            print("  " + c)
    else:
        print("No differences — the snapshot matches the storefront.")
    if problems:
        print("\nCould not verify:")
        for c in problems:
            print("  " + c)
    print()
    if write:
        print(f"products.json rewritten; snapshot.verifiedOn = {today}")
        print("Next: python3 build.py && node tests/test-rules.js && node tests/test-links.js, then republish index.html")
    else:
        print("Report only. Re-run with --write to update products.json.")
    return 1 if problems else 0

if __name__ == "__main__":
    raise SystemExit(main())
