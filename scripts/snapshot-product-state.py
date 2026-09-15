#!/usr/bin/env python3
"""Snapshot everything the Admin API exposes about the product.

The Digital Products app keeps attachment data in its own backend, so there is
no documented field to read. Snapshotting before and after the attachment and
diffing is how we find out whether ANY observable signal exists -- rather than
guessing that there is one, or that there isn't.

Usage: snapshot-product-state.py <out.json>
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import gql  # noqa: E402

Q = """{
  products(first:1){ nodes{
    id title status handle totalInventory tracksInventory
    metafields(first:100){ nodes{ namespace key type value } }
    media(first:20){ nodes{ mediaContentType status } }
    variants(first:5){ nodes{
      id title sku price
      metafields(first:100){ nodes{ namespace key type value } }
      media(first:20){ nodes{ mediaContentType } }
      inventoryItem{ id tracked requiresShipping }
    } }
    resourcePublications(first:20){ nodes{ isPublished publication{ name } } }
  } }
  appInstallations(first:50){ nodes{ app{ title handle } } }
  scriptTags(first:20){ nodes{ src displayScope } }
  files(first:100){ nodes{ ... on GenericFile { url originalFileSize } } }
}"""

out = sys.argv[1] if len(sys.argv) > 1 else "product-state.json"
d = gql(Q)
with open(out, "w", encoding="utf-8") as fh:
    json.dump(d, fh, indent=2, sort_keys=True)
p = d["products"]["nodes"][0]
print("snapshot -> %s" % out)
print("  apps          %s" % ", ".join(a["app"]["title"] for a in d["appInstallations"]["nodes"]))
print("  product mf    %d" % len(p["metafields"]["nodes"]))
print("  variant mf    %d" % len(p["variants"]["nodes"][0]["metafields"]["nodes"]))
print("  product media %d" % len(p["media"]["nodes"]))
print("  script tags   %d" % len(d["scriptTags"]["nodes"]))
print("  generic files %d" % len([f for f in d["files"]["nodes"] if f.get("url")]))
