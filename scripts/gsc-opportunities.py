#!/usr/bin/env python3
"""Search Console opportunity analysis: striking distance, CTR, content gaps.

Reads real Search Console performance data and sorts it into the tiers that
decide what to work on next. It is analysis only — it never modifies the site,
never submits anything, and never prints a credential.

Tiers, by average position:
  A  4-10   near page one       highest priority; small changes move these
  B  11-20  striking distance   page one is reachable with focused work
  C  21-40  emerging            topical signal; usually a content decision
  D  any    CTR opportunity     decent position, impressions, poor click rate

Usage:
  gsc-opportunities.py                      summary to stdout
  gsc-opportunities.py --days 28            change the window
  gsc-opportunities.py --report striking    write docs/seo/GSC-STRIKING-DISTANCE.md
  gsc-opportunities.py --report ctr         write docs/seo/GSC-CTR-OPPORTUNITIES.md
  gsc-opportunities.py --report content     write docs/seo/GSC-CONTENT-OPPORTUNITIES.md
  gsc-opportunities.py --report all         write all three
"""
import argparse
import collections
import datetime
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import google_search_console as gsc  # noqa: E402

ROOT = os.path.dirname(HERE)
SITE = os.environ.get("SBS_GSC_SITE", "sc-domain:sitebuilderstack.com")
ORIGIN = "https://sitebuilderstack.com"
DOCS = os.path.join(ROOT, "docs", "seo")
REPORTS = os.path.join(ROOT, "reports")

# Commercial relevance, used only to break ties between similar opportunities.
# A query about Shopify or SEO is closer to the product than one about the
# terminal, so when two rows score alike the commercial one wins.
COMMERCIAL = {
    3: ("launch system", "website launch", "build a website", "build website",
        "shopify seo", "website audit", "claude.md", "claude md"),
    2: ("shopify", "seo", "deploy", "production", "security", "audit", "checklist"),
    1: ("workflow", "prompt", "github actions", "enterprise", "ci"),
}


def commercial_weight(text):
    t = text.lower()
    for score, terms in sorted(COMMERCIAL.items(), reverse=True):
        if any(term in t for term in terms):
            return score
    return 0


def expected_ctr(position):
    """A rough position-to-CTR curve, used only to flag outliers.

    These are order-of-magnitude expectations for spotting a page that
    underperforms its own position. They are not a published dataset and must
    not be presented as one.
    """
    p = max(1.0, position)
    if p <= 1: return 0.28
    if p <= 2: return 0.15
    if p <= 3: return 0.11
    if p <= 5: return 0.07
    if p <= 10: return 0.03
    if p <= 20: return 0.012
    return 0.004


def tier(position):
    """Position tiers. Tier D in the brief means a CTR opportunity, which is a
    separate axis from position — it is computed by ctr_opportunities() rather
    than here, so anything past position 40 is labelled "far" instead."""
    if position < 4: return "A+"
    if position <= 10: return "A"
    if position <= 20: return "B"
    if position <= 40: return "C"
    return "far"


def score(row):
    """Opportunity score. Deliberately simple and explainable.

    Impressions carry the weight because they are the only evidence that demand
    exists. Position is a multiplier because the closer to page one, the less
    work a gain costs. Commercial relevance breaks ties.
    """
    impr, pos = row["impressions"], row["position"]
    if pos <= 3:      prox = 0.5     # already there; less headroom
    elif pos <= 10:   prox = 3.0
    elif pos <= 20:   prox = 2.0
    elif pos <= 40:   prox = 1.0
    else:             prox = 0.3
    return round(impr * prox * (1 + 0.35 * row.get("commercial", 0)), 1)


def fetch(start, end, dims, limit=1000):
    code, d = gsc.search_analytics(SITE, start, end, dims, row_limit=limit)
    if code != 200:
        raise SystemExit("Search Console returned HTTP %s for dims=%s" % (code, dims))
    out = []
    for r in d.get("rows", []):
        rec = dict(zip(dims, r["keys"]))
        rec.update(impressions=r["impressions"], clicks=r["clicks"],
                   ctr=r["ctr"], position=r["position"])
        out.append(rec)
    return out


def window(days):
    end = datetime.date.today()
    return (end - datetime.timedelta(days=days)).isoformat(), end.isoformat()


def first_seen_date():
    """Earliest date with any impressions, so the report cannot overstate history."""
    code, d = gsc.search_analytics(SITE, "2020-01-01",
                                   datetime.date.today().isoformat(), ["date"], 2000)
    rows = [r for r in d.get("rows", []) if r["impressions"] > 0] if code == 200 else []
    return rows[0]["keys"][0] if rows else None


