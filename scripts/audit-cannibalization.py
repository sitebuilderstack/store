#!/usr/bin/env python3
"""Content overlap and cannibalisation audit across the local content library.

Reads the source files rather than crawling, so it sees every page whether or
not Google has found it yet, and runs without network access.

For each indexable page it extracts the title, h1, meta description, headings
and the terms those headings are built from, then compares every pair. Overlap
is scored on two axes that disagree usefully:

  topic   how much of the vocabulary is shared (Jaccard over heading terms)
  intent  whether the two pages are trying to answer the same question,
          approximated by title-phrase overlap after stopwords

Two pages about the same topic with different intent are complementary — a hub
and a guide, or a guide and a tool, should look like that. Two pages with the
same intent are the ones that compete, whatever their topic scores.

Classification is deliberately conservative. Anything the script is not sure
about lands in "moderate overlap" for a human to read, because an automated
redirect of a page that was merely similar is far more expensive than a report
row nobody acts on.

Real Search Console evidence, when available, upgrades a pair: if one query
returns both URLs, they are competing in fact rather than in theory.

Usage:
  audit-cannibalization.py                 write reports/cannibalization-audit.md
  audit-cannibalization.py --no-gsc        skip the Search Console cross-check
  audit-cannibalization.py --self-test     prove the classifier fires and stays silent
"""
import argparse
import collections
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPORTS = os.path.join(ROOT, "reports")
ORIGIN = "https://sitebuilderstack.com"

STOP = set("""a an the and or but if then than that this these those of in on at to for with
from by as is are was were be been being it its it's you your we our they their he she his her
how what when where which who why do does did can could should would will shall may might must
not no nor own same so too very just about into over under again further once here there all any
both each few more most other some such only own s t don now i me my myself us ours""".split())

# Words that carry no distinguishing signal on this particular site: every page
# is about Claude Code and websites, so counting them would make everything
# look like everything else.
SITE_NOISE = {"claude", "code", "website", "websites", "site", "sites", "web",
              "guide", "using", "use", "make", "build", "works", "work"}


def words(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text).lower()
    out = [w for w in re.findall(r"[a-z][a-z0-9.+#-]{1,}", text)
           if w not in STOP and len(w) > 2]
    return out


def terms(text):
    return set(words(text)) - SITE_NOISE


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


# ── extraction ──────────────────────────────────────────────────────────────
def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s or "")).strip()


def headings(body):
    return [strip_tags(m.group(1))
            for m in re.finditer(r"<h[23][^>]*>(.*?)</h[23]>", body, re.S | re.I)]


def load_articles():
    path = os.path.join(ROOT, "content", "articles.json")
    if not os.path.exists(path):
        return []
    d = json.load(open(path, encoding="utf-8"))
    arts = d if isinstance(d, list) else d.get("articles", d)
    seq = arts if isinstance(arts, list) else list(arts.values())
    out = []
    for a in seq:
        f = os.path.join(ROOT, "content", "articles", a["file"])
        body = open(f, encoding="utf-8").read() if os.path.exists(f) else ""
        out.append({
            "url": "/blogs/guides/" + a["handle"],
            "kind": "guide",
            "title": a.get("seoTitle") or a.get("title", ""),
            "h1": a.get("title", ""),
            "desc": a.get("seoDescription", ""),
            "headings": headings(body),
            "body": body,
            "source": os.path.relpath(f, ROOT),
        })
    return out


def load_dir(subdir, prefix, kind):
    d = os.path.join(ROOT, "content", subdir)
    out = []
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        if not fn.endswith((".html", ".md")):
            continue
        body = open(os.path.join(d, fn), encoding="utf-8").read()
        slug = os.path.splitext(fn)[0].lstrip("_")
        m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S | re.I)
        h1 = strip_tags(m.group(1)) if m else ""
        if not h1:
            m = re.search(r"^#\s+(.+)$", body, re.M)
            h1 = m.group(1).strip() if m else slug.replace("-", " ").title()
        hs = headings(body) or [l[3:].strip() for l in body.splitlines()
                                if l.startswith("## ")]
        out.append({"url": prefix + slug, "kind": kind, "title": h1, "h1": h1,
                    "desc": "", "headings": hs, "body": body,
                    "source": os.path.relpath(os.path.join(d, fn), ROOT)})
    return out


