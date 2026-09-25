#!/usr/bin/env python3
"""Staged product-description corrections — NOT applied by default.

A product description is shared store data: it is live the moment it is saved,
regardless of which theme is published. These two corrections are therefore
staged rather than shipped with the theme work.

    python3 docs/product-pages/staged-description-changes.py            # show the diff
    python3 docs/product-pages/staged-description-changes.py --apply    # write them

Superseded entries are removed rather than left to report "skipped" forever;
the sequence of what changed and when is in the git log and in
IMPLEMENTATION-2026-09-24.md, which is where that history belongs.

Both edits are exact-string replacements against a re-read of the live
description, so a merchant edit made in between is never overwritten: if the
expected text is no longer present the change is reported as skipped rather
than forced. Running it twice changes nothing the second time.

Nothing here touches price, handle, variants, status, SKU, media, metafields
or publication.
"""
from __future__ import annotations

import argparse, difflib, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
from shopify_api import gql, check_user_errors  # noqa: E402

READ = """
query($id: ID!) { product(id: $id) { id handle title descriptionHtml } }
"""
WRITE = """
mutation($input: ProductInput!) {
  productUpdate(input: $input) {
    product { id handle descriptionHtml }
    userErrors { field message }
  }
}
"""

CHANGES = [
    dict(
        product="gid://shopify/Product/10779378221348",
        handle="claude-code-website-launch-system",
        why=(
            "“No dependencies” read as “you need nothing”. The archive genuinely installs "
            "nothing, but the workflows are run inside Claude Code, which the buyer must "
            "already have. The other seven pages name their prerequisites; this one did not."
        ),
        old=(
            "Everything is plain Markdown you\nown outright. No installation, no dependencies, "
            "no subscription, nothing that\nphones home."
        ),
        new=(
            "Everything is plain Markdown you\nown outright. Nothing to install, no subscription, "
            "nothing that phones home.\nYou run the workflows yourself inside Claude Code, so you "
            "need Claude Code and a\nterminal; the files themselves need nothing but a text editor."
        ),
    ),
    dict(
        product="gid://shopify/Product/10795841519908",
        handle="complete-site-builder-stack",
        why=(
            "The replacement-file route was removed from the policy as well, so the page "
            "must not promise one either."
        ),
        old=(
            "<p>All sales are final and we do not offer refunds. If a download link does not "
            "work or a file will not open, email "
            '<a href="mailto:admin@sitebuilderstack.com">admin@sitebuilderstack.com</a> and we '
            "will supply a working copy. The full terms are in the "
            '<a href="/policies/refund-policy">refund policy</a>.</p>'
        ),
        new=(
            "<p>All sales are final and we do not offer refunds. The full terms are in the "
            '<a href="/policies/refund-policy">refund policy</a>.</p>'
        ),
    ),
]


def show(handle: str, old: str, new: str) -> None:
    diff = difflib.unified_diff(
        old.splitlines(), new.splitlines(), fromfile=f"{handle} (live)", tofile=f"{handle} (proposed)", lineterm=""
    )
    for line in diff:
        print("   " + line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the corrections to the live products")
    args = ap.parse_args()

    applied = skipped = already = 0
    for c in CHANGES:
        live = gql(READ, {"id": c["product"]})["product"]
        if live is None:
            print(f"! {c['handle']}: not found"); skipped += 1; continue
        body = live["descriptionHtml"]
        print(f"\n=== {live['title']}  ({live['handle']})")
        print(f"    Why: {c['why']}")

        if c["new"] in body:
            print("    already applied — nothing to do"); already += 1; continue
        if c["old"] not in body:
            print("    SKIPPED: the expected text is not present. The description has changed;")
            print("    re-read it and update this changeset rather than forcing the edit.")
            skipped += 1
            continue

        show(live["handle"], c["old"], c["new"])
        if not args.apply:
            continue

        updated = body.replace(c["old"], c["new"], 1)
        res = gql(WRITE, {"input": {"id": c["product"], "descriptionHtml": updated}})
        check_user_errors(res["productUpdate"], "productUpdate")
        back = gql(READ, {"id": c["product"]})["product"]["descriptionHtml"]
        if c["new"] in back and c["old"] not in back:
            print("    applied and read back OK"); applied += 1
        else:
            print("    APPLIED BUT READ-BACK FAILED — inspect this product by hand"); skipped += 1

    print(f"\napplied {applied}, already correct {already}, skipped {skipped}")
    if not args.apply:
        print("dry run — nothing was written. Re-run with --apply when authorised.")
    return 1 if skipped else 0


if __name__ == "__main__":
    raise SystemExit(main())