def short(u):
    return u.replace(ORIGIN, "") or "/"


def _rollup(qp, key):
    """Aggregate query+page rows down to one dimension.

    Only used for the CSV path. Impressions and clicks add; position is
    impression-weighted, because a straight mean would let a single-impression
    row at position 90 outvote a hundred impressions at position 3.
    """
    acc = collections.OrderedDict()
    for r in qp:
        e = acc.setdefault(r[key], {key: r[key], "impressions": 0, "clicks": 0,
                                    "_pw": 0.0})
        e["impressions"] += r["impressions"]
        e["clicks"] += r["clicks"]
        e["_pw"] += r["position"] * r["impressions"]
    out = []
    for e in acc.values():
        i = e.pop("_pw")
        e["position"] = (i / e["impressions"]) if e["impressions"] else 100.0
        e["ctr"] = (e["clicks"] / e["impressions"]) if e["impressions"] else 0.0
        out.append(e)
    return out


def analyse(days, csv_path=None):
    if csv_path:
        qp = load_csv(csv_path)
        start, end = window(days)
        pages, queries = _rollup(qp, "page"), _rollup(qp, "query")
        first = None
    else:
        start, end = window(days)
        qp = fetch(start, end, ["query", "page"])
        pages = fetch(start, end, ["page"])
        queries = fetch(start, end, ["query"])
        first = first_seen_date()
    for r in qp:
        r["commercial"] = commercial_weight(r["query"])
        r["score"] = score(r)
        r["tier"] = tier(r["position"])
    for r in pages:
        r["commercial"] = commercial_weight(r["page"])
        r["score"] = score(r)
        r["tier"] = tier(r["position"])
    return {"start": start, "end": end, "qp": qp, "pages": pages,
            "queries": queries, "first_seen": first,
            "source": "CSV export" if csv_path else "Search Console API"}


def ctr_opportunities(qp):
    """Rows where the click rate is well under what the position would suggest."""
    out = []
    for r in qp:
        if r["impressions"] < 5 or r["position"] > 30:
            continue
        exp = expected_ctr(r["position"])
        if r["ctr"] < exp * 0.5:
            out.append(dict(r, expected=exp, gap=round((exp - r["ctr"]) * r["impressions"], 1)))
    return sorted(out, key=lambda r: -r["gap"])


def hdr(a, title, extra=""):
    n_days = (datetime.date.fromisoformat(a["end"]) -
              datetime.date.fromisoformat(a["start"])).days
    total_i = sum(r["impressions"] for r in a["pages"])
    total_c = sum(r["clicks"] for r in a["pages"])
    return (
        "# %s\n\n"
        "Generated by `scripts/gsc-opportunities.py` from live Search Console data. "
        "Regenerate rather than editing by hand.\n\n"
        "| | |\n| --- | --- |\n"
        "| Window | %s to %s (%d days) |\n"
        "| First impression on record | %s |\n"
        "| Impressions | %d |\n| Clicks | %d |\n"
        "| Queries with impressions | %d |\n| Pages with impressions | %d |\n"
        "| Source | %s |\n\n"
        "%s\n"
        % (title, a["start"], a["end"], n_days, a["first_seen"] or "none",
           total_i, total_c, len(a["queries"]), len(a["pages"]), a.get("source", "Search Console API"), extra))


def caveat(a):
    return (
        "> **Read this before acting on the numbers.** Search Console finalises data "
        "with a lag of roughly two days, so the most recent rows are provisional and "
        "will move. At this volume an average position computed over a handful of "
        "impressions is noisy — treat a single row with under about 10 impressions as "
        "a hint, not a finding. Nothing here is a projection; every figure is what "
        "Google reported.\n")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8").write(text)
    print("wrote %s (%d bytes)" % (path, len(text)))


