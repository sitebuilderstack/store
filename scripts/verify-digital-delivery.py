#!/usr/bin/env python3
"""Prove the store can actually deliver what it sells.

A digital storefront has a failure mode ordinary sites do not: everything can
look right, checkout can succeed, payment can capture, and the customer still
receives nothing. There is no error anywhere. This script is the gate that
catches that before a customer does.

Exit code 0 means delivery is wired. Anything else means it is not.

Usage: verify-digital-delivery.py
"""
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import gql  # noqa: E402

ORIGIN = "https://sitebuilderstack.com"

# Apps that provide digital delivery. Matched case-insensitively against the
# app title; the regex catches third-party equivalents too, so swapping app
# does not silently turn this check into a no-op.
KNOWN_DELIVERY_APPS = re.compile(
    r"digital\s*(products?|downloads?|assets?)|downloadable|sendowl|sky\s*pilot|"
    r"fetchapp|filemonk|easy\s*digital|deliverable|single\b", re.I)

fails, warns, notes = [], [], []


def check(label, ok, detail, hard=True):
    print("  %-46s %s" % (label, "PASS" if ok else ("FAIL" if hard else "WARN")))
    if detail:
        print("      %s" % detail)
    if not ok:
        (fails if hard else warns).append("%s -- %s" % (label, detail))
    return ok


print("=" * 74)
print("DIGITAL DELIVERY READINESS")
print("=" * 74)

# ── 1. a delivery mechanism exists ───────────────────────────────────────────
print("\n[1] Delivery mechanism")
d = gql("{ appInstallations(first:50){ nodes{ app{ title handle developerName } } } }")
apps = [n["app"] for n in d["appInstallations"]["nodes"]]
titles = [a["title"] for a in apps]
delivery = [a for a in apps if KNOWN_DELIVERY_APPS.search(a["title"] or "")]
check("A digital delivery app is installed",
      bool(delivery),
      ("found: %s" % ", ".join(a["title"] for a in delivery)) if delivery
      else "installed apps are: %s -- none of these deliver files" % ", ".join(titles))

# The app keeps its attachments in its own backend. Verified empirically:
# attaching a file changes NOTHING in the Admin API -- no metafield, no media,
# no fulfilment service, no script tag -- and the app's endpoints return 401 to
# an Admin API token. So "app installed" must never be reported as "delivery
# works": the catastrophic case, app installed with no file attached, looks
# identical from here.
notes.append("Whether a file is actually attached CANNOT be checked from the "
             "Admin API -- the app stores it privately. Only a paid order proves it.")

# ── 2. every purchasable product is shaped like a digital good ──────────────
# The store sells more than one product now. Checking only the first one would
# have passed while a second product was purchasable and undeliverable, which
# is the exact failure this script exists to prevent.
print("\n[2] Product configuration")
d = gql("""{ products(first:20){ nodes{ title status handle onlineStoreUrl
  variants(first:1){ nodes{ id price
    inventoryItem{ tracked requiresShipping measurement{ weight{ value } } } } } } } }""")
PRODUCTS = [n for n in d["products"]["nodes"] if n["status"] == "ACTIVE"]
check("At least one active product", bool(PRODUCTS), "%d active" % len(PRODUCTS))

for p in PRODUCTS:
    v = p["variants"]["nodes"][0]
    ii = v["inventoryItem"]
    tag = p["handle"][:34]
    check("%s: purchasable on the storefront" % tag, bool(p["onlineStoreUrl"]),
          p["onlineStoreUrl"] or "not published to the Online Store")
    check("%s: does not require shipping" % tag, ii["requiresShipping"] is False,
          "requiresShipping=%s" % ii["requiresShipping"])
    check("%s: inventory not tracked" % tag, ii["tracked"] is False,
          "tracked=%s -- a tracked digital item can sell out" % ii["tracked"])
    check("%s: weight is zero" % tag, ii["measurement"]["weight"]["value"] == 0,
          "weight=%s" % ii["measurement"]["weight"]["value"])

# The cart checks below run against the first active product. Every product is
# shape-checked above; the checkout path is exercised once because it is the
# same path for all of them.
p = PRODUCTS[0]
v = p["variants"]["nodes"][0]
ii = v["inventoryItem"]

