#!/usr/bin/env python3
"""Turn audit-rendered-a11y.js output into a pass/fail exit code.

Kept as a file rather than inlined into the shell so the quoting stays
readable and the noise list is reviewable.
"""
import json
import sys

# Console errors emitted by Shopify's own storefront resources, not by this
# theme. Matched by narrow substring so a real error from site code still fails
# — every entry here is an error that stops being caught, so each one needs
# evidence before it is added.
#
#   shop.app frame-ancestors  — appears on pages this project has never touched.
#   monorail event            — Shopify's analytics beacon failing to send.
#   X-Frame-Options ALLOW-FROM — a deprecated directive on a resource Shopify
#     embeds behind its payment button. Verified: the theme sets no such header
#     (nothing in theme/dev matches), the document itself returns
#     `x-frame-options: DENY`, and the error is intermittent across loads of the
#     same URL rather than deterministic.
NOISE = (
    "Framing 'https://shop.app/' violates",
    "Error producing monorail event",
    "Invalid 'X-Frame-Options' header",
)


def main():
    d = json.load(sys.stdin)
    bad = []
    for key in ("contrast", "headings", "names", "images", "taps", "focus"):
        if d.get(key):
            bad.append("%s:%d" % (key, len(d[key])))
    errs = [e for e in (d.get("consoleErrors") or [])
            if not any(n in e for n in NOISE)]
    if errs:
        bad.append("console:%d" % len(errs))
    ov = d.get("overflow") or {}
    if ov.get("scrollW", 0) > ov.get("clientW", 0) + 1:
        bad.append("overflow %d>%d" % (ov["scrollW"], ov["clientW"]))
    print(", ".join(bad) if bad else "clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
