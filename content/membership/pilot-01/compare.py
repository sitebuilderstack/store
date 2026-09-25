#!/usr/bin/env python3
"""compare.py — did the change do what was asked, and only what was asked?

Reads two capture.py files and prints one row per property: before, after, and
a verdict. A property you named with --expect is meant to change and fails if
it did not; every other property is meant to hold and fails if it moved. That
inversion is the point — the usual regression is not "the change did not
happen", it is "something else did".

    python3 compare.py changes/CR-07/before.json changes/CR-07/after.json \\
        --expect h1 --expect content_sha256
    python3 compare.py --self-test

Exit 0 when every check passes, 1 when any fails, 2 on a usage error.
Python 3.8+, standard library only. Part of Workflow Club release 01.
"""
import argparse
import io
import json
import sys

# Properties compared by default. content_sha256 and content_words move on
# almost any edit, so they are informational unless named with --expect.
FIELDS = ["status", "final_url", "title", "h1", "h2", "canonical", "robots_meta",
          "x_robots_tag", "forms", "form_count", "cta", "content_sha256", "content_words"]
SOFT = {"content_sha256", "content_words", "h2"}


def fmt(v):
    if v is None:
        return "(absent)"
    if isinstance(v, list):
        return "[]" if not v else " | ".join(str(x) for x in v)
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def compare(before, after, expect, require=None):
    """`expect` names properties the change should alter; `require` maps a
    property to text its new value must contain. The second exists because
    "h1 changed" is satisfied by the h1 disappearing — the failure this whole
    workflow is built to catch. Requiring the new wording closes that."""
    require = require or {}
    rows, failures = [], 0
    for f in FIELDS:
        if f not in before and f not in after:
            continue
        b, a = before.get(f, "__missing__"), after.get(f, "__missing__")
        missing = b == "__missing__" or a == "__missing__"
        changed = b != a
        want = f in expect
        need = require.get(f)
        if missing:
            verdict, ok = "MISSING FIELD", False
        elif need is not None and need.lower() not in fmt(a).lower():
            verdict, ok = "FAIL — new value does not contain %r" % need, False
        elif want and not changed:
            verdict, ok = "FAIL — expected to change, did not", False
        elif want and changed:
            verdict, ok = "OK — changed as expected", True
        elif changed and f in SOFT:
            verdict, ok = "changed (informational)", True
        elif changed:
            verdict, ok = "FAIL — changed and was not expected to", False
        else:
            verdict, ok = "unchanged", True
        if not ok:
            failures += 1
        rows.append((f, fmt(b if b != "__missing__" else None), fmt(a if a != "__missing__" else None), verdict, ok))
    return rows, failures


def render(rows, before, after):
    w = max(len(r[0]) for r in rows) + 2
    out = ["Change verification — %s -> %s" % (before.get("label", "before"), after.get("label", "after")),
           "URL: %s" % before.get("url", "?"), ""]
    for f, b, a, v, ok in rows:
        out.append("%-*s %s" % (w, f, v))
        if b != a:
            out.append("%-*s   before: %s" % (w, "", b[:160]))
            out.append("%-*s   after:  %s" % (w, "", a[:160]))
    bad = [r for r in rows if not r[4]]
    out += ["", "%d checked, %d failed" % (len(rows), len(bad))]
    if bad:
        out.append("Failed: " + ", ".join(r[0] for r in bad))
    return "\n".join(out)


def self_test():
    fails = 0

    def check(name, ok, detail=""):
        nonlocal fails
        if not ok:
            fails += 1
        print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -> " + str(detail)[:160]) if detail and not ok else ""))

    base = {"label": "before", "url": "https://example.com/", "status": 200, "final_url": "https://example.com/",
            "title": "Harbourline Physio", "h1": ["Welcome"], "h2": ["Our services"], "canonical": "https://example.com/",
            "robots_meta": "index,follow", "x_robots_tag": None, "forms": ["/api/contact"], "form_count": 1,
            "cta": {"text": "Book an assessment", "href": "/book"}, "content_sha256": "aaa", "content_words": 20}

    good = dict(base, label="after", h1=["Physiotherapy in Harbourline"], content_sha256="bbb", content_words=22)
    rows, f = compare(base, good, {"h1"})
    check("the intended change passes", f == 0, render(rows, base, good))

    bad = dict(base, label="after", h1=[], content_sha256="bbb", content_words=22)
    rows, f = compare(base, bad, {"h1"})
    check("h1 vanishing passes the bare expected-to-change test (the documented gap)",
          f == 0, render(rows, base, bad))
    rows, f = compare(base, bad, {"h1"}, {"h1": "Physiotherapy in Harbourline"})
    check("--require catches the h1 that vanished", f == 1 and any(r[0] == "h1" and not r[4] for r in rows))
    rows, f = compare(base, good, {"h1"}, {"h1": "Physiotherapy in Harbourline"})
    check("--require passes when the new wording is there", f == 0)
    rows, f = compare(base, bad, set())
    check("an unexpected h1 change fails when h1 was not listed", f >= 1 and any(r[0] == "h1" and not r[4] for r in rows))

    broke = dict(base, label="after", h1=["Physiotherapy in Harbourline"], canonical="https://staging.example.com/",
                 content_sha256="bbb", content_words=22)
    rows, f = compare(base, broke, {"h1"})
    check("a canonical that moved is caught as collateral damage", f == 1 and any(r[0] == "canonical" and not r[4] for r in rows))

    rows, f = compare(base, dict(base, label="after"), {"h1"})
    check("a change that did not happen fails", f == 1 and any(r[0] == "h1" and "did not" in r[3] for r in rows))

    missing = {k: v for k, v in base.items() if k != "canonical"}
    rows, f = compare(base, dict(missing, label="after"), set())
    check("a field missing from one capture is reported, not ignored", f == 1 and any(r[3] == "MISSING FIELD" for r in rows))

    rows, f = compare(base, dict(base, label="after", content_words=25, content_sha256="ccc"), set())
    check("content hash and word count alone do not fail the run", f == 0)

    print("\n%d failure(s)" % fails)
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("before", nargs="?")
    ap.add_argument("after", nargs="?")
    ap.add_argument("--expect", action="append", default=[], metavar="FIELD",
                    help="a property the change was supposed to alter; repeatable")
    ap.add_argument("--require", action="append", default=[], metavar="FIELD=TEXT",
                    help="the property's new value must contain TEXT; repeatable")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.before or not a.after:
        print("usage: compare.py before.json after.json [--expect FIELD ...]", file=sys.stderr)
        return 2
    try:
        before = json.load(io.open(a.before, encoding="utf-8"))
        after = json.load(io.open(a.after, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("cannot read captures: %s" % e, file=sys.stderr)
        return 2
    req = {}
    for pair in a.require:
        if "=" not in pair:
            print("--require takes FIELD=TEXT", file=sys.stderr)
            return 2
        k, v = pair.split("=", 1)
        req[k.strip()] = v
    rows, failures = compare(before, after, set(a.expect), req)
    print(render(rows, before, after))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