# ── 3. the real customer path ────────────────────────────────────────────────
print("\n[3] Customer checkout path")
vid = v["id"].split("/")[-1]
try:
    import http.cookiejar
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    body = json.dumps({"items": [{"id": int(vid), "quantity": 1}]}).encode()
    req = urllib.request.Request(ORIGIN + "/cart/add.js", data=body,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "sbs-delivery-check/1.0"})
    op.open(req, timeout=30).read()
    cart = json.loads(op.open(ORIGIN + "/cart.js", timeout=30).read().decode())
    check("Cart does not require shipping", cart.get("requires_shipping") is False,
          "requires_shipping=%s" % cart.get("requires_shipping"))
    # round(), not int(): 19.99 * 100 is 1998.9999… in binary floating point,
    # and int() truncated it to 1998 against a cart that correctly said 1999.
    expected_cents = round(float(v["price"]) * 100)
    check("Cart price is correct", str(cart.get("total_price")) == str(expected_cents),
          "cart=%s expected=%s" % (cart.get("total_price"), expected_cents))
except Exception as e:
    check("Cart could be built", False, "error: %s" % e)

# ── 4. the paid file must not be publicly reachable ──────────────────────────
print("\n[4] The archive is not given away")
d = gql("""{ files(first:100){ nodes{ ... on GenericFile { url } } } }""")
urls = [n.get("url") or "" for n in d["files"]["nodes"]]
leaked = [u for u in urls if u.endswith(".zip") or "launch-system" in u]
check("Product archive is not on the public CDN", not leaked,
      "exposed: %s" % leaked if leaked else "no product archive in Shopify Files")

# ── 4b. delivery attachment, per product ────────────────────────────────────
# The Admin API cannot see whether a file is attached in the delivery app. What
# it CAN see is whether a paid order for that product ever reached FULFILLED.
# For a product with no such order, delivery is UNPROVEN — and a purchasable
# product with unproven delivery takes money and may deliver nothing.
print("\n[4b] Delivery proven per product")
od = gql("""{ orders(first:50, query:"financial_status:paid"){ nodes{
  name displayFulfillmentStatus
  lineItems(first:10){ nodes{ product{ handle } } } } } }""")
delivered = set()
for o in od["orders"]["nodes"]:
    if o["displayFulfillmentStatus"] != "FULFILLED":
        continue
    for li in o["lineItems"]["nodes"]:
        if li.get("product"):
            delivered.add(li["product"]["handle"])
for p2 in PRODUCTS:
    proven = p2["handle"] in delivered
    check("%s: delivery proven by a fulfilled paid order" % p2["handle"][:34], proven,
          "a paid order reached FULFILLED" if proven else
          "NO fulfilled paid order -- attach the file in the Digital Products app "
          "and place a real test order before promoting this product")

# ── 5. evidence from real orders ─────────────────────────────────────────────
print("\n[5] Evidence from real orders")
d = gql("""{ orders(first:10, reverse:true){ nodes{ name createdAt email
  displayFulfillmentStatus displayFinancialStatus
  fulfillments(first:5){ status }
  lineItems(first:5){ nodes{ title requiresShipping } } } } }""")
orders = d["orders"]["nodes"]
if not orders:
    notes.append("No orders yet, so delivery has never actually run. "
                 "A real test order is the only thing that proves it end to end.")
    print("  %-46s %s" % ("Orders placed so far", "none"))
else:
    for o in orders[:3]:
        ff = o["displayFulfillmentStatus"]
        print("  %-16s %s  payment=%s fulfilment=%s email=%s"
              % (o["name"], o["createdAt"][:10], o["displayFinancialStatus"], ff,
                 o.get("email") or "NONE"))
        if ff not in ("FULFILLED",):
            warns.append("%s is %s -- a digital order should fulfil immediately"
                         % (o["name"], ff))
        # The download link is delivered by email. An order with no email
        # address is undeliverable no matter how correctly it fulfils -- this
        # is exactly how order #1001 failed while showing FULFILLED.
        if not o.get("email"):
            fails.append("%s has NO email address -- the download link is sent by "
                         "email, so this order cannot be delivered even though it "
                         "shows %s" % (o["name"], ff))

print("\n" + "=" * 74)
for w in warns:
    print("WARN: %s" % w)
for f in fails:
    print("FAIL: %s" % f)
for n in notes:
    print("NOTE: %s" % n)

if fails:
    print("\n%d blocking problem(s). The store cannot deliver what it sells." % len(fails))
else:
    delivered = any(o["displayFulfillmentStatus"] == "FULFILLED" for o in orders)
    if delivered:
        print("\nEverything checkable passes AND a real order reached FULFILLED. "
              "Delivery has actually run.")
    else:
        print("\nEverything checkable passes, but nothing here proves a file is "
              "attached.\nNo order has been delivered yet -- until one has, "
              "delivery is UNCONFIRMED, not working.")
sys.exit(1 if fails else 0)
