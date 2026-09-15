#!/usr/bin/env python3
"""Check the custom pixel forwards exactly the events the site documents.

Two lists that must agree and live in different files always drift. The pixel
is the only thing that will ever collect these events, so an event documented
but not subscribed is silently uncollected, and an event subscribed but not
documented is data arriving that nobody can interpret.

Also asserts the pixel cannot leak anything it should not: the payload builder
must send only the event name, the label, the path and a coarse timestamp.

Usage:
  validate-pixel.py               check
  validate-pixel.py --self-test   prove the checks fire
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIXEL = os.path.join(ROOT, "analytics", "custom-pixel.js")
WORKER = os.path.join(ROOT, "analytics", "collector-worker.js")
DOC = os.path.join(ROOT, "docs", "analytics", "EVENTS.md")

# Fields the payload is allowed to contain. Anything else is a leak.
ALLOWED_KEYS = {"e", "l", "p", "t"}
# Things that must never appear in the pixel at all.
FORBIDDEN = (
    (r"\bdocument\.cookie\b", "reads cookies"),
    (r"\blocalStorage\b", "reads local storage"),
    (r"\bnavigator\.userAgent\b", "reads the user agent"),
    (r"\bdocument\.referrer\b", "reads the referrer"),
    (r"\bemail\b", "mentions email"),
    (r"customData\s*\)\s*[,;]?\s*$", "forwards the whole customData object"),
)


def pixel_events(src):
    m = re.search(r"const EVENTS = \[(.*?)\];", src, re.S)
    if not m:
        return set()
    return set(re.findall(r"'([a-z_]+)'", m.group(1)))


def doc_events(src):
    return set(re.findall(r"^\| `([a-z_]+)` \|", src, re.M))


def payload_keys(src):
    m = re.search(r"const body = JSON\.stringify\(\{(.*?)\n  \}\);", src, re.S)
    if not m:
        return None
    return set(re.findall(r"^\s*([a-z]+):", m.group(1), re.M))


def worker_events(src):
    m = re.search(r"const KNOWN = new Set\(\[(.*?)\]\);", src, re.S)
    return set(re.findall(r"'([a-z_]+)'", m.group(1))) if m else set()


def check(pixel_src, doc_src, worker_src=None):
    """Findings. Empty list means all three lists agree."""
    bad = []
    pe, de = pixel_events(pixel_src), doc_events(doc_src)
    if not pe:
        bad.append("could not parse the EVENTS list out of the pixel")
    if not de:
        bad.append("could not parse any events out of the documentation")
    for e in sorted(de - pe):
        bad.append("documented but not subscribed, so it is uncollected: %s" % e)
    for e in sorted(pe - de):
        bad.append("subscribed but not documented, so nobody can read it: %s" % e)

    keys = payload_keys(pixel_src)
    if keys is None:
        bad.append("could not find the payload builder")
    else:
        extra = keys - ALLOWED_KEYS
        if extra:
            bad.append("payload carries unexpected field(s): %s" % ", ".join(sorted(extra)))

    for pattern, why in FORBIDDEN:
        if re.search(pattern, pixel_src, re.M):
            bad.append("pixel %s" % why)

    # The collector drops anything not in its own allowlist, so an event the
    # pixel forwards and the worker does not know is silently discarded on
    # arrival -- the most expensive kind of drift, because both files look
    # correct in isolation.
    if worker_src is not None:
        we = worker_events(worker_src)
        if not we:
            bad.append("could not parse the KNOWN list out of the collector")
        for e in sorted(pe - we):
            bad.append("forwarded by the pixel but dropped by the collector: %s" % e)
        for e in sorted(we - pe):
            bad.append("accepted by the collector but never sent: %s" % e)
    return bad


def self_test():
    ok, bad = [], []

    def t(name, got, want):
        (ok if got == want else bad).append("%s: got %r want %r" % (name, got, want))

    good_pixel = ("const EVENTS = [\n  'a_b', 'c_d',\n];\n"
                  "  const body = JSON.stringify({\n    e: 1,\n    l: 2,\n    p: 3,\n    t: 4,\n  });\n")
    good_doc = "| `a_b` | x | y |\n| `c_d` | x | y |\n"
    good_worker = "const KNOWN = new Set([\n  'a_b','c_d',\n]);\n"
    t("matching lists are silent", check(good_pixel, good_doc, good_worker), [])
    t("an event the collector would drop fires",
      any("dropped by the collector" in x for x in
          check(good_pixel, good_doc, "const KNOWN = new Set([\n  'a_b',\n]);\n")), True)
    t("an event the collector accepts but nothing sends fires",
      any("never sent" in x for x in
          check(good_pixel, good_doc, "const KNOWN = new Set([\n  'a_b','c_d','q_q',\n]);\n")), True)
    t("a documented event that is not subscribed fires",
      any("uncollected" in x for x in check(good_pixel, good_doc + "| `e_f` | x | y |\n")), True)
    t("a subscribed event that is not documented fires",
      any("nobody can read it" in x for x in
          check(good_pixel.replace("'c_d',", "'c_d', 'z_z',"), good_doc)), True)
    t("an extra payload field fires",
      any("unexpected field" in x for x in
          check(good_pixel.replace("    t: 4,", "    t: 4,\n    ip: 5,"), good_doc)), True)
    for pattern, why in (("document.cookie", "cookies"), ("localStorage", "local storage"),
                         ("navigator.userAgent", "user agent"), ("document.referrer", "referrer")):
        t("reading the %s fires" % why,
          any(why in x for x in check(good_pixel + "\n" + pattern + ";\n", good_doc)), True)
    for line in ok:
        print("  ok   %s" % line)
    for line in bad:
        print("  FAIL %s" % line)
    print("\n%d passed, %d failed" % (len(ok), len(bad)))
    return 1 if bad else 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    if not os.path.exists(PIXEL):
        print("no pixel at %s" % os.path.relpath(PIXEL, ROOT))
        return 1
    src = open(PIXEL, encoding="utf-8").read()
    doc = open(DOC, encoding="utf-8").read()
    wsrc = open(WORKER, encoding="utf-8").read() if os.path.exists(WORKER) else None
    bad = check(src, doc, wsrc)
    n = len(pixel_events(src))
    for b in bad:
        print("  FAIL %s" % b)
    print("%d event(s) subscribed, %d finding(s)" % (n, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