def corpus():
    pages = load_articles()
    pages += load_dir("pillars", "/pages/", "hub")
    pages += load_dir("tools", "/pages/", "tool")
    pages += load_dir("pages", "/pages/", "page")
    pages += load_dir("products", "/products/", "product")
    for p in pages:
        p["terms"] = terms(" ".join(p["headings"]) + " " + p["h1"])
        p["intent"] = terms(p["title"] + " " + p["h1"])
    return [p for p in pages if p["terms"] or p["intent"]]


# ── classification ──────────────────────────────────────────────────────────
def classify(topic, intent, same_kind, shared_query):
    """Return (label, why). Order matters: the strongest evidence decides."""
    if topic >= 0.55 and intent >= 0.55:
        return "duplicate/near duplicate", "near-identical vocabulary and intent"
    if shared_query:
        return ("probable cannibalization",
                "one Search Console query returns both URLs")
    # Intent alone is not enough on this site. Every guide title contains the
    # same few words, so two pages can share "audit" or "seo" in their titles
    # while covering entirely different ground. Requiring topic overlap as well
    # is what separates "both titles say audit" from "both pages are the audit
    # page". Without this guard the report flags security-vs-accessibility, and
    # a report that cries wolf gets ignored wholesale.
    if intent >= 0.45 and topic >= 0.25 and same_kind:
        return ("probable cannibalization",
                "same page type, same subject, same promise")
    if topic >= 0.30 or intent >= 0.30:
        return "moderate overlap", "shared subject, different framing"
    return None, ""


def analyse(pages, shared_queries):
    rows = []
    for i in range(len(pages)):
        for j in range(i + 1, len(pages)):
            a, b = pages[i], pages[j]
            topic = jaccard(a["terms"], b["terms"])
            intent = jaccard(a["intent"], b["intent"])
            sq = shared_queries.get(frozenset((a["url"], b["url"])), [])
            label, why = classify(topic, intent, a["kind"] == b["kind"], bool(sq))
            if not label:
                continue
            # A hub and one of its own guides is the architecture working, not a
            # fault, so it is recorded as intentional rather than as overlap.
            if {a["kind"], b["kind"]} == {"hub", "guide"} and label == "moderate overlap":
                label, why = "intentional complementary", "hub and supporting guide"
            rows.append({"a": a, "b": b, "topic": topic, "intent": intent,
                         "label": label, "why": why, "queries": sq})
    order = {"duplicate/near duplicate": 0, "probable cannibalization": 1,
             "moderate overlap": 2, "intentional complementary": 3}
    rows.sort(key=lambda r: (order[r["label"]], -(r["topic"] + r["intent"])))
    return rows


def gsc_shared_queries(days=90):
    """Queries where Google returns more than one of our URLs. Real evidence."""
    try:
        sys.path.insert(0, HERE)
        import datetime
        import google_search_console as gsc
        end = datetime.date.today()
        start = (end - datetime.timedelta(days=days)).isoformat()
        code, d = gsc.search_analytics("sc-domain:sitebuilderstack.com", start,
                                       end.isoformat(), ["query", "page"], 5000)
        if code != 200:
            return {}, "Search Console returned HTTP %s" % code
    except Exception as e:                                    # noqa: BLE001
        return {}, "Search Console unavailable (%s)" % type(e).__name__
    byq = collections.defaultdict(list)
    for r in d.get("rows", []):
        q, page = r["keys"]
        byq[q].append((page.replace(ORIGIN, "") or "/", r["impressions"]))
    out = collections.defaultdict(list)
    for q, pages in byq.items():
        urls = sorted({p for p, _ in pages})
        if len(urls) < 2:
            continue
        for i in range(len(urls)):
            for j in range(i + 1, len(urls)):
                out[frozenset((urls[i], urls[j]))].append(q)
    return out, None


ACTIONS = {
    "duplicate/near duplicate":
        "Consolidate into one URL and 301 the other. Two pages this similar "
        "cannot both be the best answer.",
    "probable cannibalization":
        "Decide which URL owns the query, then differentiate the other's title, "
        "h1 and opening — or merge. Do not optimise both.",
    "moderate overlap":
        "Usually correct as-is. Confirm the titles promise different things, and "
        "that each links to the other rather than repeating it.",
    "intentional complementary":
        "No action. Confirm the hub links down and the guide links up.",
}


