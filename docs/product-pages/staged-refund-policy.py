#!/usr/bin/env python3
"""Staged rewrite of the refund policy — final sale, covering all eight products.

    python3 docs/product-pages/staged-refund-policy.py            # show the diff
    python3 docs/product-pages/staged-refund-policy.py --apply    # write it

What changes
------------
- It covers all eight products instead of naming only the Launch System.
- Final sale is the rule. Change of mind, having read it, not needing it any
  more, buying the wrong product, or buying the same one twice are all stated
  as NOT refundable. The old discretionary line — "if you have looked at it and
  decided it is not for you, get in touch and tell us why" — is gone.

No carve-outs
-------------
Both exceptions this policy originally carried were removed on the owner's
explicit instruction, after the trade-offs were put to them twice:

- **Failure to supply.** There is no promise to refund when the store cannot
  deliver, and — on a later instruction the same day — no promise to supply a
  replacement file either. The policy commits to no outcome when a download
  fails. It still carries the contact address, so a customer has somewhere to
  write; it simply does not say what will happen. Delivery has been proven end
  to end for ONE product — the Launch System, by order #1001 — and the other
  seven have archives attached but no completed test purchase.
- **Statutory rights.** The paragraph stating that consumer law is unaffected is
  gone. The policy is now silent on the subject. It does not assert that such
  rights do not exist, because in the UK, the EU, Australia and several US
  states they do, regardless of what this page says.

Placing a test order for each product is what would make the first of these
safe to have removed.

"""
from __future__ import annotations

import argparse, difflib, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
from shopify_api import gql, check_user_errors  # noqa: E402

READ = "{ shop { shopPolicies { id type title body } } }"
WRITE = """
mutation($policy: ShopPolicyInput!) {
  shopPolicyUpdate(shopPolicy: $policy) {
    shopPolicy { id type body }
    userErrors { field message }
  }
}
"""

POLICY = """<p><em>This document explains how this store operates. It is not legal advice and is not individualised to your circumstances.</em></p>

<h2>The short version</h2>
<p>Every product sold here is a digital download, and <strong>all sales are final</strong>. We do not offer refunds.</p>

<h2>What this covers</h2>
<p>This policy applies to all eight products sold here:</p>
<ul>
<li>The Claude Code Website Launch System</li>
<li>Claude Code SEO &amp; Website Audit Toolkit</li>
<li>Claude Code Conversion &amp; Revenue Optimization Toolkit</li>
<li>Claude Code Website Operations &amp; Maintenance System</li>
<li>Claude Code Shopify Automation &amp; Admin API Toolkit</li>
<li>Claude Code Website Migration &amp; Replatforming System</li>
<li>Claude Code Agency &amp; Client Delivery System</li>
<li>Complete Site Builder Stack (the first three, as three downloads on one order)</li>
</ul>

<h2>Why digital products are final sale</h2>
<p>Each of these is a file you download and keep. Once it has been supplied it cannot be returned and we have no way to un-supply it &mdash; you still have everything you paid for. That is why every product page sets out in detail what is inside before you buy: the file count, the module list, the word count, what it requires you to already have, what it does not do, and how delivery works. Read it, and <em>ask us before you buy</em> if anything is unclear. We would far rather answer a question than take money for the wrong product.</p>

<h2>What this means</h2>
<p>We do not refund where:</p>
<ul>
<li>You changed your mind, or no longer need it</li>
<li>You have read it, downloaded it, or used it</li>
<li>You bought the wrong product, or one you already owned</li>
<li>You bought a single product and later wanted the bundle, or the reverse &mdash; there is no upgrade credit and never has been</li>
<li>It did not produce the result you hoped for. No product here promises rankings, traffic, revenue, uptime or security, and every product page says so</li>
<li>You do not have, or do not want to use, the things it requires &mdash; Claude Code, a terminal, Python, or platform access. Each product page names its requirements before the price</li>
</ul>

<h2>Licence breach</h2>
<p>Where there is evidence the licence has been breached &mdash; the files redistributed, resold, or published &mdash; we may revoke access.</p>

<h2>How to contact us</h2>
<p>Email <a href="mailto:admin@sitebuilderstack.com">admin@sitebuilderstack.com</a> with your order number and a short description of the problem. We aim to respond within a few business days.</p>

<h2>Returns and shipping</h2>
<p>There is nothing to return and nothing is shipped. This is a digital store.</p>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    policies = {p["type"]: p for p in gql(READ)["shop"]["shopPolicies"]}
    current = policies.get("REFUND_POLICY")
    if current is None:
        print("No refund policy exists on this shop."); return 1

    def flat(html: str) -> list[str]:
        t = re.sub(r"<[^>]+>", "", html)
        t = t.replace("&mdash;", "—").replace("&amp;", "&").replace("&nbsp;", " ")
        return [ln.strip() for ln in t.splitlines() if ln.strip()]

    if flat(current["body"]) == flat(POLICY):
        print("already applied — nothing to do"); return 0

    print("=== Refund policy — proposed replacement ===\n")
    for line in difflib.unified_diff(flat(current["body"]), flat(POLICY),
                                     fromfile="live", tofile="proposed", lineterm=""):
        print("  " + line)

    if not args.apply:
        print("\ndry run — nothing was written. Re-run with --apply when authorised.")
        return 0

    # ShopPolicyInput is keyed by `type`, not by the policy's id.
    res = gql(WRITE, {"policy": {"type": "REFUND_POLICY", "body": POLICY}})
    check_user_errors(res["shopPolicyUpdate"], "shopPolicyUpdate")
    back = {p["type"]: p for p in gql(READ)["shop"]["shopPolicies"]}["REFUND_POLICY"]["body"]
    low = back.lower()
    ok = ("all sales are final" in low and "all eight products" in low
          and "we do not offer refunds" in low
          and "statutory rights" not in low
          and "refund you in full" not in low
          and "working copy" not in low
          and "working file" not in low)
    print("\napplied and read back OK" if ok else "\nAPPLIED BUT READ-BACK LOOKS WRONG — inspect by hand")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
