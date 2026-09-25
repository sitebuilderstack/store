#!/usr/bin/env python3
"""weekly_check.py — read-only weekly inspection of a website you own.

Given a small config (a list of URLs and, optionally, a string each must
contain), it fetches every URL from the outside, records status and final URL,
checks the TLS certificate's days to expiry for https hosts, checks that every
same-host link on each page resolves (bounded), and writes a Markdown report
with one line per check and the evidence for it. It changes nothing: GET and
HEAD requests only.

Config is JSON:
    {
      "pages": [
        {"url": "https://example.com/", "expect": "Example Co"},
        {"url": "https://example.com/contact", "expect": "<form"}
      ],
      "max_links": 100,
      "timeout": 8,
      "min_cert_days": 14
    }

Usage:
    python3 weekly_check.py check.json [--report report.md]

Exit 0 when every check passes, 1 when any fails, 2 on a config error.
What this does NOT check, because it cannot from outside: that a form
delivers, that a backup restores, that a dependency is current. Those are on
the checklist as manual items for a reason.
Python 3.8+, standard library only.
"""
import argparse
import datetime
import html
import io
import json
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "sitebuilderstack-weekly-check/1.0 (read-only)"


def fetch(url, timeout, method="GET"):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(400000).decode("utf-8", "replace") if method == "GET" else ""
            return r.status, r.geturl(), body, ""
    except urllib.error.HTTPError as e:
        return e.code, e.geturl() or url, "", ""
    except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as e:
        return None, url, "", "request failed: %s" % getattr(e, "reason", e)


def cert_days(host, port, timeout):
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=timeout) as s, ctx.wrap_socket(s, server_hostname=host) as t:
            not_after = t.getpeercert()["notAfter"]
    except (ssl.SSLError, OSError, KeyError) as e:
        return None, "tls check failed: %s" % e
    exp = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.timezone.utc)
    return (exp - datetime.datetime.now(datetime.timezone.utc)).days, exp.date().isoformat()


def links_of(base, body):
    out, seen = [], set()
    for m in re.finditer(r'<a\s[^>]*href=["\']([^"\'#?]+)', body, re.I):
        u = urllib.parse.urljoin(base, html.unescape(m.group(1)))
        if urllib.parse.urlsplit(u).netloc == urllib.parse.urlsplit(base).netloc and u not in seen:
            seen.add(u); out.append(u)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("config")
    ap.add_argument("--report")
    args = ap.parse_args()
    try:
        cfg = json.load(io.open(args.config, encoding="utf-8"))
        pages = cfg["pages"]
        assert isinstance(pages, list) and pages
    except (OSError, ValueError, KeyError, AssertionError) as e:
        print("config error: %s" % e, file=sys.stderr)
        return 2
    timeout = float(cfg.get("timeout", 8))
    max_links = int(cfg.get("max_links", 100))
    min_days = int(cfg.get("min_cert_days", 14))

    rows, hosts_done, checked_links = [], {}, 0
    for p in pages:
        url, expect = p.get("url", ""), p.get("expect", "")
        if not url.startswith(("http://", "https://")):
            print("config error: url must be absolute: %r" % url, file=sys.stderr)
            return 2
        status, final, body, err = fetch(url, timeout)
        ok = status == 200 and not err
        rows.append(("page 200", url, ok, err or ("%s → %s" % (status, final) if final != url else str(status))))
        if ok and expect:
            has = expect in body
            rows.append(("page contains %r" % expect, url, has, "found" if has else "not found in first 400 KB"))
        parts = urllib.parse.urlsplit(url)
        if parts.scheme == "https" and parts.hostname not in hosts_done:
            days, note = cert_days(parts.hostname, parts.port or 443, timeout)
            hosts_done[parts.hostname] = True
            rows.append(("certificate ≥ %d days" % min_days, parts.hostname, days is not None and days >= min_days,
                         ("%d days, expires %s" % (days, note)) if days is not None else note))
        elif parts.scheme == "http" and parts.hostname not in hosts_done:
            hosts_done[parts.hostname] = True
            rows.append(("certificate", parts.hostname, True, "skipped (http)"))
        if ok:
            for link in links_of(final, body):
                if checked_links >= max_links:
                    rows.append(("links", url, True, "link budget of %d reached; remaining links not checked" % max_links))
                    break
                checked_links += 1
                st, fin, _, e2 = fetch(link, timeout, "HEAD")
                if st in (405, 501):
                    st, fin, _, e2 = fetch(link, timeout, "GET")
                good = st is not None and st < 400
                rows.append(("link resolves", link, good, e2 or ("%s%s" % (st, (" → " + fin) if fin != link else ""))))

    failed = [r for r in rows if not r[2]]
    lines = ["# Weekly check — %s" % time.strftime("%Y-%m-%d %H:%M"), "",
             "Checks: %d · passed: %d · failed: %d" % (len(rows), len(rows) - len(failed), len(failed)), "",
             "| Check | Subject | Result | Evidence |", "|---|---|---|---|"]
    for name, subj, ok, ev in rows:
        lines.append("| %s | %s | %s | %s |" % (name, subj, "PASS" if ok else "FAIL", ev))
    lines += ["", "## Not checked by this script", "",
              "- Forms deliver (send a marked submission; look in the inbox)",
              "- Backups restore (restore one and open it)",
              "- Dependencies and platform updates (read the admin, then staging first)",
              "- Configuration drift (compare with the recorded baseline)", ""]
    text = "\n".join(lines) + "\n"
    print(text)
    if args.report:
        io.open(args.report, "w", encoding="utf-8").write(text)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
