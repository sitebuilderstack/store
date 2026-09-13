#!/usr/bin/env python3
"""Replace the legacy customer-facing support address in the Shopify policies.

The policies are stored in Shopify, not in this repository, so they are edited
through the Admin API. Only the customer-facing support address is touched;
nothing else in the policy bodies is rewritten.

Usage: fix-policy-contact.py [--apply]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import gql, check_user_errors  # noqa: E402

OLD = "admin@lofiskunk.com"
NEW = "admin@sitebuilderstack.com"

READ = "{ shop { shopPolicies { id type title body } } }"
WRITE = """mutation($p: ShopPolicyInput!) {
  shopPolicyUpdate(shopPolicy: $p) {
    shopPolicy { id type }
    userErrors { field message }
  }
}"""


def main():
    apply = "--apply" in sys.argv
    pols = gql(READ)["shop"]["shopPolicies"]
    touched = 0

    for p in pols:
        body = p["body"] or ""
        n = body.count(OLD)
        if not n:
            print("%-22s clean" % p["type"])
            continue
        touched += 1
        print("%-22s %d occurrence(s) of the legacy address" % (p["type"], n))
        new_body = body.replace(OLD, NEW)
        assert OLD not in new_body and new_body.count(NEW) >= n
        if not apply:
            print("    dry run; re-run with --apply")
            continue
        d = gql(WRITE, {"p": {"type": p["type"], "body": new_body}})
        check_user_errors(d["shopPolicyUpdate"], "shopPolicyUpdate")
        print("    updated")

    if not apply:
        print("\n%d policy(ies) would change." % touched)
        return

    # Re-read from the API rather than trusting the mutation response.
    print("\nVerifying against a fresh read:")
    bad = 0
    for p in gql(READ)["shop"]["shopPolicies"]:
        body = p["body"] or ""
        if OLD in body:
            bad += 1
            print("  FAIL %s still contains the legacy address" % p["type"])
        else:
            print("  ok   %-22s new address present: %s" % (p["type"], NEW in body))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