def report(rows, pages, gsc_note):
    n = collections.Counter(r["label"] for r in rows)
    t = ["# Content overlap and cannibalisation audit", "",
         "Generated by `scripts/audit-cannibalization.py`. Regenerate rather than "
         "editing by hand.", "",
         "| | |", "| --- | --- |",
         "| Pages compared | %d |" % len(pages),
         "| Pairs reported | %d |" % len(rows),
         "| Search Console cross-check | %s |" % (gsc_note or "live query data, 90 days"),
         "", "Scored on two axes. **Topic** is shared heading vocabulary; "
         "**intent** is shared title and h1 vocabulary. High topic with low "
         "intent is the healthy shape for a hub and its guides — the pages are "
         "about the same subject and promise different things. High intent is "
         "what competes.", "",
         "Terms common to the whole site (`claude`, `code`, `website`) are "
         "excluded, or every page would look like every other page.", ""]

    for label in ("duplicate/near duplicate", "probable cannibalization",
                  "moderate overlap", "intentional complementary"):
        sel = [r for r in rows if r["label"] == label]
        t += ["## %s — %d" % (label.capitalize(), len(sel)), "",
              "_%s_" % ACTIONS[label], ""]
        if not sel:
            t += ["None found.", ""]
            continue
        t += ["| A | B | Topic | Intent | Evidence |",
              "| --- | --- | ---: | ---: | --- |"]
        for r in sel[:40]:
            ev = r["why"]
            if r["queries"]:
                ev += " — e.g. `%s`" % r["queries"][0][:70]
            t += ["| `%s` | `%s` | %.2f | %.2f | %s |" %
                  (r["a"]["url"], r["b"]["url"], r["topic"], r["intent"], ev)]
        if len(sel) > 40:
            t += ["", "_%d further pairs omitted._" % (len(sel) - 40)]
        t += [""]

    t += ["## How to read a row you disagree with", "",
          "The thresholds are in `classify()` and are meant to be argued with. "
          "A pair landing in the wrong bucket is a reason to change the "
          "threshold and re-run, not to edit this file.", ""]
    return "\n".join(t) + "\n"


# ── self-test ───────────────────────────────────────────────────────────────
def self_test():
    """Prove each classification fires on a crafted case and stays silent on a
    clean one. A classifier that has only been seen agreeing is not evidence."""
    ok, bad = [], []

    def check(name, got, want):
        (ok if got == want else bad).append("%s: got %r want %r" % (name, got, want))

    check("identical pages",
          classify(0.9, 0.9, True, False)[0], "duplicate/near duplicate")
    check("shared query is cannibalisation",
          classify(0.1, 0.1, False, True)[0], "probable cannibalization")
    check("same kind, same intent, same subject",
          classify(0.4, 0.5, True, False)[0], "probable cannibalization")
    check("same title words but different subject is only moderate",
          classify(0.11, 0.5, True, False)[0], "moderate overlap")
    check("same intent, different kind is not automatic",
          classify(0.2, 0.5, False, False)[0], "moderate overlap")
    check("shared subject only",
          classify(0.35, 0.1, False, False)[0], "moderate overlap")
    check("unrelated pages stay silent",
          classify(0.05, 0.05, True, False)[0], None)
    check("unrelated pages stay silent even when same kind",
          classify(0.2, 0.2, True, False)[0], None)

    # The site-noise guard: two pages sharing only site-wide words must not pair.
    a = terms("Build a website with Claude Code")
    b = terms("Claude Code website guide")
    check("site-noise alone scores zero", jaccard(a, b) < 0.3, True)

    for line in ok:
        print("  ok   %s" % line)
    for line in bad:
        print("  FAIL %s" % line)
    print("\n%d passed, %d failed" % (len(ok), len(bad)))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-gsc", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(self_test())

    pages = corpus()
    shared, note = ({}, "skipped") if args.no_gsc else gsc_shared_queries()
    rows = analyse(pages, shared)
    os.makedirs(REPORTS, exist_ok=True)
    out = os.path.join(REPORTS, "cannibalization-audit.md")
    open(out, "w", encoding="utf-8").write(report(rows, pages, note))
    n = collections.Counter(r["label"] for r in rows)
    print("compared %d pages" % len(pages))
    for k in ("duplicate/near duplicate", "probable cannibalization",
              "moderate overlap", "intentional complementary"):
        print("  %-28s %d" % (k, n.get(k, 0)))
    print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
