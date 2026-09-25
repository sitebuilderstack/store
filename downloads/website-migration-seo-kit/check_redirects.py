#!/usr/bin/env python3
"""check_redirects.py — read-only redirect validation for a site move.

Reads a URL map (CSV) and, for every row, requests the SOURCE URL without
following redirects, walks the chain hop by hop, and reports whether it ends
where the map says it should. It also checks page identity: the final page's
<title> (or <h1>) must contain the identity string from the map, so a redirect
that lands on the right URL but the wrong content (a homepage dump) still
fails.

Bounded by design: a maximum number of rows, a per-request timeout, a maximum
hop count, and a hard stop on the first malformed row. Read-only: GET and HEAD
only; nothing is written anywhere but the report.

CSV columns (header row required):
    source_url,target_url,expected_status,identity,notes
    - source_url      the old URL (absolute)
    - target_url      where it must end up (absolute), or empty for "must 200 as is"
    - expected_status status the SOURCE must return: 301, 308, 200, 410
    - identity        text the final page's <title> or <h1> must contain (optional)
    - notes           ignored

Usage:
    python3 check_redirects.py url-map.csv [--limit 500] [--timeout 8] [--max-hops 5]
                               [--host-rewrite old=new] [--report report.md]

--host-rewrite lets you test a map written for production against staging
or local copies: every URL whose host is `old` is requested at `new` instead,
and destinations are compared after the same rewrite. Exit status: 0 all rows pass, 1 any failure, 2 usage.

Python 3.8+, standard library only. No dependencies, no credentials.
"""
import argparse
import csv
import html
import io
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "sitebuilderstack-check-redirects/1.0 (read-only migration check)"
OK_STATUSES = {"200", "301", "302", "307", "308", "410", "404"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url, timeout):
    """One request, redirects NOT followed. Returns (status, location, body_head)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, r.headers.get("Location"), r.read(65536).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            body = e.read(65536).decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, e.headers.get("Location"), body
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return None, None, "error: %s" % getattr(e, "reason", e)


def rewrite(url, mapping):
    if not mapping:
        return url
    p = urllib.parse.urlsplit(url)
    if p.netloc in mapping:
        return urllib.parse.urlunsplit((p.scheme, mapping[p.netloc], p.path, p.query, p.fragment))
    return url


def identity_of(body):
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    if m:
        return html.unescape(re.sub(r"\s+", " ", m.group(1))).strip()
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.I | re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""


def check_row(row, n, args, mapping):
    src, tgt, exp, ident = row["source_url"].strip(), row["target_url"].strip(), row["expected_status"].strip(), row.get("identity", "").strip()
    if not src.startswith(("http://", "https://")):
        raise ValueError("row %d: source_url is not absolute: %r" % (n, src))
    if tgt and not tgt.startswith(("http://", "https://")):
        raise ValueError("row %d: target_url is not absolute: %r" % (n, tgt))
    if exp not in OK_STATUSES:
        raise ValueError("row %d: expected_status %r is not one of %s" % (n, exp, sorted(OK_STATUSES)))

    hops, url, status, location, body = [], src, None, None, ""
    for _ in range(args.max_hops + 1):
        status, location, body = fetch(rewrite(url, mapping), args.timeout)
        hops.append((url, status))
        if status is None:
            return dict(row=n, source=src, ok=False, hops=hops, final=url, why="request failed: " + body)
        if status in (301, 302, 307, 308) and location:
            url = urllib.parse.urljoin(url, location)
            if len(hops) > args.max_hops:
                return dict(row=n, source=src, ok=False, hops=hops, final=url, why="more than %d hops" % args.max_hops)
            if any(h[0] == url for h in hops):
                return dict(row=n, source=src, ok=False, hops=hops, final=url, why="redirect loop")
            continue
        break

    first_status = str(hops[0][1])
    final_url, final_status = hops[-1][0], hops[-1][1]
    problems = []
    if first_status != exp:
        problems.append("source returned %s, expected %s" % (first_status, exp))
    if exp in ("301", "308"):
        if len(hops) - 1 != 1:
            problems.append("%d hops, expected exactly 1" % (len(hops) - 1))
        # Compared after the same host rewrite on both sides, so a staging
        # copy that redirects to staging URLs can be checked against a map
        # written for production.
        if tgt and rewrite(final_url, mapping).rstrip("/") != rewrite(tgt, mapping).rstrip("/"):
            problems.append("landed on %s, expected %s" % (final_url, tgt))
        if final_status != 200:
            problems.append("final page returned %s, expected 200" % final_status)
    if exp == "200" and final_status != 200:
        problems.append("page returned %s" % final_status)
    if ident and final_status == 200:
        got = identity_of(body)
        if ident.lower() not in got.lower():
            problems.append("page identity %r does not contain %r" % (got[:60], ident))
    return dict(row=n, source=src, ok=not problems, hops=hops, final=final_url, why="; ".join(problems))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("csv")
    ap.add_argument("--limit", type=int, default=500, help="maximum rows to check (default 500)")
    ap.add_argument("--timeout", type=float, default=8.0, help="seconds per request (default 8)")
    ap.add_argument("--max-hops", type=int, default=5, help="fail beyond this many redirects (default 5)")
    ap.add_argument("--host-rewrite", action="append", default=[], metavar="OLD=NEW", help="request OLD host at NEW host (staging/local tests)")
    ap.add_argument("--report", help="write a Markdown report here")
    args = ap.parse_args()

    mapping = {}
    for m in args.host_rewrite:
        if "=" not in m:
            print("bad --host-rewrite %r (want old=new)" % m, file=sys.stderr)
            return 2
        old, new = m.split("=", 1)
        mapping[old] = new

    try:
        with io.open(args.csv, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            need = {"source_url", "target_url", "expected_status"}
            if not reader.fieldnames or not need.issubset(reader.fieldnames):
                print("CSV needs columns: source_url,target_url,expected_status (got %s)" % reader.fieldnames, file=sys.stderr)
                return 2
            rows = list(reader)
    except (OSError, csv.Error) as e:
        print("cannot read %s: %s" % (args.csv, e), file=sys.stderr)
        return 2
    if len(rows) > args.limit:
        print("map has %d rows; checking the first %d (raise --limit deliberately)" % (len(rows), args.limit))
        rows = rows[: args.limit]

    results, started = [], time.time()
    for n, row in enumerate(rows, 2):
        try:
            results.append(check_row(row, n, args, mapping))
        except ValueError as e:
            print("STOP — %s. Fix the map and re-run; nothing after this row was checked." % e, file=sys.stderr)
            return 2
    failed = [r for r in results if not r["ok"]]
    lines = ["# Redirect check — %s" % time.strftime("%Y-%m-%d %H:%M"), "",
             "Rows checked: %d · passed: %d · failed: %d · %.1fs" % (len(results), len(results) - len(failed), len(failed), time.time() - started), ""]
    if mapping:
        lines += ["Host rewrites: " + ", ".join("%s→%s" % kv for kv in mapping.items()), ""]
    lines += ["| row | source | result | chain | problem |", "|---|---|---|---|---|"]
    for r in results:
        chain = " → ".join("%s (%s)" % (u, s) for u, s in r["hops"])
        lines.append("| %d | %s | %s | %s | %s |" % (r["row"], r["source"], "PASS" if r["ok"] else "FAIL", chain, r["why"]))
    text = "\n".join(lines) + "\n"
    print(text)
    if args.report:
        with io.open(args.report, "w", encoding="utf-8") as fh:
            fh.write(text)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