def report_striking(a):
    rows = sorted([r for r in a["qp"] if r["tier"] in ("A+", "A", "B", "C")],
                  key=lambda r: -r["score"])
    t = hdr(a, "Search Console striking-distance report") + caveat(a) + "\n"
    for name, tiers, blurb in [
        ("Tier A — near page one (positions 4–10)", ("A",),
         "Highest priority. These are close enough that metadata, intent alignment "
         "and a few internal links can move them."),
        ("Tier A+ — already ranking (positions 1–3)", ("A+",),
         "Protect rather than optimise. Changing a page that already ranks is the "
         "easiest way to lose the position."),
        ("Tier B — striking distance (positions 11–20)", ("B",),
         "Page one is reachable with focused work on one page each."),
        ("Tier C — emerging (positions 21–40)", ("C",),
         "Read these as topical signal. Usually a content decision, not an "
         "optimisation one."),
    ]:
        sel = [r for r in rows if r["tier"] in tiers][:25]
        t += "\n## %s\n\n%s\n\n" % (name, blurb)
        if not sel:
            t += "_No rows in this tier for the current window._\n"
            continue
        t += ("| Score | Query | Page | Pos | Impr | Clicks | CTR |\n"
              "| ---: | --- | --- | ---: | ---: | ---: | ---: |\n")
        for r in sel:
            t += "| %s | %s | `%s` | %.1f | %d | %d | %.1f%% |\n" % (
                r["score"], r["query"], short(r["page"]), r["position"],
                r["impressions"], r["clicks"], r["ctr"] * 100)
    # A tier full of one-impression rows is noise, and presenting it as a
    # priority list would be worse than presenting nothing. Say so in the
    # report itself so a future regeneration cannot quietly drop the warning.
    a_rows = [r for r in rows if r["tier"] in ("A", "A+")]
    thin = [r for r in a_rows if r["impressions"] < 5]
    t += "\n## Reading this honestly\n\n"
    if a_rows and len(thin) == len(a_rows):
        t += ("**Every row in Tier A has fewer than 5 impressions.** At that volume "
              "an average position is close to meaningless — one impression at "
              "position 6 produces the same \"position 6\" as a page that genuinely "
              "ranks there. Several of these rows are also long verbatim phrases "
              "lifted from an article body rather than queries anyone types.\n\n"
              "**Do not treat this tier as a work list.** The page-level table below "
              "is the more reliable signal at this stage.\n\n")
    far = [r for r in a["pages"] if r["position"] > 40]
    if far and len(far) >= len(a["pages"]) / 2:
        t += ("Most pages with real impression volume sit past position 40. Metadata "
              "and internal linking do not move a page from 50 to 10 — that gap is "
              "an authority problem, not an on-page one. The on-page work worth "
              "doing here is where a page is thin relative to the demand it is "
              "already attracting.\n")
    t += "\n## Page opportunities\n\n"
    t += ("| URL | Clicks | Impr | Pos | CTR | Tier | Score |\n"
          "| --- | ---: | ---: | ---: | ---: | --- | ---: |\n")
    for r in sorted(a["pages"], key=lambda r: -r["score"])[:30]:
        t += "| `%s` | %d | %d | %.1f | %.1f%% | %s | %s |\n" % (
            short(r["page"]), r["clicks"], r["impressions"], r["position"],
            r["ctr"] * 100, r["tier"], r["score"])
    t += ("\n## How the score works\n\n"
          "`impressions × proximity × (1 + 0.35 × commercial relevance)`\n\n"
          "Impressions carry the weight because they are the only evidence that "
          "demand exists at all. Proximity rewards positions 4–20, where a gain is "
          "cheapest, and discounts positions 1–3 (little headroom) and 40+ (a long "
          "way to go). Commercial relevance breaks ties between similar rows.\n\n"
          "It is deliberately simple. A score is a sort order, not a forecast.\n")
    return t


def report_ctr(a):
    ops = ctr_opportunities(a["qp"])
    t = hdr(a, "Search Console CTR opportunities") + caveat(a)
    t += ("\nRows where the click rate is less than half what the position would "
          "normally produce. The expected-CTR curve below is a rough internal "
          "heuristic for spotting outliers — it is not a published dataset and is "
          "not presented as one.\n\n")
    if not ops:
        t += ("## No CTR opportunities in this window\n\n"
              "Either no row has enough impressions to judge, or nothing is "
              "underperforming its position. At low volume this is the expected "
              "result, and inventing rewrites without evidence would be worse than "
              "leaving titles alone.\n")
        return t
    t += ("| Query | Page | Pos | Impr | CTR | Expected | Missed clicks |\n"
          "| --- | --- | ---: | ---: | ---: | ---: | ---: |\n")
    for r in ops[:30]:
        t += "| %s | `%s` | %.1f | %d | %.1f%% | %.1f%% | %.1f |\n" % (
            r["query"], short(r["page"]), r["position"], r["impressions"],
            r["ctr"] * 100, r["expected"] * 100, r["gap"])
    t += ("\n## Before rewriting anything\n\n"
          "A low CTR at position 40 means nobody scrolled that far, not that the "
          "title is wrong. Only act where the position is genuinely visible "
          "(roughly 10 or better) and the impressions are enough to be real. "
          "Never make a title more clickable than the page is accurate.\n")
    return t


