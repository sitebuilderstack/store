#!/usr/bin/env python3
"""capture.py — record the observable state of a page before or after a change.

Fetches one URL and writes what the server actually returned: status and final
URL after redirects, title, every h1, canonical, robots directive, forms and
their actions, an optional named element's text and href, and a hash of the
main content. Read-only: GET only, no credentials, no cookies kept, nothing
written but the JSON file.

    python3 capture.py https://example.com/ --label before --out changes/CR-07
    python3 capture.py https://example.com/ --label after  --out changes/CR-07 \
        --cta "a.btn-primary"
    python3 capture.py --self-test

Python 3.8+, standard library only. Part of Workflow Club release 01.
"""
import argparse
import hashlib
import html
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

UA = "sitebuilderstack-capture/1.0 (read-only change verification)"


def fetch(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.geturl(), dict(r.headers), r.read(2_000_000).decode("utf-8", "replace")


def text_of(fragment):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", fragment))).strip()


def extract(body, cta_selector=None):
    """Pull the fields a change is usually judged on. Deliberately regex-based:
    no dependency, and every field is reported as found-or-null rather than
    silently defaulted."""
    out = {}
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    out["title"] = text_of(m.group(1)) if m else None
    out["h1"] = [text_of(x) for x in re.findall(r"<h1[^>]*>(.*?)</h1>", body, re.I | re.S)]
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', body, re.I)
    out["canonical"] = m.group(1) if m else None
    m = re.search(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\']([^"\']+)', body, re.I)
    out["robots_meta"] = m.group(1) if m else None
    out["h2"] = [text_of(x) for x in re.findall(r"<h2[^>]*>(.*?)</h2>", body, re.I | re.S)]
    forms = re.findall(r"<form[^>]*>", body, re.I)
    out["forms"] = [(re.search(r'action=["\']([^"\']*)', f) or [None, None])[1] for f in forms]
    out["form_count"] = len(forms)
    # The named element: a class or id, not a full CSS engine. Enough for a CTA.
    out["cta"] = None
    if cta_selector:
        out["cta"] = find_named(body, cta_selector)
    main = re.search(r"<main[^>]*>(.*?)</main>", body, re.I | re.S)
    content = main.group(1) if main else body
    out["content_sha256"] = hashlib.sha256(text_of(content).encode("utf-8")).hexdigest()[:16]
    out["content_words"] = len(text_of(content).split())
    return out


def find_named(body, selector):
    """Support `tag.class`, `.class` and `#id` — the three that cover a CTA."""
    m = re.fullmatch(r"(?:([a-zA-Z]+))?(?:\.([\w-]+)|#([\w-]+))", selector.strip())
    if not m:
        return {"error": "selector not supported: use tag.class, .class or #id"}
    tag, cls, idn = m.group(1) or r"[a-zA-Z0-9]+", m.group(2), m.group(3)
    attr = (r'class=["\'][^"\']*\b%s\b' % re.escape(cls)) if cls else (r'id=["\']%s["\']' % re.escape(idn))
    pat = re.compile(r"<(%s)\b([^>]*%s[^>]*)>(.*?)</\1>" % (tag, attr), re.I | re.S)
    hit = pat.search(body)
    if not hit:
        return None
    href = re.search(r'href=["\']([^"\']*)', hit.group(2))
    return {"text": text_of(hit.group(3)), "href": href.group(1) if href else None}


def capture(url, label, cta=None, timeout=15):
    status, final, headers, body = fetch(url, timeout)
    rec = {
        "label": label,
        "url": url,
        "final_url": final,
        "status": status,
        "x_robots_tag": headers.get("X-Robots-Tag"),
        "captured": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    rec.update(extract(body, cta))
    return rec


FIXTURE = """<!doctype html><html lang="en"><head><title>Harbourline Physio</title>
<link rel="canonical" href="https://example.com/"><meta name="robots" content="index,follow"></head>
<body><main><h1>Welcome</h1><h2>Our services</h2>
<a class="btn-primary" href="/book">Book an assessment</a>
<form action="/api/contact"><input name="email"></form></main></body></html>"""


def self_test():
    fails = 0

    def check(name, ok, detail=""):
        nonlocal fails
        if not ok:
            fails += 1
        print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -> " + str(detail)[:160]) if detail and not ok else ""))

    f = extract(FIXTURE, "a.btn-primary")
    check("title extracted", f["title"] == "Harbourline Physio", f["title"])
    check("single h1 extracted", f["h1"] == ["Welcome"], f["h1"])
    check("canonical extracted", f["canonical"] == "https://example.com/", f["canonical"])
    check("robots meta extracted", f["robots_meta"] == "index,follow", f["robots_meta"])
    check("form action extracted", f["forms"] == ["/api/contact"] and f["form_count"] == 1, f["forms"])
    check("named CTA text and href", f["cta"] == {"text": "Book an assessment", "href": "/book"}, f["cta"])
    check("content hash and word count present", len(f["content_sha256"]) == 16 and f["content_words"] > 3)

    # The case the workflow exists to catch: the h1 becomes a p.
    bad = FIXTURE.replace("<h1>Welcome</h1>", '<p class="hero-title">Physiotherapy in Harbourline</p>')
    b = extract(bad, "a.btn-primary")
    check("no h1 is reported as an empty list, not a default", b["h1"] == [], b["h1"])
    check("content hash changes when the content changes", b["content_sha256"] != f["content_sha256"])

    check("unsupported selector reports an error rather than guessing",
          extract(FIXTURE, "div > span")["cta"] == {"error": "selector not supported: use tag.class, .class or #id"})
    check("absent selector captures as null", extract(FIXTURE, ".does-not-exist")["cta"] is None)
    print("\n%d failure(s)" % fails)
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("url", nargs="?")
    ap.add_argument("--label", default="before", help="before | after | any name")
    ap.add_argument("--out", default=".", help="directory for <label>.json")
    ap.add_argument("--cta", help="selector for the primary call to action: tag.class, .class or #id")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.url or not a.url.startswith(("http://", "https://")):
        print("give an absolute http(s) URL, or --self-test", file=sys.stderr)
        return 2
    try:
        rec = capture(a.url, a.label, a.cta, a.timeout)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print("fetch failed: %s" % e, file=sys.stderr)
        return 1
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "%s.json" % re.sub(r"[^A-Za-z0-9._-]", "-", a.label))
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote %s  (status %s, %d h1, %d forms)" % (path, rec["status"], len(rec["h1"]), rec["form_count"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
