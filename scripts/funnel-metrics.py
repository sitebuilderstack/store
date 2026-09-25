#!/usr/bin/env python3
"""Funnel metrics from data the store already collects.

Deliberately uses Shopify's own analytics and the Admin API rather than adding
a tracking script. A one-product store does not need fingerprinting to know how
many people reached the product page.

  Visitor -> Guide -> Free resource -> Signup -> Product page -> Cart -> Purchase

Usage: funnel-metrics.py [--days 28]
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shopify_api import gql  # noqa: E402
import shopifyql  # noqa: E402

KIT_TAG = "claude-md-kit"


def sessions_by_landing_page(days):
    q = ("FROM sessions SHOW sessions "
         "GROUP BY landing_page_path SINCE -%dd UNTIL today "
         "ORDER BY sessions DESC LIMIT 25" % days)
    try:
        return shopifyql.run(q)
    except Exception as e:                            # noqa: BLE001
        return {"error": str(e)}


def signups():
    """Customers who came in through the Starter Kit form.

    Counted two ways because the tag is unverified: nobody has completed the
    form yet, so whether Shopify applies contact[tags] on this endpoint has
    never been observed. If the tagged count stays zero while the subscribed
    count grows, the tag is not being applied and the automation trigger has to
    key off consent and date instead.
    """
    d = gql("""{ customers(first: 250) { nodes {
                 id createdAt email tags
                 emailMarketingConsent { marketingState consentUpdatedAt } } } }""")
    nodes = d["customers"]["nodes"]
    tagged = [c for c in nodes if KIT_TAG in (c["tags"] or [])]
    subscribed = [c for c in nodes
                  if (c.get("emailMarketingConsent") or {}).get("marketingState")
                  == "SUBSCRIBED"]
    return nodes, tagged, subscribed


def orders(days):
    d = gql("""query($q:String!){ orders(first:100, query:$q) {
                 nodes { id name createdAt displayFinancialStatus
                         totalPriceSet { shopMoney { amount currencyCode } } } } }""",
            {"q": "created_at:>-%dd" % days})
    return d["orders"]["nodes"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    a = ap.parse_args()

    print("=== Sessions by landing page (last %d days) ===" % a.days)
    s = sessions_by_landing_page(a.days)
    if isinstance(s, dict) and "error" in s:
        print("  ShopifyQL unavailable:", s["error"][:120])
    else:
        # shopifyql.run returns ((headers, rows), errors)
        payload = s[0] if isinstance(s, tuple) else s
        rows = payload[1] if isinstance(payload, (list, tuple)) and len(payload) > 1 else []
        for r in rows[:25]:
            if isinstance(r, dict):
                print("  %-58s %s" % (r.get("landing_page_path", "?")[:58],
                                      r.get("sessions", "?")))
        print("\n  Sessions on a store this new are mostly automation and crawlers.")
        print("  Cross-check against Search Console before reading them as people.")

    print("\n=== Email capture ===")
    nodes, tagged, subscribed = signups()
    print("  customer records total          %d" % len(nodes))
    print("  tagged '%s'            %d" % (KIT_TAG, len(tagged)))
    print("  marketing state SUBSCRIBED      %d" % len(subscribed))
    if not tagged and not subscribed:
        print("\n  !! The funnel has no entries. The opt-in form has never produced a")
        print("     subscriber, so nothing downstream of it can be measured yet.")
        print("     Submit it once by hand before building an automation on it.")
    elif subscribed and not tagged:
        print("\n  !! Subscribers exist but none carry the tag. contact[tags] is probably")
        print("     not being applied — trigger the automation on consent + date instead.")

    print("\n=== Orders (last %d days) ===" % a.days)
    os_ = orders(a.days)
    print("  orders %d" % len(os_))
    for o in os_:
        m = o["totalPriceSet"]["shopMoney"]
        print("   %-8s %s %s %s  %s" % (o["name"], m["amount"], m["currencyCode"],
                                        o["displayFinancialStatus"], o["createdAt"][:10]))

    print("\n=== Conversion ===")
    print("  Shopify's own analytics reports sessions and conversion rate without any")
    print("  added script. Add-to-cart and reached-checkout are in Analytics > Reports.")
    print("  Nothing here needs a third-party pixel.")


if __name__ == "__main__":
    main()