def report_content(a):
    known = {short(r["page"]) for r in a["pages"]}
    byq = collections.defaultdict(lambda: {"impressions": 0, "clicks": 0,
                                           "pages": set(), "position": []})
    for r in a["qp"]:
        e = byq[r["query"]]
        e["impressions"] += r["impressions"]
        e["clicks"] += r["clicks"]
        e["pages"].add(short(r["page"]))
        e["position"].append(r["position"])
    gaps = []
    for q, e in byq.items():
        pos = sum(e["position"]) / len(e["position"])
        gaps.append({"query": q, "impressions": e["impressions"], "clicks": e["clicks"],
                     "position": pos, "pages": sorted(e["pages"]),
                     "commercial": commercial_weight(q),
                     "cannibal": len(e["pages"]) > 1})
    gaps.sort(key=lambda g: (-g["impressions"], g["position"]))

    t = hdr(a, "Search Console content opportunities") + caveat(a)
    t += ("\nThis report says what the data supports. It does **not** propose an "
          "article per query — most rows here are served well enough by a page that "
          "already exists, and the correct action is to improve that page or to do "
          "nothing.\n\n## Queries by demand\n\n")
    t += ("| Query | Impr | Clicks | Avg pos | Ranking page(s) | Commercial |\n"
          "| --- | ---: | ---: | ---: | --- | ---: |\n")
    for g in gaps[:40]:
        t += "| %s | %d | %d | %.1f | %s | %s |\n" % (
            g["query"], g["impressions"], g["clicks"], g["position"],
            ", ".join("`%s`" % p for p in g["pages"]), g["commercial"])

    cann = [g for g in gaps if g["cannibal"] and g["impressions"] >= 3]
    t += "\n## Possible cannibalisation\n\n"
    if cann:
        t += ("More than one page taking impressions for the same query. Two pages "
              "alternating on one query is the signal to merge, not to optimise "
              "both.\n\n| Query | Impr | Pages |\n| --- | ---: | --- |\n")
        for g in cann:
            t += "| %s | %d | %s |\n" % (g["query"], g["impressions"],
                                         ", ".join("`%s`" % p for p in g["pages"]))
    else:
        t += "_No query is currently split across more than one page._\n"
    return t



# ── CSV fallback ────────────────────────────────────────────────────────────
# Used when the Search Console API is not authorised for this environment. The
# export must be the "Queries + Pages" view so both dimensions are on one row;
# Search Console's per-query and per-page exports cannot be joined after the
# fact, and guessing the join would invent data.
CSV_HELP = """Export from Search Console:

  Performance -> Search results
  Set the date range (90 days recommended)
  Open the 'Pages' tab, click a page, then the 'Queries' tab  -- or use the
  Search Analytics API / Looker Studio to get Query AND Page on the same row.
  Export -> Download CSV

Required columns (header names are matched case-insensitively):
  Query, Page, Clicks, Impressions, CTR, Position

A per-query-only or per-page-only export cannot be used: this analysis needs
both dimensions on the same row and will not fabricate the join."""


def load_csv(path):
    """Read a Search Console export into the same row shape fetch() returns."""
    import csv as _csv

    want = {"query": "query", "page": "page", "clicks": "clicks",
            "impressions": "impressions", "ctr": "ctr", "position": "position"}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rd = _csv.DictReader(fh)
        cols = {}
        for name in rd.fieldnames or []:
            key = name.strip().lower().replace(" ", "").replace("_", "")
            for w in want:
                if key == w or key.startswith(w):
                    cols[w] = name
        missing = [w for w in want if w not in cols]
        if missing:
            raise SystemExit("CSV is missing column(s): %s\n\n%s"
                             % (", ".join(missing), CSV_HELP))
        out = []
        for r in rd:
            def num(k, default=0.0):
                v = (r.get(cols[k]) or "").strip().replace("%", "").replace(",", "")
                try:
                    return float(v)
                except ValueError:
                    return default
            ctr = num("ctr")
            if ctr > 1:          # exports write CTR as a percentage
                ctr /= 100.0
            out.append({"query": (r.get(cols["query"]) or "").strip(),
                        "page": (r.get(cols["page"]) or "").strip(),
                        "clicks": int(num("clicks")),
                        "impressions": int(num("impressions")),
                        "ctr": ctr, "position": num("position", 100.0)})
    if not out:
        raise SystemExit("CSV contained no rows.\n\n" + CSV_HELP)
    return out


# ── Recommended action ──────────────────────────────────────────────────────
def recommended_action(row):
    """What to actually do with this row.

    Deliberately conservative: most rows deserve no action at all, and saying
    so is more useful than inventing a task per query. Thresholds are stated
    rather than tuned, so a reader can disagree with them.
    """
    pos, impr, clicks = row["position"], row["impressions"], row["clicks"]
    ctr = row["ctr"]
    if impr < 3:
        return "Watch — too few impressions to act on"
    if pos < 4:
        if ctr == 0 and impr >= 5:
            return "Rewrite title/description — ranking well, no clicks"
        return "Protect — already ranking; change nothing without reason"
    if pos <= 10:
        if ctr < expected_ctr(pos) / 2:
            return "Rewrite title/description, confirm intent match"
        return "Strengthen on-page coverage and internal links"
    if pos <= 20:
        return "Expand the section that answers this, add internal links"
    if pos <= 40:
        return "Assess intent match — may need its own section or page"
    return "No action — position too low for metadata work to matter"


def report_opportunities(a):
    """The ranked opportunity table in the format the brief asks for."""
    rows = sorted(a["qp"], key=lambda r: -r["score"])
    acted = [r for r in rows if r["tier"] in ("A", "B") or
             (r["tier"] == "A+" and r["ctr"] == 0 and r["impressions"] >= 5)]

    t = hdr(a, "Search Console opportunities") + caveat(a)
    t += ("\nRanked by opportunity score: impressions weighted by how close the "
          "position already is, with commercial relevance breaking ties. The "
          "scoring model is in `scripts/gsc-opportunities.py` and is meant to be "
          "argued with rather than trusted.\n\n")

    t += "## Priority rows — positions 4–20, plus high-position zero-CTR\n\n"
    if acted:
        t += ("| URL | Query | Position | Impressions | Clicks | CTR | Opportunity Score | Recommended Action |\n"
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |\n")
        for r in acted:
            t += "| `%s` | %s | %.1f | %d | %d | %.1f%% | %.1f | %s |\n" % (
                short(r["page"]), r["query"], r["position"], r["impressions"],
                r["clicks"], r["ctr"] * 100, r["score"], recommended_action(r))
    else:
        t += "_No row currently qualifies._\n"

    t += "\n## Everything else, by score\n\n"
    t += ("| URL | Query | Position | Impressions | Clicks | CTR | Opportunity Score | Recommended Action |\n"
          "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |\n")
    rest = [r for r in rows if r not in acted][:40]
    for r in rest:
        t += "| `%s` | %s | %.1f | %d | %d | %.1f%% | %.1f | %s |\n" % (
            short(r["page"]), r["query"], r["position"], r["impressions"],
            r["clicks"], r["ctr"] * 100, r["score"], recommended_action(r))

    t += ("\n## How to regenerate\n\n"
          "```\nscripts/gsc-opportunities.py --days 90 --report opportunities\n```\n\n"
          "Without API access, export the Queries+Pages view from Search Console "
          "and pass it in:\n\n```\nscripts/gsc-opportunities.py --csv export.csv "
          "--report opportunities\n```\n")
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--report",
                choices=["striking", "ctr", "content", "opportunities", "all"])
    ap.add_argument("--csv", help="Search Console CSV export "
                                  "(Query+Page+Clicks+Impressions+CTR+Position)")
    args = ap.parse_args()

    a = analyse(args.days, csv_path=args.csv)
    if not args.report:
        print("window %s to %s   first impression %s" %
              (a["start"], a["end"], a["first_seen"]))
        print("impressions %d   clicks %d   queries %d   pages %d\n" % (
            sum(r["impressions"] for r in a["pages"]),
            sum(r["clicks"] for r in a["pages"]),
            len(a["queries"]), len(a["pages"])))
        counts = collections.Counter(r["tier"] for r in a["qp"])
        for k in ("A+", "A", "B", "C", "far"):
            print("  tier %-4s %4d query/page rows" % (k, counts.get(k, 0)))
        print("  CTR opportunities: %d" % len(ctr_opportunities(a["qp"])))
        return

    if args.report in ("striking", "all"):
        write(os.path.join(DOCS, "GSC-STRIKING-DISTANCE.md"), report_striking(a))
    if args.report in ("ctr", "all"):
        write(os.path.join(DOCS, "GSC-CTR-OPPORTUNITIES.md"), report_ctr(a))
    if args.report in ("content", "all"):
        write(os.path.join(DOCS, "GSC-CONTENT-OPPORTUNITIES.md"), report_content(a))
    if args.report in ("opportunities", "all"):
        os.makedirs(REPORTS, exist_ok=True)
        write(os.path.join(REPORTS, "gsc-opportunities.md"), report_opportunities(a))


if __name__ == "__main__":
    main()
